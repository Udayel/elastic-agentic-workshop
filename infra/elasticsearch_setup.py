#!/usr/bin/env python3
"""
Elasticsearch Index Setup Script
Creates all indices with proper mappings for customer support system
"""

import os
import sys
import logging
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElasticsearchSetup:
    """Setup Elasticsearch indices for customer support"""

    def __init__(self):
        self.es_url = os.getenv("ES_URL")
        self.es_api_key = os.getenv("ES_API_KEY")

        if not self.es_url or not self.es_api_key:
            logger.error("ES_URL and ES_API_KEY must be set in .env file")
            sys.exit(1)

        self.es = Elasticsearch(
            self.es_url,
            api_key=self.es_api_key,
            verify_certs=True
        )

        logger.info(f"Connected to Elasticsearch: {self.es_url}")

    def create_kb_index(self):
        """Create knowledge base index with ELSER embeddings"""
        index_name = "customer-kb"

        logger.info(f"Creating index: {index_name}")

        mapping = {
            "mappings": {
                "properties": {
                    "article_id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "content_embedding": {
                        "type": "sparse_vector"
                    },
                    "category": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "author": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "view_count": {"type": "long"},
                    "helpfulness_score": {"type": "float"}
                }
            }
        }

        if self.es.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
        else:
            self.es.indices.create(index=index_name, body=mapping)
            logger.info(f"✓ Created index: {index_name}")

    def create_orders_index(self):
        """Create orders index"""
        index_name = "customer-orders"

        logger.info(f"Creating index: {index_name}")

        mapping = {
            "mappings": {
                "properties": {
                    "order_id": {"type": "keyword"},
                    "customer_id": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "tracking_number": {"type": "keyword"},
                    "items": {
                        "type": "nested",
                        "properties": {
                            "product_id": {"type": "keyword"},
                            "name": {"type": "text"},
                            "quantity": {"type": "integer"},
                            "price": {"type": "float"}
                        }
                    },
                    "total": {"type": "float"},
                    "shipping_address": {"type": "text"},
                    "estimated_delivery": {"type": "date"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }

        if self.es.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
        else:
            self.es.indices.create(index=index_name, body=mapping)
            logger.info(f"✓ Created index: {index_name}")

    def create_products_index(self):
        """Create products index with ELSER embeddings"""
        index_name = "customer-products"

        logger.info(f"Creating index: {index_name}")

        mapping = {
            "mappings": {
                "properties": {
                    "product_id": {"type": "keyword"},
                    "name": {"type": "text"},
                    "description": {"type": "text"},
                    "description_embedding": {
                        "type": "sparse_vector"
                    },
                    "category": {"type": "keyword"},
                    "price": {"type": "float"},
                    "in_stock": {"type": "boolean"},
                    "quantity": {"type": "integer"},
                    "warehouse_location": {"type": "keyword"},
                    "restock_date": {"type": "date"},
                    "specifications": {"type": "object"},
                    "images": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }

        if self.es.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
        else:
            self.es.indices.create(index=index_name, body=mapping)
            logger.info(f"✓ Created index: {index_name}")

    def create_tickets_index(self):
        """Create support tickets index"""
        index_name = "customer-tickets"

        logger.info(f"Creating index: {index_name}")

        mapping = {
            "mappings": {
                "properties": {
                    "ticket_id": {"type": "keyword"},
                    "customer_id": {"type": "keyword"},
                    "session_id": {"type": "keyword"},
                    "issue_type": {"type": "keyword"},
                    "description": {"type": "text"},
                    "priority": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "assigned_agent": {"type": "keyword"},
                    "resolution": {"type": "text"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "resolved_at": {"type": "date"}
                }
            }
        }

        if self.es.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
        else:
            self.es.indices.create(index=index_name, body=mapping)
            logger.info(f"✓ Created index: {index_name}")

    def create_interactions_index(self):
        """Create customer interactions index"""
        index_name = "customer-interactions"

        logger.info(f"Creating index: {index_name}")

        mapping = {
            "mappings": {
                "properties": {
                    "customer_id": {"type": "keyword"},
                    "session_id": {"type": "keyword"},
                    "interaction_type": {"type": "keyword"},
                    "summary": {"type": "text"},
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "date"}
                }
            }
        }

        if self.es.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
        else:
            self.es.indices.create(index=index_name, body=mapping)
            logger.info(f"✓ Created index: {index_name}")

    def create_notifications_index(self):
        """Create notifications index"""
        index_name = "customer-notifications"

        logger.info(f"Creating index: {index_name}")

        mapping = {
            "mappings": {
                "properties": {
                    "customer_id": {"type": "keyword"},
                    "channel": {"type": "keyword"},
                    "message": {"type": "text"},
                    "status": {"type": "keyword"},
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "date"}
                }
            }
        }

        if self.es.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
        else:
            self.es.indices.create(index=index_name, body=mapping)
            logger.info(f"✓ Created index: {index_name}")

    def create_analytics_index(self):
        """Create analytics index"""
        index_name = "customer-analytics"

        logger.info(f"Creating index: {index_name}")

        mapping = {
            "mappings": {
                "properties": {
                    "metric_name": {"type": "keyword"},
                    "metric_value": {"type": "float"},
                    "dimensions": {"type": "object"},
                    "timestamp": {"type": "date"}
                }
            }
        }

        if self.es.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
        else:
            self.es.indices.create(index=index_name, body=mapping)
            logger.info(f"✓ Created index: {index_name}")

    def setup_all(self):
        """Create all indices"""
        logger.info("="*60)
        logger.info("Elasticsearch Index Setup")
        logger.info("="*60)

        self.create_kb_index()
        self.create_orders_index()
        self.create_products_index()
        self.create_tickets_index()
        self.create_interactions_index()
        self.create_notifications_index()
        self.create_analytics_index()

        logger.info("="*60)
        logger.info("All indices created successfully!")
        logger.info("="*60)

        logger.info("\nNext steps:")
        logger.info("1. Deploy ELSER model: python infra/deploy_elser.py")
        logger.info("2. Seed sample data: python infra/seed_data.py")
        logger.info("3. Test the agent: python main.py")


def main():
    setup = ElasticsearchSetup()
    setup.setup_all()


if __name__ == "__main__":
    main()
