#!/usr/bin/env python3
"""
Hybrid Customer Support Agent
Uses Elastic AgenticBuilder for context and tool calling
Uses Strands Agents SDK for orchestration and agent framework
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import boto3

# Strands framework imports
from strands import Agent, Tool, MCPClient, ConversationMemory

load_dotenv()

logger = logging.getLogger(__name__)


class AgenticBuilderContext:
    """
    Elastic AgenticBuilder - Context Management Layer
    Stores conversation history and session data in Elasticsearch
    """

    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
        self.context_index = "agenticbuilder-context"
        self.tools_index = "agenticbuilder-tools"
        self.executions_index = "agenticbuilder-executions"

        self._setup_indices()

    def _setup_indices(self):
        """Create AgenticBuilder indices"""

        if not self.es.indices.exists(index=self.context_index):
            self.es.indices.create(
                index=self.context_index,
                body={
                    "mappings": {
                        "properties": {
                            "session_id": {"type": "keyword"},
                            "agent_id": {"type": "keyword"},
                            "customer_id": {"type": "keyword"},
                            "context_data": {"type": "object"},
                            "conversation_history": {
                                "type": "nested",
                                "properties": {
                                    "role": {"type": "keyword"},
                                    "content": {"type": "text"},
                                    "timestamp": {"type": "date"},
                                    "tool_calls": {"type": "object"}
                                }
                            },
                            "preferences": {"type": "object"},
                            "metadata": {"type": "object"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"}
                        }
                    }
                }
            )

        if not self.es.indices.exists(index=self.tools_index):
            self.es.indices.create(
                index=self.tools_index,
                body={
                    "mappings": {
                        "properties": {
                            "tool_id": {"type": "keyword"},
                            "name": {"type": "keyword"},
                            "description": {"type": "text"},
                            "usage_count": {"type": "long"},
                            "success_rate": {"type": "float"},
                            "avg_latency_ms": {"type": "float"},
                            "last_used": {"type": "date"}
                        }
                    }
                }
            )

        if not self.es.indices.exists(index=self.executions_index):
            self.es.indices.create(
                index=self.executions_index,
                body={
                    "mappings": {
                        "properties": {
                            "execution_id": {"type": "keyword"},
                            "session_id": {"type": "keyword"},
                            "tool_name": {"type": "keyword"},
                            "input": {"type": "object"},
                            "output": {"type": "object"},
                            "status": {"type": "keyword"},
                            "execution_time_ms": {"type": "float"},
                            "timestamp": {"type": "date"}
                        }
                    }
                }
            )

        logger.info("AgenticBuilder indices ready")

    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session context"""
        try:
            response = self.es.search(
                index=self.context_index,
                body={
                    "query": {"term": {"session_id": session_id}},
                    "sort": [{"updated_at": {"order": "desc"}}],
                    "size": 1
                }
            )

            if response["hits"]["total"]["value"] > 0:
                return response["hits"]["hits"][0]["_source"]
            return None

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return None

    def store_context(
        self,
        session_id: str,
        agent_id: str,
        customer_id: str,
        context_data: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        preferences: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Store or update session context"""
        try:
            context_doc = {
                "session_id": session_id,
                "agent_id": agent_id,
                "customer_id": customer_id,
                "context_data": context_data,
                "conversation_history": conversation_history,
                "preferences": preferences or {},
                "metadata": metadata or {},
                "updated_at": datetime.utcnow().isoformat()
            }

            # Check if context exists
            existing = self.get_context(session_id)
            if existing:
                context_doc["created_at"] = existing.get("created_at")
            else:
                context_doc["created_at"] = datetime.utcnow().isoformat()

            self.es.index(
                index=self.context_index,
                document=context_doc
            )

            return True

        except Exception as e:
            logger.error(f"Error storing context: {e}")
            return False

    def log_tool_execution(
        self,
        session_id: str,
        tool_name: str,
        input_params: Dict[str, Any],
        output_result: Dict[str, Any],
        status: str,
        execution_time_ms: float
    ):
        """Log tool execution for analytics"""
        try:
            exec_doc = {
                "execution_id": f"exec_{int(time.time() * 1000)}",
                "session_id": session_id,
                "tool_name": tool_name,
                "input": input_params,
                "output": output_result,
                "status": status,
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.utcnow().isoformat()
            }

            self.es.index(
                index=self.executions_index,
                document=exec_doc
            )

            # Update tool statistics
            self._update_tool_stats(tool_name, status, execution_time_ms)

        except Exception as e:
            logger.error(f"Error logging execution: {e}")

    def _update_tool_stats(self, tool_name: str, status: str, latency_ms: float):
        """Update tool usage statistics"""
        try:
            self.es.update(
                index=self.tools_index,
                id=tool_name,
                body={
                    "script": {
                        "source": """
                            if (ctx._source.containsKey('usage_count')) {
                                ctx._source.usage_count += 1;
                            } else {
                                ctx._source.usage_count = 1;
                                ctx._source.success_rate = 1.0;
                                ctx._source.avg_latency_ms = 0.0;
                            }

                            double success_val = params.status == 'success' ? 1.0 : 0.0;
                            ctx._source.success_rate =
                                (ctx._source.success_rate * (ctx._source.usage_count - 1) + success_val) /
                                ctx._source.usage_count;

                            ctx._source.avg_latency_ms =
                                (ctx._source.avg_latency_ms * (ctx._source.usage_count - 1) + params.latency) /
                                ctx._source.usage_count;

                            ctx._source.last_used = params.timestamp;
                        """,
                        "params": {
                            "status": status,
                            "latency": latency_ms,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    },
                    "upsert": {
                        "tool_id": tool_name,
                        "name": tool_name,
                        "description": "",
                        "usage_count": 1,
                        "success_rate": 1.0 if status == "success" else 0.0,
                        "avg_latency_ms": latency_ms,
                        "last_used": datetime.utcnow().isoformat()
                    }
                },
                retry_on_conflict=3
            )

        except Exception as e:
            logger.error(f"Error updating tool stats: {e}")


class HybridCustomerSupportAgent(Agent):
    """
    Hybrid Customer Support Agent

    Architecture:
    - Strands Agent SDK: Orchestration, tool execution, routing
    - Elastic AgenticBuilder: Context management, analytics, persistence
    - MCP Client: Tool gateway communication
    - Elastic Search: Knowledge base, orders, products
    """

    def __init__(
        self,
        name: str = "CustomerSupportAgent",
        session_id: str = None,
        customer_id: str = None
    ):
        # Load configuration
        self.es_url = os.getenv("ES_URL")
        self.es_api_key = os.getenv("ES_API_KEY")
        self.mcp_gateway_url = os.getenv("AGENTCORE_GATEWAY_URL")

        # Initialize Elasticsearch
        self.es = Elasticsearch(
            self.es_url,
            api_key=self.es_api_key,
            verify_certs=True
        )

        # Initialize AgenticBuilder for context management
        self.context_manager = AgenticBuilderContext(self.es)

        # Session management
        self.session_id = session_id or f"session_{int(time.time())}"
        self.customer_id = customer_id or "anonymous"

        # Initialize Bedrock for Claude
        self.bedrock = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

        # Initialize MCP Client (Strands SDK)
        self.mcp_client = MCPClient(
            gateway_url=self.mcp_gateway_url,
            token_provider=self._get_auth_token
        ) if self.mcp_gateway_url else None

        # Load or create context from AgenticBuilder
        self.context = self._load_context()

        # Initialize Strands Agent with tools
        super().__init__(
            name=name,
            tools=self._register_tools(),
            memory=ConversationMemory(
                namespace=f"customer-support-{self.session_id}",
                max_turns=50
            )
        )

        logger.info(f"Hybrid Customer Support Agent initialized")
        logger.info(f"Session: {self.session_id}, Customer: {self.customer_id}")

    def _load_context(self) -> Dict[str, Any]:
        """Load context from AgenticBuilder"""
        context = self.context_manager.get_context(self.session_id)

        if not context:
            # Create new context
            context = {
                "customer_id": self.customer_id,
                "context_data": {
                    "current_order_id": None,
                    "recent_searches": [],
                    "last_interaction": None
                },
                "conversation_history": [],
                "preferences": {
                    "language": "en",
                    "notification_channel": "email"
                }
            }

            self.context_manager.store_context(
                session_id=self.session_id,
                agent_id="customer-support",
                customer_id=self.customer_id,
                context_data=context["context_data"],
                conversation_history=[],
                preferences=context["preferences"]
            )

        return context

    def _get_auth_token(self) -> str:
        """Get OAuth2 token for MCP gateway"""
        # In production, get token from Cognito
        # For now, return placeholder
        return os.getenv("MCP_AUTH_TOKEN", "placeholder-token")

    def _register_tools(self) -> List[Tool]:
        """Register tools using Strands Tool interface"""

        return [
            Tool(
                name="hybrid_search_kb",
                description="Search knowledge base using hybrid search (BM25 + ELSER)",
                function=self._tool_hybrid_search_kb,
                parameters={
                    "query": "string",
                    "top_k": "integer (default: 5)"
                }
            ),
            Tool(
                name="get_order_status",
                description="Get order status and tracking information",
                function=self._tool_get_order_status,
                parameters={
                    "order_id": "string"
                }
            ),
            Tool(
                name="search_products",
                description="Search product catalog with semantic search",
                function=self._tool_search_products,
                parameters={
                    "query": "string",
                    "category": "string (optional)"
                }
            ),
            Tool(
                name="check_inventory",
                description="Check product inventory and availability",
                function=self._tool_check_inventory,
                parameters={
                    "product_id": "string"
                }
            ),
            Tool(
                name="elastic_rerank_results",
                description="Rerank results using Elastic Learning to Rank",
                function=self._tool_elastic_rerank,
                parameters={
                    "query": "string",
                    "document_ids": "array of strings"
                }
            ),
            Tool(
                name="create_support_ticket",
                description="Create support ticket for human agent",
                function=self._tool_create_ticket,
                parameters={
                    "issue_type": "string",
                    "description": "string",
                    "priority": "string (low|medium|high|urgent)"
                }
            ),
            Tool(
                name="update_customer_preferences",
                description="Update customer preferences in context",
                function=self._tool_update_preferences,
                parameters={
                    "preferences": "object"
                }
            ),
            Tool(
                name="send_notification",
                description="Send notification via email or SMS",
                function=self._tool_send_notification,
                parameters={
                    "channel": "string (email|sms)",
                    "message": "string"
                }
            )
        ]

    def _tool_hybrid_search_kb(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Hybrid search using BM25 + ELSER"""
        start_time = time.time()

        try:
            response = self.es.search(
                index="customer-kb",
                body={
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "match": {
                                        "content": {
                                            "query": query,
                                            "boost": 1.0
                                        }
                                    }
                                },
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
                    "size": top_k
                }
            )

            results = [
                {
                    "id": hit["_id"],
                    "title": hit["_source"].get("title", ""),
                    "content": hit["_source"].get("content", ""),
                    "score": hit["_score"]
                }
                for hit in response["hits"]["hits"]
            ]

            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="hybrid_search_kb",
                input_params={"query": query, "top_k": top_k},
                output_result={"results_count": len(results)},
                status="success",
                execution_time_ms=execution_time
            )

            return {
                "success": True,
                "results": results,
                "total": response["hits"]["total"]["value"]
            }

        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="hybrid_search_kb",
                input_params={"query": query},
                output_result={},
                status="error",
                execution_time_ms=execution_time
            )

            return {"success": False, "error": str(e)}

    def _tool_get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status from Elasticsearch"""
        start_time = time.time()

        try:
            response = self.es.get(
                index="customer-orders",
                id=order_id
            )

            order_data = response["_source"]

            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="get_order_status",
                input_params={"order_id": order_id},
                output_result={"found": True},
                status="success",
                execution_time_ms=execution_time
            )

            return {
                "success": True,
                "order": order_data
            }

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="get_order_status",
                input_params={"order_id": order_id},
                output_result={},
                status="error",
                execution_time_ms=execution_time
            )

            return {"success": False, "error": str(e)}

    def _tool_search_products(self, query: str, category: str = None) -> Dict[str, Any]:
        """Search products with ELSER semantic search"""
        start_time = time.time()

        try:
            search_query = {
                "text_expansion": {
                    "description_embedding": {
                        "model_id": ".elser_model_2",
                        "model_text": query
                    }
                }
            }

            if category:
                search_query = {
                    "bool": {
                        "must": [search_query],
                        "filter": {"term": {"category": category}}
                    }
                }

            response = self.es.search(
                index="customer-products",
                body={
                    "query": search_query,
                    "size": 10
                }
            )

            products = [
                {
                    "id": hit["_id"],
                    "name": hit["_source"].get("name"),
                    "description": hit["_source"].get("description"),
                    "price": hit["_source"].get("price"),
                    "in_stock": hit["_source"].get("in_stock")
                }
                for hit in response["hits"]["hits"]
            ]

            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="search_products",
                input_params={"query": query, "category": category},
                output_result={"count": len(products)},
                status="success",
                execution_time_ms=execution_time
            )

            return {"success": True, "products": products}

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="search_products",
                input_params={"query": query},
                output_result={},
                status="error",
                execution_time_ms=execution_time
            )

            return {"success": False, "error": str(e)}

    def _tool_check_inventory(self, product_id: str) -> Dict[str, Any]:
        """Check inventory for a product"""
        start_time = time.time()

        try:
            response = self.es.get(
                index="customer-products",
                id=product_id
            )

            product = response["_source"]

            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="check_inventory",
                input_params={"product_id": product_id},
                output_result={"in_stock": product.get("in_stock")},
                status="success",
                execution_time_ms=execution_time
            )

            return {
                "success": True,
                "product_id": product_id,
                "in_stock": product.get("in_stock", False),
                "quantity": product.get("quantity", 0),
                "warehouse": product.get("warehouse_location")
            }

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="check_inventory",
                input_params={"product_id": product_id},
                output_result={},
                status="error",
                execution_time_ms=execution_time
            )

            return {"success": False, "error": str(e)}

    def _tool_elastic_rerank(self, query: str, document_ids: List[str]) -> Dict[str, Any]:
        """Rerank using Elastic LTR"""
        start_time = time.time()

        try:
            response = self.es.search(
                index="customer-kb",
                body={
                    "query": {
                        "bool": {
                            "filter": {"terms": {"article_id": document_ids}}
                        }
                    },
                    "rescore": {
                        "window_size": 50,
                        "query": {
                            "rescore_query": {
                                "sltr": {
                                    "params": {"query": query},
                                    "model": "customer_support_reranker"
                                }
                            }
                        }
                    }
                }
            )

            reranked = [
                {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "content": hit["_source"].get("content")
                }
                for hit in response["hits"]["hits"]
            ]

            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="elastic_rerank_results",
                input_params={"query": query, "doc_count": len(document_ids)},
                output_result={"reranked_count": len(reranked)},
                status="success",
                execution_time_ms=execution_time
            )

            return {"success": True, "reranked_results": reranked}

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="elastic_rerank_results",
                input_params={"query": query},
                output_result={},
                status="error",
                execution_time_ms=execution_time
            )

            return {"success": False, "error": str(e)}

    def _tool_create_ticket(
        self,
        issue_type: str,
        description: str,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """Create support ticket"""
        start_time = time.time()

        try:
            ticket = {
                "customer_id": self.customer_id,
                "session_id": self.session_id,
                "issue_type": issue_type,
                "description": description,
                "priority": priority,
                "status": "open",
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.es.index(
                index="customer-tickets",
                document=ticket
            )

            ticket_id = response["_id"]

            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="create_support_ticket",
                input_params={"issue_type": issue_type, "priority": priority},
                output_result={"ticket_id": ticket_id},
                status="success",
                execution_time_ms=execution_time
            )

            return {
                "success": True,
                "ticket_id": ticket_id,
                "message": "Support ticket created successfully"
            }

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="create_support_ticket",
                input_params={"issue_type": issue_type},
                output_result={},
                status="error",
                execution_time_ms=execution_time
            )

            return {"success": False, "error": str(e)}

    def _tool_update_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer preferences in AgenticBuilder context"""
        try:
            self.context["preferences"].update(preferences)

            self.context_manager.store_context(
                session_id=self.session_id,
                agent_id="customer-support",
                customer_id=self.customer_id,
                context_data=self.context["context_data"],
                conversation_history=self.context["conversation_history"],
                preferences=self.context["preferences"]
            )

            return {
                "success": True,
                "message": "Preferences updated",
                "preferences": self.context["preferences"]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_send_notification(self, channel: str, message: str) -> Dict[str, Any]:
        """Send notification"""
        start_time = time.time()

        try:
            # Store notification in Elasticsearch
            notification = {
                "customer_id": self.customer_id,
                "channel": channel,
                "message": message,
                "status": "sent",
                "timestamp": datetime.utcnow().isoformat()
            }

            self.es.index(
                index="customer-notifications",
                document=notification
            )

            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="send_notification",
                input_params={"channel": channel},
                output_result={"status": "sent"},
                status="success",
                execution_time_ms=execution_time
            )

            return {
                "success": True,
                "message": f"Notification sent via {channel}"
            }

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            self.context_manager.log_tool_execution(
                session_id=self.session_id,
                tool_name="send_notification",
                input_params={"channel": channel},
                output_result={},
                status="error",
                execution_time_ms=execution_time
            )

            return {"success": False, "error": str(e)}

    def handle_customer_query(self, query: str) -> str:
        """
        Main entry point for customer queries

        Flow:
        1. Load context from AgenticBuilder
        2. Use Strands Agent to process query
        3. Agent selects and executes tools
        4. Store updated context in AgenticBuilder
        5. Return response
        """

        # Add user message to context
        user_message = {
            "role": "user",
            "content": query,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.context["conversation_history"].append(user_message)

        # Use Strands Agent to process (this calls the parent Agent.run())
        response = self.run(query)

        # Add assistant response to context
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.context["conversation_history"].append(assistant_message)

        # Update context in AgenticBuilder
        self.context_manager.store_context(
            session_id=self.session_id,
            agent_id="customer-support",
            customer_id=self.customer_id,
            context_data=self.context["context_data"],
            conversation_history=self.context["conversation_history"],
            preferences=self.context["preferences"]
        )

        return response

    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics from AgenticBuilder"""
        try:
            # Get tool usage statistics
            tool_stats = self.es.search(
                index="agenticbuilder-tools",
                body={
                    "query": {"match_all": {}},
                    "size": 100
                }
            )

            # Get session statistics
            session_stats = self.es.search(
                index="agenticbuilder-executions",
                body={
                    "query": {"term": {"session_id": self.session_id}},
                    "aggs": {
                        "total_executions": {"value_count": {"field": "execution_id"}},
                        "avg_latency": {"avg": {"field": "execution_time_ms"}},
                        "success_rate": {
                            "terms": {"field": "status"}
                        }
                    }
                }
            )

            return {
                "session_id": self.session_id,
                "tool_statistics": [
                    {
                        "name": hit["_source"]["name"],
                        "usage_count": hit["_source"]["usage_count"],
                        "success_rate": hit["_source"]["success_rate"],
                        "avg_latency_ms": hit["_source"]["avg_latency_ms"]
                    }
                    for hit in tool_stats["hits"]["hits"]
                ],
                "session_statistics": session_stats.get("aggregations", {})
            }

        except Exception as e:
            logger.error(f"Error fetching analytics: {e}")
            return {}


def main():
    """Test the hybrid agent"""
    logging.basicConfig(level=logging.INFO)

    # Create agent
    agent = HybridCustomerSupportAgent(
        name="CustomerSupport",
        session_id="test_session_001",
        customer_id="customer_123"
    )

    # Test queries
    queries = [
        "What is your return policy?",
        "Check status of order ORD-12345",
        "Show me wireless headphones under $100",
        "Is product PROD-789 in stock?"
    ]

    for query in queries:
        print(f"\nUser: {query}")
        response = agent.handle_customer_query(query)
        print(f"Agent: {response}")
        print("-" * 60)

    # Show analytics
    print("\nAnalytics:")
    analytics = agent.get_analytics()
    print(json.dumps(analytics, indent=2))


if __name__ == "__main__":
    main()
