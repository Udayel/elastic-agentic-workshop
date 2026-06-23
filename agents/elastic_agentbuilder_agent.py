#!/usr/bin/env python3
"""
Customer Support Agent using Elastic AgentBuilder
Uses AgentBuilder API to define tools and agent configuration
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ElasticAgentBuilder:
    """
    Elastic AgentBuilder Client
    Creates and manages agents using Elastic's native agent framework
    """

    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
        self.agents_index = "agentbuilder-agents"
        self.tools_index = "agentbuilder-tools"
        self.sessions_index = "agentbuilder-sessions"

        self._setup_indices()

    def _setup_indices(self):
        """Create AgentBuilder indices"""

        # Agents index
        if not self.es.indices.exists(index=self.agents_index):
            self.es.indices.create(
                index=self.agents_index,
                body={
                    "mappings": {
                        "properties": {
                            "agent_id": {"type": "keyword"},
                            "name": {"type": "text"},
                            "description": {"type": "text"},
                            "system_prompt": {"type": "text"},
                            "tools": {"type": "keyword"},
                            "model": {"type": "keyword"},
                            "config": {"type": "object"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"}
                        }
                    }
                }
            )

        # Tools index
        if not self.es.indices.exists(index=self.tools_index):
            self.es.indices.create(
                index=self.tools_index,
                body={
                    "mappings": {
                        "properties": {
                            "tool_id": {"type": "keyword"},
                            "name": {"type": "keyword"},
                            "description": {"type": "text"},
                            "input_schema": {"type": "object"},
                            "elasticsearch_query_template": {"type": "object"},
                            "index_pattern": {"type": "keyword"},
                            "search_type": {
                                "type": "keyword"  # "bm25", "elser", "knn", "hybrid"
                            },
                            "enabled": {"type": "boolean"}
                        }
                    }
                }
            )

        logger.info("AgentBuilder indices initialized")

    def register_tool(
        self,
        tool_id: str,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        elasticsearch_query_template: Dict[str, Any],
        index_pattern: str,
        search_type: str = "bm25"
    ) -> Dict[str, Any]:
        """Register a tool in AgentBuilder"""

        tool_doc = {
            "tool_id": tool_id,
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "elasticsearch_query_template": elasticsearch_query_template,
            "index_pattern": index_pattern,
            "search_type": search_type,
            "enabled": True
        }

        self.es.index(
            index=self.tools_index,
            id=tool_id,
            document=tool_doc
        )

        logger.info(f"Registered tool: {tool_id}")
        return {"success": True, "tool_id": tool_id}

    def register_agent(
        self,
        agent_id: str,
        name: str,
        description: str,
        system_prompt: str,
        tools: List[str],
        model: str = "gpt-4",
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Register an agent in AgentBuilder"""

        agent_doc = {
            "agent_id": agent_id,
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            "tools": tools,
            "model": model,
            "config": config or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        self.es.index(
            index=self.agents_index,
            id=agent_id,
            document=agent_doc
        )

        logger.info(f"Registered agent: {agent_id}")
        return {"success": True, "agent_id": agent_id}

    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool definition"""
        try:
            response = self.es.get(index=self.tools_index, id=tool_id)
            return response["_source"]
        except Exception as e:
            logger.error(f"Tool not found: {tool_id}")
            return None

    def execute_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool using its Elasticsearch query template"""

        tool = self.get_tool(tool_id)
        if not tool:
            return {"success": False, "error": f"Tool {tool_id} not found"}

        try:
            # Build query from template and parameters
            query_template = tool["elasticsearch_query_template"]
            index_pattern = tool["index_pattern"]

            # Replace template variables with actual parameters
            query = self._build_query(query_template, parameters)

            # Execute search
            response = self.es.search(
                index=index_pattern,
                body=query
            )

            # Format results
            results = self._format_results(response, tool["search_type"])

            return {
                "success": True,
                "tool_id": tool_id,
                "results": results,
                "total": response["hits"]["total"]["value"]
            }

        except Exception as e:
            logger.error(f"Error executing tool {tool_id}: {e}")
            return {"success": False, "error": str(e)}

    def _build_query(
        self,
        template: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Elasticsearch query from template and parameters"""

        # Simple template variable replacement
        query_str = json.dumps(template)

        for key, value in parameters.items():
            placeholder = f"{{{{ {key} }}}}"
            query_str = query_str.replace(placeholder, json.dumps(value))

        return json.loads(query_str)

    def _format_results(
        self,
        response: Dict[str, Any],
        search_type: str
    ) -> List[Dict[str, Any]]:
        """Format Elasticsearch results"""

        results = []
        for hit in response["hits"]["hits"]:
            result = {
                "id": hit["_id"],
                "score": hit["_score"],
                "source": hit["_source"]
            }
            results.append(result)

        return results


class CustomerSupportAgentWithBuilder:
    """
    Customer Support Agent using Elastic AgentBuilder
    """

    def __init__(
        self,
        agent_id: str = "customer-support-agent",
        session_id: str = None,
        customer_id: str = None
    ):
        # Initialize Elasticsearch
        self.es_url = os.getenv("ES_URL")
        self.es_api_key = os.getenv("ES_API_KEY")

        self.es = Elasticsearch(
            self.es_url,
            api_key=self.es_api_key,
            verify_certs=True
        )

        # Initialize AgentBuilder
        self.builder = ElasticAgentBuilder(self.es)

        self.agent_id = agent_id
        self.session_id = session_id or f"session_{int(time.time())}"
        self.customer_id = customer_id or "anonymous"

        # Register agent and tools
        self._register_tools()
        self._register_agent()

        logger.info(f"Customer Support Agent initialized with AgentBuilder")

    def _register_tools(self):
        """Register all customer support tools in AgentBuilder"""

        # Tool 1: Hybrid Search KB
        self.builder.register_tool(
            tool_id="hybrid_search_kb",
            name="hybrid_search_kb",
            description="Search knowledge base using hybrid search (BM25 + ELSER semantic search)",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            },
            elasticsearch_query_template={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match": {
                                    "content": {
                                        "query": "{{ query }}",
                                        "boost": 1.0
                                    }
                                }
                            },
                            {
                                "text_expansion": {
                                    "content_embedding": {
                                        "model_id": ".elser_model_2",
                                        "model_text": "{{ query }}",
                                        "boost": 2.0
                                    }
                                }
                            }
                        ]
                    }
                },
                "size": "{{ top_k }}"
            },
            index_pattern="customer-kb",
            search_type="hybrid"
        )

        # Tool 2: Get Order Status
        self.builder.register_tool(
            tool_id="get_order_status",
            name="get_order_status",
            description="Get order status and tracking information",
            input_schema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to lookup"
                    }
                },
                "required": ["order_id"]
            },
            elasticsearch_query_template={
                "query": {
                    "term": {
                        "order_id": "{{ order_id }}"
                    }
                }
            },
            index_pattern="customer-orders",
            search_type="bm25"
        )

        # Tool 3: Search Products (ELSER semantic)
        self.builder.register_tool(
            tool_id="search_products",
            name="search_products",
            description="Search product catalog using ELSER semantic search",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Product search query"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter"
                    }
                },
                "required": ["query"]
            },
            elasticsearch_query_template={
                "query": {
                    "text_expansion": {
                        "description_embedding": {
                            "model_id": ".elser_model_2",
                            "model_text": "{{ query }}"
                        }
                    }
                },
                "size": 10
            },
            index_pattern="customer-products",
            search_type="elser"
        )

        # Tool 4: Check Inventory
        self.builder.register_tool(
            tool_id="check_inventory",
            name="check_inventory",
            description="Check product inventory and availability",
            input_schema={
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product ID to check"
                    }
                },
                "required": ["product_id"]
            },
            elasticsearch_query_template={
                "query": {
                    "term": {
                        "product_id": "{{ product_id }}"
                    }
                }
            },
            index_pattern="customer-products",
            search_type="bm25"
        )

        logger.info("Registered 4 tools in AgentBuilder")

    def _register_agent(self):
        """Register the customer support agent in AgentBuilder"""

        system_prompt = """You are a helpful customer support AI assistant.

Your capabilities:
- Search knowledge base for policies and FAQs
- Check order status and tracking
- Search products with semantic understanding
- Check inventory availability

Guidelines:
- Be polite and professional
- Use hybrid search for best results
- Provide accurate information from Elasticsearch
- Create support tickets when needed

Available tools: hybrid_search_kb, get_order_status, search_products, check_inventory"""

        self.builder.register_agent(
            agent_id=self.agent_id,
            name="Customer Support Agent",
            description="AI-powered customer support using Elastic AgentBuilder",
            system_prompt=system_prompt,
            tools=[
                "hybrid_search_kb",
                "get_order_status",
                "search_products",
                "check_inventory"
            ],
            model="claude-3.5-sonnet",
            config={
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )

        logger.info("Registered agent in AgentBuilder")

    def handle_query(self, query: str) -> str:
        """Handle customer query using AgentBuilder tools"""

        # Simple intent detection (in production, use LLM for this)
        if "return" in query.lower() or "policy" in query.lower():
            tool_id = "hybrid_search_kb"
            parameters = {"query": query, "top_k": 3}

        elif "order" in query.lower() and "ORD-" in query:
            tool_id = "get_order_status"
            # Extract order ID
            import re
            match = re.search(r'ORD-\d+', query)
            order_id = match.group(0) if match else "ORD-12345"
            parameters = {"order_id": order_id}

        elif "product" in query.lower() or "headphone" in query.lower():
            tool_id = "search_products"
            parameters = {"query": query}

        elif "stock" in query.lower() and "PROD-" in query:
            tool_id = "check_inventory"
            import re
            match = re.search(r'PROD-\d+', query)
            product_id = match.group(0) if match else "PROD-001"
            parameters = {"product_id": product_id}

        else:
            # Default to knowledge base search
            tool_id = "hybrid_search_kb"
            parameters = {"query": query, "top_k": 5}

        # Execute tool via AgentBuilder
        result = self.builder.execute_tool(tool_id, parameters)

        if result["success"]:
            # Format response
            response = self._format_response(result)
            return response
        else:
            return f"Sorry, I encountered an error: {result.get('error', 'Unknown error')}"

    def _format_response(self, result: Dict[str, Any]) -> str:
        """Format tool execution result as natural language response"""

        if not result.get("results"):
            return "I couldn't find any relevant information."

        tool_id = result["tool_id"]
        results = result["results"]

        if tool_id == "hybrid_search_kb":
            if results:
                top_result = results[0]["source"]
                return f"{top_result.get('title', 'Information')}: {top_result.get('content', 'No content available')}"

        elif tool_id == "get_order_status":
            if results:
                order = results[0]["source"]
                return f"Order {order.get('order_id')} is {order.get('status')}. Tracking: {order.get('tracking_number', 'N/A')}"

        elif tool_id == "search_products":
            if results:
                products = "\n".join([
                    f"- {p['source'].get('name')} - ${p['source'].get('price')} ({'In stock' if p['source'].get('in_stock') else 'Out of stock'})"
                    for p in results[:3]
                ])
                return f"I found these products:\n{products}"

        elif tool_id == "check_inventory":
            if results:
                product = results[0]["source"]
                status = "in stock" if product.get("in_stock") else "out of stock"
                qty = product.get("quantity", 0)
                return f"{product.get('name')} is {status}. Available quantity: {qty}"

        return "I found some information but couldn't format it properly."


def main():
    """Test the AgentBuilder implementation"""
    logging.basicConfig(level=logging.INFO)

    # Initialize agent
    agent = CustomerSupportAgentWithBuilder()

    # Test queries
    queries = [
        "What is your return policy?",
        "Check status of order ORD-12345",
        "Show me wireless headphones",
        "Is product PROD-001 in stock?"
    ]

    for query in queries:
        print(f"\nUser: {query}")
        response = agent.handle_query(query)
        print(f"Agent: {response}")
        print("-" * 60)


if __name__ == "__main__":
    main()
