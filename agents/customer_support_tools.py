#!/usr/bin/env python3
"""
Customer Support Tools
Standalone tool functions for customer support operations
Used by both Strands and AgenticBuilder implementations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


def hybrid_search_kb(
    es: Elasticsearch,
    query: str,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Hybrid search using BM25 + ELSER
    Combines keyword and semantic search for best results
    """
    try:
        response = es.search(
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
                "size": top_k,
                "_source": ["title", "content", "category", "article_id"]
            }
        )

        results = [
            {
                "id": hit["_id"],
                "article_id": hit["_source"].get("article_id"),
                "title": hit["_source"].get("title", ""),
                "content": hit["_source"].get("content", ""),
                "category": hit["_source"].get("category", ""),
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]

        return {
            "success": True,
            "results": results,
            "total": response["hits"]["total"]["value"]
        }

    except Exception as e:
        logger.error(f"Error in hybrid_search_kb: {e}")
        return {"success": False, "error": str(e)}


def get_order_status(
    es: Elasticsearch,
    order_id: str
) -> Dict[str, Any]:
    """
    Get order status and tracking information
    """
    try:
        response = es.get(
            index="customer-orders",
            id=order_id
        )

        order = response["_source"]

        return {
            "success": True,
            "order_id": order_id,
            "status": order.get("status"),
            "tracking_number": order.get("tracking_number"),
            "estimated_delivery": order.get("estimated_delivery"),
            "items": order.get("items", []),
            "total": order.get("total"),
            "customer_id": order.get("customer_id")
        }

    except Exception as e:
        logger.error(f"Error in get_order_status: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Order {order_id} not found"
        }


def search_products(
    es: Elasticsearch,
    query: str,
    category: Optional[str] = None,
    top_k: int = 10
) -> Dict[str, Any]:
    """
    Search products using ELSER semantic search
    """
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

        response = es.search(
            index="customer-products",
            body={
                "query": search_query,
                "size": top_k,
                "_source": ["product_id", "name", "description", "price", "category", "in_stock", "quantity"]
            }
        )

        products = [
            {
                "id": hit["_id"],
                "product_id": hit["_source"].get("product_id"),
                "name": hit["_source"].get("name"),
                "description": hit["_source"].get("description"),
                "price": hit["_source"].get("price"),
                "category": hit["_source"].get("category"),
                "in_stock": hit["_source"].get("in_stock", False),
                "quantity": hit["_source"].get("quantity", 0),
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]

        return {
            "success": True,
            "products": products,
            "total": response["hits"]["total"]["value"]
        }

    except Exception as e:
        logger.error(f"Error in search_products: {e}")
        return {"success": False, "error": str(e)}


def check_inventory(
    es: Elasticsearch,
    product_id: str
) -> Dict[str, Any]:
    """
    Check inventory for a specific product
    """
    try:
        response = es.get(
            index="customer-products",
            id=product_id
        )

        product = response["_source"]

        return {
            "success": True,
            "product_id": product_id,
            "name": product.get("name"),
            "in_stock": product.get("in_stock", False),
            "quantity": product.get("quantity", 0),
            "warehouse_location": product.get("warehouse_location"),
            "restock_date": product.get("restock_date")
        }

    except Exception as e:
        logger.error(f"Error in check_inventory: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Product {product_id} not found"
        }


def elastic_rerank_results(
    es: Elasticsearch,
    query: str,
    document_ids: List[str]
) -> Dict[str, Any]:
    """
    Rerank results using Elastic Learning to Rank
    """
    try:
        response = es.search(
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
                },
                "_source": ["article_id", "title", "content"]
            }
        )

        reranked = [
            {
                "id": hit["_id"],
                "article_id": hit["_source"].get("article_id"),
                "title": hit["_source"].get("title"),
                "content": hit["_source"].get("content"),
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]

        return {
            "success": True,
            "reranked_results": reranked,
            "total": len(reranked)
        }

    except Exception as e:
        logger.error(f"Error in elastic_rerank_results: {e}")
        return {"success": False, "error": str(e)}


def create_support_ticket(
    es: Elasticsearch,
    customer_id: str,
    issue_type: str,
    description: str,
    priority: str = "medium",
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a support ticket
    """
    try:
        ticket = {
            "customer_id": customer_id,
            "session_id": session_id,
            "issue_type": issue_type,
            "description": description,
            "priority": priority,
            "status": "open",
            "assigned_agent": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = es.index(
            index="customer-tickets",
            document=ticket
        )

        ticket_id = response["_id"]

        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": f"Support ticket {ticket_id} created successfully",
            "priority": priority,
            "status": "open"
        }

    except Exception as e:
        logger.error(f"Error in create_support_ticket: {e}")
        return {"success": False, "error": str(e)}


def update_customer_record(
    es: Elasticsearch,
    customer_id: str,
    session_id: str,
    interaction_type: str,
    summary: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update customer interaction history
    """
    try:
        interaction = {
            "customer_id": customer_id,
            "session_id": session_id,
            "interaction_type": interaction_type,
            "summary": summary,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        response = es.index(
            index="customer-interactions",
            document=interaction
        )

        return {
            "success": True,
            "interaction_id": response["_id"],
            "message": "Customer record updated"
        }

    except Exception as e:
        logger.error(f"Error in update_customer_record: {e}")
        return {"success": False, "error": str(e)}


def send_notification(
    es: Elasticsearch,
    customer_id: str,
    channel: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send notification via email or SMS
    Stores notification in Elasticsearch for tracking
    """
    try:
        notification = {
            "customer_id": customer_id,
            "channel": channel,
            "message": message,
            "status": "sent",
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        response = es.index(
            index="customer-notifications",
            document=notification
        )

        return {
            "success": True,
            "notification_id": response["_id"],
            "message": f"Notification sent via {channel}"
        }

    except Exception as e:
        logger.error(f"Error in send_notification: {e}")
        return {"success": False, "error": str(e)}


def get_customer_history(
    es: Elasticsearch,
    customer_id: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get customer interaction history
    """
    try:
        response = es.search(
            index="customer-interactions",
            body={
                "query": {"term": {"customer_id": customer_id}},
                "sort": [{"timestamp": {"order": "desc"}}],
                "size": limit
            }
        )

        interactions = [
            {
                "id": hit["_id"],
                "interaction_type": hit["_source"].get("interaction_type"),
                "summary": hit["_source"].get("summary"),
                "timestamp": hit["_source"].get("timestamp")
            }
            for hit in response["hits"]["hits"]
        ]

        return {
            "success": True,
            "customer_id": customer_id,
            "interactions": interactions,
            "total": response["hits"]["total"]["value"]
        }

    except Exception as e:
        logger.error(f"Error in get_customer_history: {e}")
        return {"success": False, "error": str(e)}


def analyze_sentiment(
    es: Elasticsearch,
    text: str
) -> Dict[str, Any]:
    """
    Analyze sentiment using Elasticsearch ML
    """
    try:
        # Use Elasticsearch sentiment analysis
        response = es.ml.infer_trained_model(
            model_id="sentiment_analysis",
            docs=[{"text_field": text}]
        )

        prediction = response["inference_results"][0]["predicted_value"]

        return {
            "success": True,
            "sentiment": prediction,
            "text": text
        }

    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {e}")
        # Fallback to simple heuristic
        negative_words = ["bad", "terrible", "horrible", "angry", "frustrated", "disappointed"]
        positive_words = ["good", "great", "excellent", "happy", "satisfied", "pleased"]

        text_lower = text.lower()
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)

        if negative_count > positive_count:
            sentiment = "negative"
        elif positive_count > negative_count:
            sentiment = "positive"
        else:
            sentiment = "neutral"

        return {
            "success": True,
            "sentiment": sentiment,
            "text": text,
            "fallback": True
        }
