#!/usr/bin/env python3
"""
Simple Customer Support Agent
Direct Elasticsearch integration without external frameworks
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Import tool functions
from agents.customer_support_tools import (
    hybrid_search_kb,
    get_order_status,
    search_products,
    check_inventory,
    create_support_ticket,
    send_notification
)

load_dotenv()

logger = logging.getLogger(__name__)


class SimpleCustomerSupportAgent:
    """
    Simple Customer Support Agent
    No external frameworks - just Elasticsearch + Python
    """

    def __init__(
        self,
        session_id: str = None,
        customer_id: str = None
    ):
        # Initialize Elasticsearch
        self.es_url = os.getenv("ES_URL")
        self.es_api_key = os.getenv("ES_API_KEY")

        if not self.es_url or not self.es_api_key:
            raise ValueError("ES_URL and ES_API_KEY must be set in config/.env")

        self.es = Elasticsearch(
            self.es_url,
            api_key=self.es_api_key,
            verify_certs=True
        )

        self.session_id = session_id or f"session_{int(time.time())}"
        self.customer_id = customer_id or "anonymous"

        # Context storage
        self.context = {
            "session_id": self.session_id,
            "customer_id": self.customer_id,
            "conversation_history": [],
            "context_data": {}
        }

        # Create context index if needed
        self._ensure_context_index()

        logger.info(f"Agent initialized - Session: {self.session_id}")

    def _ensure_context_index(self):
        """Ensure context index exists"""
        context_index = "agenticbuilder-context"

        if not self.es.indices.exists(index=context_index):
            self.es.indices.create(
                index=context_index,
                body={
                    "mappings": {
                        "properties": {
                            "session_id": {"type": "keyword"},
                            "customer_id": {"type": "keyword"},
                            "conversation_history": {
                                "type": "nested",
                                "properties": {
                                    "role": {"type": "keyword"},
                                    "content": {"type": "text"},
                                    "timestamp": {"type": "date"}
                                }
                            },
                            "context_data": {"type": "object"},
                            "updated_at": {"type": "date"}
                        }
                    }
                }
            )

    def handle_customer_query(self, query: str) -> str:
        """Handle a customer query"""

        # Add user message to context
        user_message = {
            "role": "user",
            "content": query,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.context["conversation_history"].append(user_message)

        # Determine intent and select tool
        response = self._process_query(query)

        # Add assistant response to context
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.context["conversation_history"].append(assistant_message)

        # Save context
        self._save_context()

        return response

    def _process_query(self, query: str) -> str:
        """Process query and return response"""

        query_lower = query.lower()

        try:
            # Intent: Return policy / KB search
            if any(word in query_lower for word in ["return", "refund", "policy", "warranty", "shipping", "payment"]):
                result = hybrid_search_kb(self.es, query, top_k=3)
                if result["success"] and result["results"]:
                    article = result["results"][0]
                    return f"{article['title']}\n\n{article['content']}"
                return "I couldn't find information about that. Let me create a support ticket for you."

            # Intent: Order status
            elif "order" in query_lower and "ORD-" in query:
                import re
                match = re.search(r'ORD-\d+', query)
                if match:
                    order_id = match.group(0)
                    result = get_order_status(self.es, order_id)
                    if result["success"]:
                        order = result
                        status_text = f"Order {order_id} is currently {order['status']}."
                        if order.get('tracking_number'):
                            status_text += f"\nTracking Number: {order['tracking_number']}"
                        if order.get('estimated_delivery'):
                            status_text += f"\nEstimated Delivery: {order['estimated_delivery']}"
                        return status_text
                    return f"I couldn't find order {order_id}. Please check the order number."

            # Intent: Product search
            elif any(word in query_lower for word in ["product", "headphone", "watch", "cable", "charger", "show me", "looking for"]):
                result = search_products(self.es, query, top_k=5)
                if result["success"] and result["products"]:
                    products = result["products"][:3]  # Top 3
                    response = "I found these products:\n\n"
                    for i, prod in enumerate(products, 1):
                        stock_status = "In stock" if prod["in_stock"] else "Out of stock"
                        response += f"{i}. {prod['name']} - ${prod['price']}\n"
                        response += f"   {prod['description'][:80]}...\n"
                        response += f"   Status: {stock_status}\n\n"
                    return response.strip()
                return "I couldn't find any products matching your search."

            # Intent: Inventory check
            elif "stock" in query_lower and "PROD-" in query:
                import re
                match = re.search(r'PROD-\d+', query)
                if match:
                    product_id = match.group(0)
                    result = check_inventory(self.es, product_id)
                    if result["success"]:
                        status = "in stock" if result["in_stock"] else "out of stock"
                        response = f"{result['name']} is {status}."
                        if result["in_stock"]:
                            response += f"\n\nAvailable quantity: {result['quantity']}"
                            if result.get('warehouse_location'):
                                response += f"\nWarehouse: {result['warehouse_location']}"
                        return response
                    return f"I couldn't find product {product_id}."

            # Intent: Problem/Issue
            elif any(word in query_lower for word in ["problem", "issue", "defective", "broken", "not working", "help"]):
                # Create support ticket
                ticket_result = create_support_ticket(
                    self.es,
                    customer_id=self.customer_id,
                    issue_type="product_issue",
                    description=query,
                    priority="medium",
                    session_id=self.session_id
                )
                if ticket_result["success"]:
                    return f"I understand you're having an issue. I've created support ticket {ticket_result['ticket_id']} with medium priority. A specialist will contact you within 24 hours to resolve this."
                return "I understand you're having an issue. Let me help you with that."

            # Default: KB search
            else:
                result = hybrid_search_kb(self.es, query, top_k=5)
                if result["success"] and result["results"]:
                    article = result["results"][0]
                    return f"{article['title']}\n\n{article['content']}"
                return "I'm not sure how to help with that. Could you please rephrase your question or ask about our products, orders, or policies?"

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I apologize, but I encountered an error. Please try again or contact support."

    def _save_context(self):
        """Save conversation context to Elasticsearch"""
        try:
            self.context["updated_at"] = datetime.utcnow().isoformat()

            self.es.index(
                index="agenticbuilder-context",
                id=self.session_id,
                document=self.context
            )
        except Exception as e:
            logger.error(f"Error saving context: {e}")

    def get_analytics(self) -> Dict[str, Any]:
        """Get session analytics"""
        return {
            "session_id": self.session_id,
            "customer_id": self.customer_id,
            "total_messages": len(self.context["conversation_history"]),
            "conversation_history": self.context["conversation_history"][-5:]  # Last 5 messages
        }

    def clear_history(self):
        """Clear conversation history"""
        self.context["conversation_history"] = []
        self._save_context()
