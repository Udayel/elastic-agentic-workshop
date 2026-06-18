#!/usr/bin/env python3
"""
MCP Tools for Travel Agent
Implements Model Context Protocol for Claude/AgenticBuilder integration
"""

import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import boto3

load_dotenv()

class TravelMCPTools:
    """
    MCP-compliant tools for travel agent
    """

    def __init__(self):
        # Elasticsearch connection
        self.es = Elasticsearch(
            cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
            basic_auth=(
                os.getenv('ELASTIC_USERNAME'),
                os.getenv('ELASTIC_PASSWORD')
            )
        )

        # AWS Bedrock for LLM
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )

    def get_tool_definitions(self) -> List[Dict]:
        """
        Return MCP tool definitions for Claude
        """
        return [
            {
                "name": "search_destinations",
                "description": "Search for travel destinations using semantic search. Understands natural language queries like 'romantic beach getaway' or 'tech-savvy foodie destination'. Returns cities that match the criteria.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language description of desired destination (e.g., 'warm beach with great food', 'cultural city with history')"
                        },
                        "budget_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Budget constraint for the trip"
                        },
                        "season": {
                            "type": "string",
                            "enum": ["spring", "summer", "autumn", "winter"],
                            "description": "Preferred travel season"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 3)",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_activities",
                "description": "Find activities and things to do in a city using ELSER semantic search. Understands preferences like 'kid-friendly tech activities' or 'romantic sunset experiences'. Returns relevant activities with ratings and details.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name to search activities in"
                        },
                        "query": {
                            "type": "string",
                            "description": "What kind of activities are desired (e.g., 'family-friendly museums', 'foodie experiences', 'adventure activities')"
                        },
                        "duration_max": {
                            "type": "number",
                            "description": "Maximum duration in hours"
                        },
                        "price_range": {
                            "type": "string",
                            "enum": ["$", "$$", "$$$"],
                            "description": "Price range"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["city", "query"]
                }
            },
            {
                "name": "search_hotels",
                "description": "Search for hotels and accommodations using semantic search. Understands requests like 'boutique hotel with character' or 'luxury resort with ocean views'. Returns hotels with ratings and prices.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City to search hotels in"
                        },
                        "query": {
                            "type": "string",
                            "description": "Hotel preferences (e.g., 'romantic with spa', 'business hotel with gym', 'family-friendly')"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price per night in USD"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["city", "query"]
                }
            },
            {
                "name": "search_flights",
                "description": "Search for flight options using Strands API. Provides real flight data with prices, airlines, and schedules.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Departure city or airport code (e.g., 'New York' or 'JFK')"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Arrival city or airport code"
                        },
                        "departure_date": {
                            "type": "string",
                            "description": "Departure date in YYYY-MM-DD format"
                        },
                        "return_date": {
                            "type": "string",
                            "description": "Return date in YYYY-MM-DD format (optional for one-way)"
                        },
                        "passengers": {
                            "type": "integer",
                            "description": "Number of passengers (default: 1)",
                            "default": 1
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price per person in USD"
                        }
                    },
                    "required": ["origin", "destination", "departure_date"]
                }
            },
            {
                "name": "compare_deals",
                "description": "Compare prices across different providers and find the best deals. Analyzes flights, hotels, or packages and returns best value options.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "item_type": {
                            "type": "string",
                            "enum": ["flight", "hotel", "package"],
                            "description": "Type of item to compare"
                        },
                        "items": {
                            "type": "array",
                            "description": "List of item IDs to compare",
                            "items": {"type": "string"}
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["price", "rating", "value"],
                            "description": "How to sort results (default: value)",
                            "default": "value"
                        }
                    },
                    "required": ["item_type", "items"]
                }
            },
            {
                "name": "create_itinerary",
                "description": "Generate a day-by-day travel itinerary optimized for the user's preferences, budget, and time constraints. Uses AI to create a balanced schedule.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "destination": {
                            "type": "string",
                            "description": "Destination city"
                        },
                        "num_days": {
                            "type": "integer",
                            "description": "Number of days for the trip"
                        },
                        "activities": {
                            "type": "array",
                            "description": "List of activity IDs to include",
                            "items": {"type": "string"}
                        },
                        "preferences": {
                            "type": "object",
                            "description": "User preferences",
                            "properties": {
                                "pace": {
                                    "type": "string",
                                    "enum": ["relaxed", "moderate", "packed"]
                                },
                                "interests": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["destination", "num_days", "activities"]
                }
            },
            {
                "name": "send_notification",
                "description": "Send trip details via SMS or email using AgentBuilder notification service. Sends formatted trip summary with booking links.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "enum": ["sms", "email", "both"],
                            "description": "Notification method"
                        },
                        "recipient": {
                            "type": "string",
                            "description": "Phone number (for SMS) or email address"
                        },
                        "trip_data": {
                            "type": "object",
                            "description": "Trip information to send",
                            "properties": {
                                "destination": {"type": "string"},
                                "dates": {"type": "string"},
                                "summary": {"type": "string"},
                                "total_cost": {"type": "number"}
                            }
                        }
                    },
                    "required": ["method", "recipient", "trip_data"]
                }
            }
        ]

    def search_destinations(
        self,
        query: str,
        budget_level: Optional[str] = None,
        season: Optional[str] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Search for destinations using ELSER
        """
        print(f"🔍 Searching destinations: '{query}'")

        try:
            # Build search query
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
                "size": top_k
            }

            # Add filters
            filters = []
            if budget_level:
                filters.append({"term": {"budget_level": budget_level}})
            if season:
                filters.append({"term": {"best_season": season}})

            if filters:
                search_body["query"]["bool"]["filter"] = filters

            # Execute search
            results = self.es.search(index="travel-cities", body=search_body)

            # Format results
            destinations = []
            for hit in results['hits']['hits']:
                dest = hit['_source']
                destinations.append({
                    "name": dest['name'],
                    "country": dest['country'],
                    "description": dest['description'],
                    "highlights": dest['highlights'],
                    "budget_level": dest['budget_level'],
                    "tags": dest['tags'],
                    "relevance_score": hit['_score']
                })

            return {
                "success": True,
                "count": len(destinations),
                "destinations": destinations
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def search_activities(
        self,
        city: str,
        query: str,
        duration_max: Optional[float] = None,
        price_range: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Search for activities using ELSER
        """
        print(f"🎯 Searching activities in {city}: '{query}'")

        try:
            # Build search
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"city": city}},
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
                "size": top_k
            }

            # Add filters
            filters = []
            if duration_max:
                filters.append({"range": {"duration_hours": {"lte": duration_max}}})
            if price_range:
                filters.append({"term": {"price_range": price_range}})

            if filters:
                search_body["query"]["bool"]["filter"] = filters

            results = self.es.search(index="travel-activities", body=search_body)

            # Format results
            activities = []
            for hit in results['hits']['hits']:
                activity = hit['_source']
                activities.append({
                    "name": activity['name'],
                    "description": activity['description'],
                    "category": activity['category'],
                    "duration_hours": activity['duration_hours'],
                    "price_range": activity['price_range'],
                    "rating": activity.get('rating', 0),
                    "suitable_for": activity['suitable_for'],
                    "tags": activity['tags'],
                    "relevance_score": hit['_score']
                })

            return {
                "success": True,
                "count": len(activities),
                "activities": activities
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def search_hotels(
        self,
        city: str,
        query: str,
        max_price: Optional[float] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Search for hotels using ELSER
        """
        print(f"🏨 Searching hotels in {city}: '{query}'")

        try:
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"city": city}},
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
                "size": top_k
            }

            if max_price:
                search_body["query"]["bool"]["filter"] = [
                    {"range": {"price_per_night": {"lte": max_price}}}
                ]

            results = self.es.search(index="travel-hotels", body=search_body)

            hotels = []
            for hit in results['hits']['hits']:
                hotel = hit['_source']
                hotels.append({
                    "name": hotel['name'],
                    "description": hotel['description'],
                    "rating": hotel['rating'],
                    "price_per_night": hotel['price_per_night'],
                    "amenities": hotel['amenities'],
                    "suitable_for": hotel['suitable_for'],
                    "relevance_score": hit['_score']
                })

            return {
                "success": True,
                "count": len(hotels),
                "hotels": hotels
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def execute_tool(self, tool_name: str, tool_input: Dict) -> Dict[str, Any]:
        """
        Execute a tool by name (MCP protocol entry point)
        """
        if tool_name == "search_destinations":
            return self.search_destinations(**tool_input)
        elif tool_name == "search_activities":
            return self.search_activities(**tool_input)
        elif tool_name == "search_hotels":
            return self.search_hotels(**tool_input)
        elif tool_name == "search_flights":
            # Will integrate Strands API
            return {"success": False, "error": "Strands API integration pending"}
        elif tool_name == "compare_deals":
            return {"success": False, "error": "Not implemented yet"}
        elif tool_name == "create_itinerary":
            return {"success": False, "error": "Not implemented yet"}
        elif tool_name == "send_notification":
            return {"success": False, "error": "Not implemented yet"}
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }


# Test the tools
if __name__ == '__main__':
    tools = TravelMCPTools()

    print("="*60)
    print("Testing MCP Travel Tools")
    print("="*60)

    # Test 1: Search destinations
    print("\n1. Testing destination search...")
    result = tools.search_destinations(
        query="vibrant city with amazing food and technology",
        budget_level="medium",
        top_k=2
    )
    print(f"Found {result['count']} destinations")
    for dest in result['destinations']:
        print(f"  • {dest['name']}, {dest['country']} (score: {dest['relevance_score']:.2f})")

    # Test 2: Search activities
    print("\n2. Testing activity search...")
    result = tools.search_activities(
        city="Tokyo",
        query="interactive technology experience for families",
        top_k=2
    )
    print(f"Found {result['count']} activities")
    for act in result['activities']:
        print(f"  • {act['name']} (score: {act['relevance_score']:.2f})")

    # Test 3: Search hotels
    print("\n3. Testing hotel search...")
    result = tools.search_hotels(
        city="Tokyo",
        query="luxury hotel with amazing views",
        max_price=500,
        top_k=2
    )
    print(f"Found {result['count']} hotels")
    for hotel in result['hotels']:
        print(f"  • {hotel['name']} - ${hotel['price_per_night']}/night")

    print("\n✅ MCP Tools Test Complete!")
