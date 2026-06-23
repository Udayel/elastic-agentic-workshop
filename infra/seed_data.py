#!/usr/bin/env python3
"""
Seed Sample Data
Populates Elasticsearch indices with sample data for testing
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSeeder:
    """Seed sample data into Elasticsearch"""

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

    def seed_knowledge_base(self):
        """Seed knowledge base articles"""
        logger.info("Seeding knowledge base...")

        articles = [
            {
                "article_id": "KB-001",
                "title": "Return Policy",
                "content": "Our return policy allows you to return items within 30 days of purchase. Items must be unused and in original packaging. Refunds are processed within 5-7 business days after we receive the returned item.",
                "category": "returns",
                "tags": ["returns", "refunds", "policy"],
                "author": "support_team",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "view_count": 1523,
                "helpfulness_score": 4.7
            },
            {
                "article_id": "KB-002",
                "title": "Shipping Information",
                "content": "We offer free standard shipping on orders over $50. Standard shipping takes 5-7 business days. Express shipping (2-3 days) is available for $15. International shipping is available to select countries.",
                "category": "shipping",
                "tags": ["shipping", "delivery", "tracking"],
                "author": "support_team",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "view_count": 2341,
                "helpfulness_score": 4.5
            },
            {
                "article_id": "KB-003",
                "title": "Payment Methods",
                "content": "We accept all major credit cards (Visa, MasterCard, American Express, Discover), PayPal, Apple Pay, and Google Pay. All payments are processed securely using industry-standard encryption.",
                "category": "payment",
                "tags": ["payment", "checkout", "security"],
                "author": "support_team",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "view_count": 987,
                "helpfulness_score": 4.8
            },
            {
                "article_id": "KB-004",
                "title": "Product Warranty",
                "content": "All our products come with a 1-year manufacturer warranty covering defects in materials and workmanship. Extended warranty options are available at checkout. Warranty claims can be filed through your account or by contacting support.",
                "category": "warranty",
                "tags": ["warranty", "guarantee", "support"],
                "author": "support_team",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "view_count": 756,
                "helpfulness_score": 4.6
            },
            {
                "article_id": "KB-005",
                "title": "Account Management",
                "content": "You can manage your account by logging in and accessing the Account Settings page. Here you can update personal information, change password, manage addresses, view order history, and set communication preferences.",
                "category": "account",
                "tags": ["account", "profile", "settings"],
                "author": "support_team",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "view_count": 1234,
                "helpfulness_score": 4.4
            }
        ]

        for article in articles:
            try:
                self.es.index(
                    index="customer-kb",
                    id=article["article_id"],
                    document=article
                )
                logger.info(f"✓ Seeded article: {article['article_id']}")
            except Exception as e:
                logger.error(f"Error seeding article {article['article_id']}: {e}")

    def seed_products(self):
        """Seed product catalog"""
        logger.info("Seeding products...")

        products = [
            {
                "product_id": "PROD-001",
                "name": "Wireless Bluetooth Headphones",
                "description": "Premium over-ear wireless headphones with active noise cancellation, 30-hour battery life, and superior sound quality. Perfect for music lovers and professionals.",
                "category": "electronics",
                "price": 149.99,
                "in_stock": True,
                "quantity": 50,
                "warehouse_location": "US-EAST-1",
                "specifications": {
                    "battery_life": "30 hours",
                    "connectivity": "Bluetooth 5.0",
                    "noise_cancellation": True,
                    "color": "Black"
                },
                "images": ["prod001-1.jpg", "prod001-2.jpg"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "product_id": "PROD-002",
                "name": "Smart Watch Pro",
                "description": "Advanced fitness tracker and smartwatch with heart rate monitoring, GPS, sleep tracking, and 5-day battery life. Compatible with iOS and Android.",
                "category": "electronics",
                "price": 299.99,
                "in_stock": True,
                "quantity": 35,
                "warehouse_location": "US-WEST-1",
                "specifications": {
                    "battery_life": "5 days",
                    "water_resistance": "50m",
                    "display": "AMOLED",
                    "gps": True
                },
                "images": ["prod002-1.jpg", "prod002-2.jpg"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "product_id": "PROD-003",
                "name": "USB-C Charging Cable",
                "description": "Durable braided USB-C cable with fast charging support. 6-foot length, compatible with all USB-C devices. Reinforced connectors for long-lasting use.",
                "category": "accessories",
                "price": 19.99,
                "in_stock": True,
                "quantity": 200,
                "warehouse_location": "US-EAST-1",
                "specifications": {
                    "length": "6 feet",
                    "fast_charging": True,
                    "material": "Braided nylon",
                    "connector": "USB-C to USB-C"
                },
                "images": ["prod003-1.jpg"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "product_id": "PROD-004",
                "name": "Portable Power Bank 20000mAh",
                "description": "High-capacity portable charger with dual USB ports and USB-C input/output. Fast charge your devices on the go. LED indicator shows remaining power.",
                "category": "accessories",
                "price": 49.99,
                "in_stock": True,
                "quantity": 75,
                "warehouse_location": "US-WEST-1",
                "specifications": {
                    "capacity": "20000mAh",
                    "ports": "2x USB-A, 1x USB-C",
                    "fast_charging": True,
                    "weight": "350g"
                },
                "images": ["prod004-1.jpg", "prod004-2.jpg"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "product_id": "PROD-005",
                "name": "Mechanical Gaming Keyboard",
                "description": "RGB backlit mechanical keyboard with customizable keys, programmable macros, and anti-ghosting technology. Built for gamers and professionals.",
                "category": "electronics",
                "price": 129.99,
                "in_stock": False,
                "quantity": 0,
                "warehouse_location": "US-EAST-1",
                "restock_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                "specifications": {
                    "switch_type": "Cherry MX Red",
                    "rgb": True,
                    "connectivity": "Wired USB",
                    "layout": "Full-size"
                },
                "images": ["prod005-1.jpg", "prod005-2.jpg"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]

        for product in products:
            try:
                self.es.index(
                    index="customer-products",
                    id=product["product_id"],
                    document=product
                )
                logger.info(f"✓ Seeded product: {product['product_id']}")
            except Exception as e:
                logger.error(f"Error seeding product {product['product_id']}: {e}")

    def seed_orders(self):
        """Seed sample orders"""
        logger.info("Seeding orders...")

        orders = [
            {
                "order_id": "ORD-12345",
                "customer_id": "CUST-001",
                "status": "shipped",
                "tracking_number": "1Z999AA10123456784",
                "items": [
                    {
                        "product_id": "PROD-001",
                        "name": "Wireless Bluetooth Headphones",
                        "quantity": 1,
                        "price": 149.99
                    }
                ],
                "total": 149.99,
                "shipping_address": "123 Main St, New York, NY 10001",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "order_id": "ORD-12346",
                "customer_id": "CUST-002",
                "status": "delivered",
                "tracking_number": "1Z999AA10123456785",
                "items": [
                    {
                        "product_id": "PROD-002",
                        "name": "Smart Watch Pro",
                        "quantity": 1,
                        "price": 299.99
                    },
                    {
                        "product_id": "PROD-003",
                        "name": "USB-C Charging Cable",
                        "quantity": 2,
                        "price": 19.99
                    }
                ],
                "total": 339.97,
                "shipping_address": "456 Oak Ave, San Francisco, CA 94102",
                "estimated_delivery": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "created_at": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "order_id": "ORD-12347",
                "customer_id": "CUST-003",
                "status": "processing",
                "tracking_number": None,
                "items": [
                    {
                        "product_id": "PROD-004",
                        "name": "Portable Power Bank 20000mAh",
                        "quantity": 1,
                        "price": 49.99
                    }
                ],
                "total": 49.99,
                "shipping_address": "789 Pine St, Seattle, WA 98101",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=5)).isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]

        for order in orders:
            try:
                self.es.index(
                    index="customer-orders",
                    id=order["order_id"],
                    document=order
                )
                logger.info(f"✓ Seeded order: {order['order_id']}")
            except Exception as e:
                logger.error(f"Error seeding order {order['order_id']}: {e}")

    def seed_all(self):
        """Seed all data"""
        logger.info("="*60)
        logger.info("Seeding Sample Data")
        logger.info("="*60)

        self.seed_knowledge_base()
        self.seed_products()
        self.seed_orders()

        logger.info("="*60)
        logger.info("Sample data seeded successfully!")
        logger.info("="*60)

        logger.info("\nNote: ELSER embeddings will be generated automatically")
        logger.info("if you have deployed the .elser_model_2 pipeline")
        logger.info("\nNext steps:")
        logger.info("1. Test search: python test_search.py")
        logger.info("2. Run agent: python main.py")


def main():
    seeder = DataSeeder()
    seeder.seed_all()


if __name__ == "__main__":
    main()
