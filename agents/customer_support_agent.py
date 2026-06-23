#!/usr/bin/env python3
"""
Customer Support Agent - Built with Strands Framework
Elasticsearch-powered search and retrieval
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from strands import Agent, MCPClient, Tool
from strands.memory import ConversationMemory
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class CustomerSupportAgent(Agent):
    """
    Customer Support AI Agent using Strands Framework

    Capabilities:
    - Answer customer questions using knowledge base
    - Check order status
    - Search product information
    - Create support tickets
    - Escalate to human agents when needed
    """

    def __init__(
        self,
        name: str = "CustomerSupportAgent",
        mcp_gateway_url: str = None,
        elasticsearch_url: str = None,
        elasticsearch_api_key: str = None
    ):
        # Initialize Elasticsearch client
        self.es_url = elasticsearch_url or os.getenv("ES_URL")
        self.es_api_key = elasticsearch_api_key or os.getenv("ES_API_KEY")

        self.es = Elasticsearch(
            self.es_url,
            api_key=self.es_api_key,
            verify_certs=True
        )

        # Initialize MCP client for AgentCore Gateway
        self.mcp_gateway_url = mcp_gateway_url or os.getenv("AGENTCORE_GATEWAY_URL")
        self.mcp_client = MCPClient(
            gateway_url=self.mcp_gateway_url,
            token_provider=self._get_auth_token
        )

        # Initialize Strands Agent
        super().__init__(
            name=name,
            description="Customer support agent that helps customers with orders, products, and issues",
            tools=self._register_tools(),
            memory=ConversationMemory(
                namespace="customer-support",
                max_turns=50
            )
        )

        logger.info(f"Initialized {name} with Elasticsearch and MCP gateway")

    def _get_auth_token(self) -> str:
        """Get OAuth2 token for AgentCore Gateway"""
        # TODO: Implement Cognito token retrieval
        # For now, return environment variable
        return os.getenv("AGENTCORE_AUTH_TOKEN", "")

    def _register_tools(self) -> List[Tool]:
        """Register all tools available to the agent"""
        return [
            Tool(
                name="hybrid_search_kb",
                description="Search knowledge base using hybrid search (BM25 + ELSER semantic)",
                function=self.hybrid_search_kb,
                parameters={
                    "query": {
                        "type": "string",
                        "description": "Customer question or issue description"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                }
            ),
            Tool(
                name="get_order_status",
                description="Get current status of a customer order",
                function=self.get_order_status,
                parameters={
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to lookup"
                    }
                }
            ),
            Tool(
                name="search_products",
                description="Search product catalog for product information",
                function=self.search_products,
                parameters={
                    "query": {
                        "type": "string",
                        "description": "Product name or description"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters (category, price_range, etc.)"
                    }
                }
            ),
            Tool(
                name="check_inventory",
                description="Check real-time inventory for a product",
                function=self.check_inventory,
                parameters={
                    "product_id": {
                        "type": "string",
                        "description": "Product ID to check"
                    }
                }
            ),
            Tool(
                name="elastic_rerank_results",
                description="Rerank search results using Elastic Learning to Rank for maximum relevance",
                function=self.elastic_rerank_results,
                parameters={
                    "query": {
                        "type": "string",
                        "description": "Original query"
                    },
                    "document_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of document IDs to rerank"
                    }
                }
            ),
            Tool(
                name="create_support_ticket",
                description="Create a support ticket for issues requiring human agent attention",
                function=self.create_support_ticket,
                parameters={
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID"
                    },
                    "issue_type": {
                        "type": "string",
                        "description": "Type of issue (refund, technical, etc.)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level (low, medium, high, urgent)",
                        "default": "medium"
                    }
                }
            ),
            Tool(
                name="update_customer_record",
                description="Update customer interaction history",
                function=self.update_customer_record,
                parameters={
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID"
                    },
                    "interaction_data": {
                        "type": "object",
                        "description": "Interaction details to store"
                    }
                }
            ),
            Tool(
                name="send_notification",
                description="Send notification to customer (email/SMS)",
                function=self.send_notification,
                parameters={
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Notification channel (email or sms)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Notification message"
                    }
                }
            )
        ]

    def hybrid_search_kb(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Hybrid search combining BM25 + ELSER semantic search
        """
        logger.info(f"Hybrid search KB: {query}")

        try:
            response = self.es.search(
                index="customer-kb",
                body={
                    "query": {
                        "bool": {
                            "should": [
                                # BM25 full-text search
                                {
                                    "match": {
                                        "content": {
                                            "query": query,
                                            "boost": 1.0
                                        }
                                    }
                                },
                                # ELSER semantic search
                                {
                                    "text_expansion": {
                                        "content_embedding": {
                                            "model_id": ".elser_model_2",
                                            "model_text": query,
                                            "boost": 2.0
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "size": top_k,
                    "_source": ["article_id", "title", "content", "resolution_rate", "satisfaction_score"]
                }
            )

            hits = response["hits"]["hits"]

            return {
                "success": True,
                "total": response["hits"]["total"]["value"],
                "results": [
                    {
                        "id": hit["_id"],
                        "score": hit["_score"],
                        "title": hit["_source"]["title"],
                        "content": hit["_source"]["content"],
                        "resolution_rate": hit["_source"].get("resolution_rate", 0),
                        "satisfaction_score": hit["_source"].get("satisfaction_score", 0)
                    }
                    for hit in hits
                ]
            }

        except Exception as e:
            logger.error(f"Error in hybrid_search_kb: {e}")
            return {"success": False, "error": str(e)}

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status from Elasticsearch"""
        logger.info(f"Getting order status: {order_id}")

        try:
            response = self.es.get(
                index="customer-orders",
                id=order_id
            )

            if response["found"]:
                order = response["_source"]
                return {
                    "success": True,
                    "order_id": order_id,
                    "status": order["status"],
                    "tracking_number": order.get("tracking_number"),
                    "estimated_delivery": order.get("estimated_delivery"),
                    "items": order.get("items", []),
                    "total_amount": order.get("total_amount")
                }
            else:
                return {
                    "success": False,
                    "error": f"Order {order_id} not found"
                }

        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return {"success": False, "error": str(e)}

    def search_products(self, query: str, filters: Dict = None) -> Dict[str, Any]:
        """Search products using ELSER semantic search"""
        logger.info(f"Searching products: {query}")

        try:
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "text_expansion": {
                                    "description_embedding": {
                                        "model_id": ".elser_model_2",
                                        "model_text": query
                                    }
                                }
                            }
                        ]
                    }
                },
                "size": 10,
                "_source": ["product_id", "name", "description", "price", "stock_quantity", "rating"]
            }

            # Add filters if provided
            if filters:
                if "category" in filters:
                    search_body["query"]["bool"]["filter"] = [
                        {"term": {"category": filters["category"]}}
                    ]
                if "price_range" in filters:
                    search_body["query"]["bool"]["filter"] = search_body["query"]["bool"].get("filter", []) + [
                        {"range": {"price": filters["price_range"]}}
                    ]

            response = self.es.search(
                index="customer-products",
                body=search_body
            )

            return {
                "success": True,
                "total": response["hits"]["total"]["value"],
                "products": [
                    {
                        "product_id": hit["_source"]["product_id"],
                        "name": hit["_source"]["name"],
                        "description": hit["_source"]["description"],
                        "price": hit["_source"]["price"],
                        "in_stock": hit["_source"]["stock_quantity"] > 0,
                        "rating": hit["_source"].get("rating", 0)
                    }
                    for hit in response["hits"]["hits"]
                ]
            }

        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return {"success": False, "error": str(e)}

    def check_inventory(self, product_id: str) -> Dict[str, Any]:
        """Check product inventory"""
        logger.info(f"Checking inventory: {product_id}")

        try:
            response = self.es.get(
                index="customer-products",
                id=product_id,
                _source=["stock_quantity", "name", "price"]
            )

            if response["found"]:
                product = response["_source"]
                stock = product["stock_quantity"]

                return {
                    "success": True,
                    "product_id": product_id,
                    "name": product["name"],
                    "price": product["price"],
                    "stock_quantity": stock,
                    "in_stock": stock > 0,
                    "availability": "In Stock" if stock > 10 else "Low Stock" if stock > 0 else "Out of Stock"
                }
            else:
                return {
                    "success": False,
                    "error": f"Product {product_id} not found"
                }

        except Exception as e:
            logger.error(f"Error checking inventory: {e}")
            return {"success": False, "error": str(e)}

    def elastic_rerank_results(self, query: str, document_ids: List[str]) -> Dict[str, Any]:
        """Rerank results using Elastic Learning to Rank"""
        logger.info(f"Reranking {len(document_ids)} documents")

        try:
            response = self.es.search(
                index="customer-kb",
                body={
                    "query": {
                        "bool": {
                            "filter": {
                                "terms": {
                                    "article_id": document_ids
                                }
                            }
                        }
                    },
                    "rescore": {
                        "window_size": 50,
                        "query": {
                            "rescore_query": {
                                "sltr": {
                                    "params": {
                                        "query": query
                                    },
                                    "model": "customer_support_reranker"
                                }
                            }
                        }
                    },
                    "_source": ["article_id", "title", "content", "resolution_rate"]
                }
            )

            return {
                "success": True,
                "reranked_results": [
                    {
                        "id": hit["_source"]["article_id"],
                        "title": hit["_source"]["title"],
                        "content": hit["_source"]["content"],
                        "rerank_score": hit["_score"]
                    }
                    for hit in response["hits"]["hits"]
                ]
            }

        except Exception as e:
            logger.error(f"Error reranking: {e}")
            # Fall back to original order if LTR not configured
            return {
                "success": True,
                "reranked_results": [{"id": doc_id} for doc_id in document_ids],
                "note": "LTR reranking not available, returning original order"
            }

    def create_support_ticket(
        self,
        customer_id: str,
        issue_type: str,
        description: str,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """Create a support ticket in Elasticsearch"""
        logger.info(f"Creating support ticket for customer: {customer_id}")

        try:
            ticket_data = {
                "customer_id": customer_id,
                "issue_type": issue_type,
                "description": description,
                "priority": priority,
                "status": "open",
                "created_at": datetime.utcnow().isoformat(),
                "assigned_agent": None,
                "resolution_notes": None
            }

            response = self.es.index(
                index="customer-tickets",
                document=ticket_data
            )

            ticket_id = response["_id"]

            return {
                "success": True,
                "ticket_id": ticket_id,
                "status": "created",
                "message": f"Support ticket #{ticket_id} created. A human agent will contact you within 24 hours."
            }

        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return {"success": False, "error": str(e)}

    def update_customer_record(
        self,
        customer_id: str,
        interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update customer interaction history"""
        logger.info(f"Updating customer record: {customer_id}")

        try:
            interaction_record = {
                "customer_id": customer_id,
                "timestamp": datetime.utcnow().isoformat(),
                "channel": interaction_data.get("channel", "chat"),
                "issue_type": interaction_data.get("issue_type"),
                "resolution": interaction_data.get("resolution"),
                "satisfaction": interaction_data.get("satisfaction"),
                "agent_type": "ai"
            }

            response = self.es.index(
                index="customer-interactions",
                document=interaction_record
            )

            return {
                "success": True,
                "interaction_id": response["_id"]
            }

        except Exception as e:
            logger.error(f"Error updating customer record: {e}")
            return {"success": False, "error": str(e)}

    def send_notification(
        self,
        customer_id: str,
        channel: str,
        message: str
    ) -> Dict[str, Any]:
        """Send notification via Elastic AgenticBuilder"""
        logger.info(f"Sending {channel} notification to customer: {customer_id}")

        try:
            # Store notification in Elasticsearch
            # AgenticBuilder will process and send
            notification_data = {
                "customer_id": customer_id,
                "channel": channel,
                "message": message,
                "status": "queued",
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.es.index(
                index="customer-notifications",
                document=notification_data
            )

            return {
                "success": True,
                "notification_id": response["_id"],
                "status": "queued"
            }

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return {"success": False, "error": str(e)}

    async def handle_customer_query(self, query: str, customer_id: str = None) -> str:
        """
        Main entry point for handling customer queries
        Uses Strands Agent reasoning to autonomously:
        1. Understand the query
        2. Select appropriate tools
        3. Execute actions
        4. Generate response
        """
        logger.info(f"Handling customer query: {query}")

        # Strands Agent will autonomously reason and use tools
        response = await self.process(
            input_text=query,
            context={
                "customer_id": customer_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Update interaction history
        if customer_id:
            self.update_customer_record(
                customer_id=customer_id,
                interaction_data={
                    "query": query,
                    "response": response,
                    "channel": "chat"
                }
            )

        return response


def main():
    """Test the customer support agent"""
    agent = CustomerSupportAgent()

    # Test queries
    test_queries = [
        "Where is my order #12345?",
        "Do you have iPhone 15 Pro in stock?",
        "My laptop won't turn on, help!",
        "I want to return my purchase"
    ]

    print("="*60)
    print("Customer Support Agent - Strands Framework")
    print("="*60)
    print()

    for query in test_queries:
        print(f"Customer: {query}")
        response = agent.handle_customer_query(query, customer_id="test-customer-123")
        print(f"Agent: {response}")
        print()


if __name__ == "__main__":
    main()
