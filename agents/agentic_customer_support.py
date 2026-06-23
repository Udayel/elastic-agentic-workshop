#!/usr/bin/env python3
"""
Customer Support Agent - Built with Elastic AgenticBuilder
Uses AgenticBuilder for context management and tool calling
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import boto3

load_dotenv()

logger = logging.getLogger(__name__)


class AgenticBuilderClient:
    """
    Elastic AgenticBuilder Client
    Handles context management and tool orchestration
    """

    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
        self.agent_index = "agenticbuilder-agents"
        self.context_index = "agenticbuilder-context"
        self.tools_index = "agenticbuilder-tools"
        self.executions_index = "agenticbuilder-executions"

        # Ensure indices exist
        self._setup_indices()

    def _setup_indices(self):
        """Create AgenticBuilder indices if they don't exist"""

        # Agent definitions index
        if not self.es.indices.exists(index=self.agent_index):
            self.es.indices.create(
                index=self.agent_index,
                body={
                    "mappings": {
                        "properties": {
                            "agent_id": {"type": "keyword"},
                            "name": {"type": "text"},
                            "description": {"type": "text"},
                            "system_prompt": {"type": "text"},
                            "tools": {"type": "keyword"},
                            "model": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"}
                        }
                    }
                }
            )

        # Context storage index
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
                                    "timestamp": {"type": "date"}
                                }
                            },
                            "metadata": {"type": "object"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"},
                            "ttl": {"type": "date"}
                        }
                    }
                }
            )

        # Tools registry index
        if not self.es.indices.exists(index=self.tools_index):
            self.es.indices.create(
                index=self.tools_index,
                body={
                    "mappings": {
                        "properties": {
                            "tool_id": {"type": "keyword"},
                            "name": {"type": "keyword"},
                            "description": {"type": "text"},
                            "parameters": {"type": "object"},
                            "function_name": {"type": "keyword"},
                            "enabled": {"type": "boolean"},
                            "usage_count": {"type": "long"},
                            "success_rate": {"type": "float"},
                            "avg_latency_ms": {"type": "float"}
                        }
                    }
                }
            )

        # Tool executions log index
        if not self.es.indices.exists(index=self.executions_index):
            self.es.indices.create(
                index=self.executions_index,
                body={
                    "mappings": {
                        "properties": {
                            "execution_id": {"type": "keyword"},
                            "session_id": {"type": "keyword"},
                            "tool_id": {"type": "keyword"},
                            "tool_name": {"type": "keyword"},
                            "input_parameters": {"type": "object"},
                            "output_result": {"type": "object"},
                            "status": {"type": "keyword"},
                            "error_message": {"type": "text"},
                            "execution_time_ms": {"type": "float"},
                            "timestamp": {"type": "date"}
                        }
                    }
                }
            )

        logger.info("AgenticBuilder indices initialized")

    def register_agent(
        self,
        agent_id: str,
        name: str,
        description: str,
        system_prompt: str,
        tools: List[str],
        model: str = "claude-3.5-sonnet"
    ) -> Dict[str, Any]:
        """Register an agent in AgenticBuilder"""

        agent_doc = {
            "agent_id": agent_id,
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            "tools": tools,
            "model": model,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = self.es.index(
            index=self.agent_index,
            id=agent_id,
            document=agent_doc
        )

        return {"success": True, "agent_id": agent_id}

    def register_tool(
        self,
        tool_id: str,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function_name: str
    ) -> Dict[str, Any]:
        """Register a tool in AgenticBuilder"""

        tool_doc = {
            "tool_id": tool_id,
            "name": name,
            "description": description,
            "parameters": parameters,
            "function_name": function_name,
            "enabled": True,
            "usage_count": 0,
            "success_rate": 1.0,
            "avg_latency_ms": 0.0
        }

        response = self.es.index(
            index=self.tools_index,
            id=tool_id,
            document=tool_doc
        )

        return {"success": True, "tool_id": tool_id}

    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve conversation context for a session"""

        try:
            response = self.es.search(
                index=self.context_index,
                body={
                    "query": {
                        "term": {"session_id": session_id}
                    },
                    "sort": [{"updated_at": {"order": "desc"}}],
                    "size": 1
                }
            )

            if response["hits"]["total"]["value"] > 0:
                return response["hits"]["hits"][0]["_source"]
            else:
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
        metadata: Dict[str, Any] = None,
        ttl_hours: int = 24
    ) -> Dict[str, Any]:
        """Store conversation context in AgenticBuilder"""

        # Calculate TTL
        from datetime import timedelta
        ttl = datetime.utcnow() + timedelta(hours=ttl_hours)

        context_doc = {
            "session_id": session_id,
            "agent_id": agent_id,
            "customer_id": customer_id,
            "context_data": context_data,
            "conversation_history": conversation_history,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "ttl": ttl.isoformat()
        }

        response = self.es.index(
            index=self.context_index,
            document=context_doc
        )

        return {
            "success": True,
            "context_id": response["_id"],
            "session_id": session_id
        }

    def update_context(
        self,
        session_id: str,
        new_message: Dict[str, Any],
        context_updates: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Update existing context with new conversation turn"""

        # Get existing context
        existing_context = self.get_context(session_id)

        if not existing_context:
            return {"success": False, "error": "Context not found"}

        # Append new message to conversation history
        conversation_history = existing_context.get("conversation_history", [])
        conversation_history.append(new_message)

        # Update context data if provided
        context_data = existing_context.get("context_data", {})
        if context_updates:
            context_data.update(context_updates)

        # Store updated context
        return self.store_context(
            session_id=session_id,
            agent_id=existing_context["agent_id"],
            customer_id=existing_context["customer_id"],
            context_data=context_data,
            conversation_history=conversation_history,
            metadata=existing_context.get("metadata", {})
        )

    def get_available_tools(self, tool_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Get tool definitions for agent"""

        query = {"match_all": {}}
        if tool_ids:
            query = {"terms": {"tool_id": tool_ids}}

        response = self.es.search(
            index=self.tools_index,
            body={
                "query": query,
                "size": 100
            }
        )

        tools = [hit["_source"] for hit in response["hits"]["hits"]]
        return tools

    def log_tool_execution(
        self,
        session_id: str,
        tool_id: str,
        tool_name: str,
        input_parameters: Dict[str, Any],
        output_result: Dict[str, Any],
        status: str,
        execution_time_ms: float,
        error_message: str = None
    ) -> Dict[str, Any]:
        """Log tool execution for monitoring and analytics"""

        execution_doc = {
            "execution_id": f"exec_{datetime.utcnow().timestamp()}",
            "session_id": session_id,
            "tool_id": tool_id,
            "tool_name": tool_name,
            "input_parameters": input_parameters,
            "output_result": output_result,
            "status": status,
            "error_message": error_message,
            "execution_time_ms": execution_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }

        response = self.es.index(
            index=self.executions_index,
            document=execution_doc
        )

        # Update tool statistics
        self._update_tool_stats(tool_id, status, execution_time_ms)

        return {"success": True, "execution_id": execution_doc["execution_id"]}

    def _update_tool_stats(self, tool_id: str, status: str, execution_time_ms: float):
        """Update tool usage statistics"""

        try:
            # Increment usage count and update success rate
            self.es.update(
                index=self.tools_index,
                id=tool_id,
                body={
                    "script": {
                        "source": """
                            ctx._source.usage_count += 1;
                            if (params.status == 'success') {
                                ctx._source.success_rate =
                                    (ctx._source.success_rate * (ctx._source.usage_count - 1) + 1.0) /
                                    ctx._source.usage_count;
                            } else {
                                ctx._source.success_rate =
                                    (ctx._source.success_rate * (ctx._source.usage_count - 1)) /
                                    ctx._source.usage_count;
                            }
                            ctx._source.avg_latency_ms =
                                (ctx._source.avg_latency_ms * (ctx._source.usage_count - 1) + params.latency) /
                                ctx._source.usage_count;
                        """,
                        "params": {
                            "status": status,
                            "latency": execution_time_ms
                        }
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error updating tool stats: {e}")


class CustomerSupportAgent:
    """
    Customer Support Agent using Elastic AgenticBuilder
    """

    def __init__(
        self,
        agent_id: str = "customer-support-agent",
        elasticsearch_url: str = None,
        elasticsearch_api_key: str = None
    ):
        # Initialize Elasticsearch
        self.es_url = elasticsearch_url or os.getenv("ES_URL")
        self.es_api_key = elasticsearch_api_key or os.getenv("ES_API_KEY")

        self.es = Elasticsearch(
            self.es_url,
            api_key=self.es_api_key,
            verify_certs=True
        )

        # Initialize AgenticBuilder
        self.agentic = AgenticBuilderClient(self.es)

        # Initialize Bedrock for Claude
        self.bedrock = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )

        self.agent_id = agent_id
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

        # Register agent and tools
        self._register_agent()
        self._register_tools()

        logger.info(f"Customer Support Agent initialized with AgenticBuilder")

    def _register_agent(self):
        """Register the customer support agent in AgenticBuilder"""

        system_prompt = """You are a helpful customer support AI assistant.

Your capabilities:
- Answer customer questions using the knowledge base
- Check order status and tracking information
- Search for product information and availability
- Create support tickets for complex issues
- Provide empathetic and accurate responses

Guidelines:
- Always be polite and professional
- Search the knowledge base before answering
- If you cannot resolve an issue, create a support ticket
- Provide order tracking information when available
- Suggest relevant products when appropriate

Use the available tools to help customers effectively."""

        self.agentic.register_agent(
            agent_id=self.agent_id,
            name="Customer Support Agent",
            description="AI-powered customer support agent for orders, products, and issues",
            system_prompt=system_prompt,
            tools=[
                "hybrid_search_kb",
                "get_order_status",
                "search_products",
                "check_inventory",
                "elastic_rerank_results",
                "create_support_ticket",
                "send_notification"
            ],
            model="claude-3.5-sonnet"
        )

    def _register_tools(self):
        """Register all tools in AgenticBuilder"""

        tools = [
            {
                "tool_id": "hybrid_search_kb",
                "name": "hybrid_search_kb",
                "description": "Search knowledge base using hybrid search (BM25 + ELSER). Returns relevant support articles and FAQs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Customer question or issue description"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                },
                "function_name": "hybrid_search_kb"
            },
            {
                "tool_id": "get_order_status",
                "name": "get_order_status",
                "description": "Get current status, tracking information, and details for a customer order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "Order ID to lookup"
                        }
                    },
                    "required": ["order_id"]
                },
                "function_name": "get_order_status"
            },
            {
                "tool_id": "search_products",
                "name": "search_products",
                "description": "Search product catalog using semantic search. Returns product details, pricing, and availability.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Product name or description to search for"
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category filter"
                        }
                    },
                    "required": ["query"]
                },
                "function_name": "search_products"
            },
            {
                "tool_id": "check_inventory",
                "name": "check_inventory",
                "description": "Check real-time inventory and availability for a specific product.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": "Product ID to check"
                        }
                    },
                    "required": ["product_id"]
                },
                "function_name": "check_inventory"
            },
            {
                "tool_id": "elastic_rerank_results",
                "name": "elastic_rerank_results",
                "description": "Rerank search results using Elastic Learning to Rank for maximum relevance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Original search query"
                        },
                        "document_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of document IDs to rerank"
                        }
                    },
                    "required": ["query", "document_ids"]
                },
                "function_name": "elastic_rerank_results"
            },
            {
                "tool_id": "create_support_ticket",
                "name": "create_support_ticket",
                "description": "Create a support ticket for issues requiring human agent attention. Use when AI cannot resolve the issue.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Customer ID"
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "Type of issue (refund, technical, shipping, etc.)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the issue"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Priority level"
                        }
                    },
                    "required": ["customer_id", "issue_type", "description"]
                },
                "function_name": "create_support_ticket"
            },
            {
                "tool_id": "send_notification",
                "name": "send_notification",
                "description": "Send notification to customer via email or SMS using Elastic AgenticBuilder.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Customer ID"
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["email", "sms"],
                            "description": "Notification channel"
                        },
                        "message": {
                            "type": "string",
                            "description": "Notification message"
                        }
                    },
                    "required": ["customer_id", "channel", "message"]
                },
                "function_name": "send_notification"
            }
        ]

        for tool in tools:
            self.agentic.register_tool(**tool)

    def call_tool(self, tool_name: str, parameters: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Execute a tool and log the execution"""

        import time
        start_time = time.time()

        try:
            # Import tool functions
            from agents.customer_support_tools import (
                hybrid_search_kb,
                get_order_status,
                search_products,
                check_inventory,
                elastic_rerank_results,
                create_support_ticket,
                send_notification
            )

            # Map tool names to functions
            tool_functions = {
                "hybrid_search_kb": lambda p: hybrid_search_kb(self.es, **p),
                "get_order_status": lambda p: get_order_status(self.es, **p),
                "search_products": lambda p: search_products(self.es, **p),
                "check_inventory": lambda p: check_inventory(self.es, **p),
                "elastic_rerank_results": lambda p: elastic_rerank_results(self.es, **p),
                "create_support_ticket": lambda p: create_support_ticket(self.es, **p),
                "send_notification": lambda p: send_notification(self.es, **p)
            }

            # Execute tool
            result = tool_functions[tool_name](parameters)

            execution_time = (time.time() - start_time) * 1000
            status = "success" if result.get("success", False) else "error"

            # Log execution in AgenticBuilder
            self.agentic.log_tool_execution(
                session_id=session_id,
                tool_id=tool_name,
                tool_name=tool_name,
                input_parameters=parameters,
                output_result=result,
                status=status,
                execution_time_ms=execution_time
            )

            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            # Log failed execution
            self.agentic.log_tool_execution(
                session_id=session_id,
                tool_id=tool_name,
                tool_name=tool_name,
                input_parameters=parameters,
                output_result={},
                status="error",
                execution_time_ms=execution_time,
                error_message=str(e)
            )

            return {"success": False, "error": str(e)}

    def handle_customer_query(
        self,
        query: str,
        session_id: str,
        customer_id: str = None
    ) -> str:
        """
        Main entry point for customer queries
        Uses AgenticBuilder for context management
        """

        # Get or create context
        context = self.agentic.get_context(session_id)

        if not context:
            # Create new context
            context = {
                "customer_id": customer_id or "anonymous",
                "context_data": {},
                "conversation_history": []
            }
            self.agentic.store_context(
                session_id=session_id,
                agent_id=self.agent_id,
                customer_id=customer_id or "anonymous",
                context_data={},
                conversation_history=[],
                metadata={"channel": "chat"}
            )
        else:
            conversation_history = context.get("conversation_history", [])

        # Add user message to context
        user_message = {
            "role": "user",
            "content": query,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Get tool definitions from AgenticBuilder
        agent_doc = self.es.get(index="agenticbuilder-agents", id=self.agent_id)
        system_prompt = agent_doc["_source"]["system_prompt"]
        tool_ids = agent_doc["_source"]["tools"]
        tools = self.agentic.get_available_tools(tool_ids)

        # Convert tools to Claude format
        claude_tools = [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"]
            }
            for tool in tools
        ]

        # Prepare messages for Claude
        messages = context.get("conversation_history", []) + [user_message]

        # Call Claude via Bedrock with tools
        response = self._call_claude_with_tools(
            system_prompt=system_prompt,
            messages=messages,
            tools=claude_tools,
            session_id=session_id
        )

        # Add assistant message to context
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Update context in AgenticBuilder
        self.agentic.update_context(
            session_id=session_id,
            new_message=user_message
        )
        self.agentic.update_context(
            session_id=session_id,
            new_message=assistant_message
        )

        return response

    def _call_claude_with_tools(
        self,
        system_prompt: str,
        messages: List[Dict],
        tools: List[Dict],
        session_id: str,
        max_turns: int = 5
    ) -> str:
        """
        Call Claude with tool use capability
        Handles multi-turn tool calling
        """

        conversation = messages.copy()

        for turn in range(max_turns):
            # Prepare request for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in conversation
                ],
                "tools": tools
            }

            # Call Bedrock
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            response_body = json.loads(response["body"].read())

            # Check if Claude wants to use a tool
            if response_body.get("stop_reason") == "tool_use":
                content = response_body["content"]

                # Extract tool use
                tool_uses = [block for block in content if block["type"] == "tool_use"]

                # Add Claude's response to conversation
                conversation.append({
                    "role": "assistant",
                    "content": content
                })

                # Execute tools
                tool_results = []
                for tool_use in tool_uses:
                    tool_name = tool_use["name"]
                    tool_input = tool_use["input"]
                    tool_use_id = tool_use["id"]

