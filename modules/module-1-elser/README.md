# Module 1: ELSER Semantic Search & MCP Tools

## Overview

In this module, you'll master Elastic's ELSER (Elastic Learned Sparse EncodeR) for semantic search and integrate it with Model Context Protocol (MCP) tools for powerful agent capabilities.

**Time to Complete**: 40 minutes

---

## What You'll Learn

- ✅ How ELSER enables zero-shot semantic search
- ✅ Cross-lingual search capabilities
- ✅ Building a travel knowledge base with ELSER
- ✅ Integrating MCP tools for agent capabilities
- ✅ Creating custom MCP servers for travel data
- ✅ Performance optimization techniques

---

## Prerequisites

- Completed [Module 0: Setup](../module-0-setup/)
- Elastic Cloud with ELSER deployed
- Python environment configured

---

## What is ELSER?

ELSER (Elastic Learned Sparse EncodeR) is Elastic's trained semantic search model that:

- **Zero-shot learning**: No training data required
- **Cross-lingual**: Search in English, find results in any language
- **Domain-adaptive**: Understands context and intent
- **Real-time**: No batch processing needed
- **Privacy-first**: Runs entirely within your Elastic cluster

### ELSER vs Traditional Embeddings

| Feature | Traditional Embeddings | ELSER |
|---------|----------------------|--------|
| Training data needed | ✅ Yes | ❌ No (zero-shot) |
| Cross-lingual | ❌ Limited | ✅ Native |
| Domain adaptation | ❌ Requires fine-tuning | ✅ Automatic |
| Deployment | External API | Built into Elastic |
| Privacy | Data leaves cluster | Data stays in cluster |
| Cost | Per-token API fees | Included in Elastic |

---

## What is MCP (Model Context Protocol)?

MCP is an open protocol that standardizes how AI assistants access external data and tools:

```
┌─────────────────────────────────────────────────┐
│              AI Agent (Claude)                  │
└────────────────┬────────────────────────────────┘
                 │ MCP Protocol
┌────────────────▼────────────────────────────────┐
│          MCP Server (Travel Tools)              │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │  Search  │  │  Hotels  │  │  Activities  │ │
│  │   Tool   │  │   Tool   │  │    Tool      │ │
│  └────┬─────┘  └────┬─────┘  └─────┬────────┘ │
│       │             │               │          │
└───────┼─────────────┼───────────────┼──────────┘
        │             │               │
┌───────▼─────────────▼───────────────▼──────────┐
│          Elastic Cloud (ELSER + Data)          │
└─────────────────────────────────────────────────┘
```

### Why MCP?

- **Standardized**: One protocol for all tools
- **Secure**: Built-in authentication and authorization
- **Extensible**: Easy to add new capabilities
- **Interoperable**: Works with any MCP-compatible AI

---

## Step 1: Create Travel Knowledge Base

### 1.1 Understand the Data Schema

We'll index three types of travel data:

**1. Cities/Destinations**
```json
{
  "name": "Tokyo",
  "country": "Japan",
  "description": "Vibrant metropolis blending ultra-modern and traditional...",
  "best_season": ["spring", "autumn"],
  "highlights": ["Shibuya Crossing", "Temples", "Cherry Blossoms"],
  "budget_level": "medium",
  "tags": ["technology", "food", "culture", "shopping"]
}
```

**2. Activities**
```json
{
  "name": "teamLab Borderless",
  "city": "Tokyo",
  "description": "Immersive digital art museum with interactive exhibits...",
  "category": "museum",
  "duration_hours": 2,
  "price_range": "$$",
  "suitable_for": ["families", "couples", "photography"],
  "tags": ["technology", "art", "interactive"]
}
```

**3. Hotels/Accommodations**
```json
{
  "name": "Park Hyatt Tokyo",
  "city": "Tokyo",
  "description": "Luxury hotel with stunning city views...",
  "rating": 4.8,
  "price_per_night": 350,
  "amenities": ["pool", "spa", "gym", "restaurant"],
  "suitable_for": ["business", "couples", "luxury"]
}
```

### 1.2 Create ELSER-Optimized Indexes

Create `create_indexes.py`:

```python
#!/usr/bin/env python3
"""
Create Elasticsearch indexes optimized for ELSER semantic search
"""

import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

# Connect to Elastic
es = Elasticsearch(
    cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
    basic_auth=(os.getenv('ELASTIC_USERNAME'), os.getenv('ELASTIC_PASSWORD'))
)

def create_cities_index():
    """Create cities index with ELSER"""
    
    index_name = "travel-cities"
    
    # Delete if exists
    if es.indices.exists(index=index_name):
        print(f"Deleting existing index: {index_name}")
        es.indices.delete(index=index_name)
    
    # Create index with ELSER inference pipeline
    print(f"Creating index: {index_name}")
    
    # Index mapping
    mappings = {
        "properties": {
            "name": {"type": "keyword"},
            "country": {"type": "keyword"},
            "description": {"type": "text"},
            "description_embedding": {
                "type": "sparse_vector"
            },
            "best_season": {"type": "keyword"},
            "highlights": {"type": "text"},
            "budget_level": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "coordinates": {"type": "geo_point"}
        }
    }
    
    es.indices.create(index=index_name, mappings=mappings)
    
    # Create ingest pipeline for ELSER
    pipeline_name = f"{index_name}-elser-pipeline"
    
    es.ingest.put_pipeline(
        id=pipeline_name,
        description="ELSER pipeline for travel cities",
        processors=[
            {
                "inference": {
                    "model_id": ".elser_model_2",
                    "input_output": {
                        "input_field": "description",
                        "output_field": "description_embedding"
                    }
                }
            }
        ]
    )
    
    print(f"✓ Created index: {index_name}")
    print(f"✓ Created pipeline: {pipeline_name}")
    
    return index_name, pipeline_name

def create_activities_index():
    """Create activities index with ELSER"""
    
    index_name = "travel-activities"
    
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    
    mappings = {
        "properties": {
            "name": {"type": "text"},
            "city": {"type": "keyword"},
            "description": {"type": "text"},
            "description_embedding": {
                "type": "sparse_vector"
            },
            "category": {"type": "keyword"},
            "duration_hours": {"type": "float"},
            "price_range": {"type": "keyword"},
            "suitable_for": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "coordinates": {"type": "geo_point"},
            "rating": {"type": "float"}
        }
    }
    
    es.indices.create(index=index_name, mappings=mappings)
    
    # Create ELSER pipeline
    pipeline_name = f"{index_name}-elser-pipeline"
    
    es.ingest.put_pipeline(
        id=pipeline_name,
        processors=[
            {
                "inference": {
                    "model_id": ".elser_model_2",
                    "input_output": {
                        "input_field": "description",
                        "output_field": "description_embedding"
                    }
                }
            }
        ]
    )
    
    print(f"✓ Created index: {index_name}")
    print(f"✓ Created pipeline: {pipeline_name}")
    
    return index_name, pipeline_name

def create_hotels_index():
    """Create hotels index with ELSER"""
    
    index_name = "travel-hotels"
    
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    
    mappings = {
        "properties": {
            "name": {"type": "text"},
            "city": {"type": "keyword"},
            "description": {"type": "text"},
            "description_embedding": {
                "type": "sparse_vector"
            },
            "rating": {"type": "float"},
            "price_per_night": {"type": "integer"},
            "amenities": {"type": "keyword"},
            "suitable_for": {"type": "keyword"},
            "coordinates": {"type": "geo_point"}
        }
    }
    
    es.indices.create(index=index_name, mappings=mappings)
    
    # Create ELSER pipeline
    pipeline_name = f"{index_name}-elser-pipeline"
    
    es.ingest.put_pipeline(
        id=pipeline_name,
        processors=[
            {
                "inference": {
                    "model_id": ".elser_model_2",
                    "input_output": {
                        "input_field": "description",
                        "output_field": "description_embedding"
                    }
                }
            }
        ]
    )
    
    print(f"✓ Created index: {index_name}")
    print(f"✓ Created pipeline: {pipeline_name}")
    
    return index_name, pipeline_name

def main():
    print("=" * 60)
    print("Creating ELSER-Optimized Travel Indexes")
    print("=" * 60)
    print()
    
    create_cities_index()
    print()
    
    create_activities_index()
    print()
    
    create_hotels_index()
    print()
    
    print("=" * 60)
    print("✅ All indexes created successfully!")
    print()
    print("Next: Load sample data")
    print("  python3 load_sample_data.py")
    print("=" * 60)

if __name__ == '__main__':
    main()
```

### 1.3 Run Index Creation

```bash
chmod +x create_indexes.py
python3 create_indexes.py
```

Expected output:
```
============================================================
Creating ELSER-Optimized Travel Indexes
============================================================

Deleting existing index: travel-cities
Creating index: travel-cities
✓ Created index: travel-cities
✓ Created pipeline: travel-cities-elser-pipeline

✓ Created index: travel-activities
✓ Created pipeline: travel-activities-elser-pipeline

✓ Created index: travel-hotels
✓ Created pipeline: travel-hotels-elser-pipeline

============================================================
✅ All indexes created successfully!

Next: Load sample data
  python3 load_sample_data.py
============================================================
```

✅ **Checkpoint**: Indexes created with ELSER pipelines!

---

## Step 2: Load Sample Travel Data

### 2.1 Download Sample Dataset

```bash
# Create data directory
mkdir -p ../../data

# Download sample data
curl -o ../../data/travel-data.json \
  https://raw.githubusercontent.com/elastic/travel-agent-workshop/main/data/travel-data.json
```

**Or create manually** - create `../../data/travel-data.json`:

```json
{
  "cities": [
    {
      "name": "Tokyo",
      "country": "Japan",
      "description": "Tokyo is a vibrant metropolis that seamlessly blends ultra-modern technology with traditional Japanese culture. From the neon-lit streets of Shibuya and the serene temples of Asakusa to world-class dining and cutting-edge electronics, Tokyo offers an unforgettable experience for technology enthusiasts and culture lovers alike.",
      "best_season": ["spring", "autumn"],
      "highlights": ["Shibuya Crossing", "Senso-ji Temple", "Tokyo Skytree", "Tsukiji Market"],
      "budget_level": "medium",
      "tags": ["technology", "food", "culture", "shopping", "modern"],
      "coordinates": {"lat": 35.6762, "lon": 139.6503}
    },
    {
      "name": "Paris",
      "country": "France",
      "description": "Paris, the City of Light, is renowned for its art, fashion, gastronomy, and culture. Home to iconic landmarks like the Eiffel Tower and Louvre Museum, Paris exudes romance with its charming cafes, elegant boulevards, and world-famous cuisine. Perfect for art lovers, history buffs, and anyone seeking a romantic getaway.",
      "best_season": ["spring", "autumn"],
      "highlights": ["Eiffel Tower", "Louvre Museum", "Notre-Dame", "Champs-Élysées"],
      "budget_level": "high",
      "tags": ["art", "culture", "romance", "food", "history"],
      "coordinates": {"lat": 48.8566, "lon": 2.3522}
    },
    {
      "name": "Bali",
      "country": "Indonesia",
      "description": "Bali is a tropical paradise known for its stunning beaches, lush rice terraces, ancient temples, and vibrant culture. Whether you're seeking relaxation at luxury beach resorts, adventure through jungle treks, or spiritual experiences at sacred temples, Bali offers the perfect blend of natural beauty and cultural richness.",
      "best_season": ["summer", "autumn"],
      "highlights": ["Ubud Rice Terraces", "Tanah Lot Temple", "Seminy Beach", "Sacred Monkey Forest"],
      "budget_level": "low",
      "tags": ["beach", "nature", "relaxation", "temples", "adventure"],
      "coordinates": {"lat": -8.3405, "lon": 115.0920}
    }
  ],
  "activities": [
    {
      "name": "teamLab Borderless Digital Art Museum",
      "city": "Tokyo",
      "description": "An immersive digital art museum where technology meets creativity. Walk through stunning interactive installations that respond to your presence, creating a unique experience every time. Perfect for families, photography enthusiasts, and anyone who loves cutting-edge technology and art.",
      "category": "museum",
      "duration_hours": 2.5,
      "price_range": "$$",
      "suitable_for": ["families", "couples", "photography", "technology"],
      "tags": ["technology", "art", "interactive", "instagram-worthy"],
      "coordinates": {"lat": 35.6246, "lon": 139.7778},
      "rating": 4.8
    },
    {
      "name": "Tsukiji Outer Market Food Tour",
      "city": "Tokyo",
      "description": "Experience the authentic flavors of Tokyo at the famous Tsukiji Outer Market. Sample fresh sushi, traditional Japanese street food, and local delicacies while learning about Japanese culinary traditions from expert guides. A must-do for food lovers!",
      "category": "food_tour",
      "duration_hours": 3,
      "price_range": "$$$",
      "suitable_for": ["food_lovers", "families", "groups"],
      "tags": ["food", "authentic", "local_experience", "sushi"],
      "coordinates": {"lat": 35.6654, "lon": 139.7707},
      "rating": 4.9
    },
    {
      "name": "Louvre Museum Guided Tour",
      "city": "Paris",
      "description": "Explore the world's largest art museum with an expert guide who brings history and art to life. See masterpieces including the Mona Lisa, Venus de Milo, and Winged Victory. Skip-the-line access ensures you maximize your time admiring incredible art rather than waiting in queues.",
      "category": "museum",
      "duration_hours": 3.5,
      "price_range": "$$$",
      "suitable_for": ["art_lovers", "history_buffs", "photographers"],
      "tags": ["art", "history", "culture", "iconic"],
      "coordinates": {"lat": 48.8606, "lon": 2.3376},
      "rating": 4.7
    }
  ],
  "hotels": [
    {
      "name": "Park Hyatt Tokyo",
      "city": "Tokyo",
      "description": "Luxury hotel offering stunning panoramic city views from its location in Shinjuku skyscraper. Features elegant rooms, world-class dining including the New York Bar made famous by 'Lost in Translation', and exceptional service. Perfect for business travelers and luxury seekers.",
      "rating": 4.8,
      "price_per_night": 450,
      "amenities": ["pool", "spa", "gym", "restaurant", "bar", "city_views"],
      "suitable_for": ["business", "luxury", "couples"],
      "coordinates": {"lat": 35.6850, "lon": 139.6917}
    },
    {
      "name": "Hôtel Plaza Athénée",
      "city": "Paris",
      "description": "Iconic palace hotel on Avenue Montaigne embodying Parisian elegance and luxury. Featuring haute couture décor, Michelin-starred dining, and impeccable service. Steps from the Eiffel Tower and Champs-Élysées, it's the epitome of a romantic Paris experience.",
      "rating": 4.9,
      "price_per_night": 1200,
      "amenities": ["spa", "michelin_restaurant", "concierge", "romantic"],
      "suitable_for": ["luxury", "romance", "special_occasions"],
      "coordinates": {"lat": 48.8661, "lon": 2.3042}
    },
    {
      "name": "Alila Villas Uluwatu",
      "city": "Bali",
      "description": "Stunning clifftop resort overlooking the Indian Ocean. Contemporary design meets Balinese hospitality with private villas, infinity pools, and spectacular sunset views. Ideal for honeymooners and those seeking a luxurious tropical escape.",
      "rating": 4.9,
      "price_per_night": 350,
      "amenities": ["pool", "spa", "beach_access", "restaurant", "ocean_view"],
      "suitable_for": ["honeymoon", "luxury", "relaxation"],
      "coordinates": {"lat": -8.8290, "lon": 115.0846}
    }
  ]
}
```

### 2.2 Create Data Loader Script

Create `load_sample_data.py`:

```python
#!/usr/bin/env python3
"""
Load sample travel data with ELSER embeddings
"""

import os
import json
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

load_dotenv()

# Connect to Elastic
es = Elasticsearch(
    cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
    basic_auth=(os.getenv('ELASTIC_USERNAME'), os.getenv('ELASTIC_PASSWORD'))
)

def load_data(index_name, pipeline_name, documents):
    """Load documents with ELSER pipeline"""
    
    print(f"Loading {len(documents)} documents into {index_name}...")
    
    actions = []
    for doc in documents:
        actions.append({
            "_index": index_name,
            "_source": doc,
            "pipeline": pipeline_name
        })
    
    # Bulk index
    success, failed = bulk(es, actions, raise_on_error=False)
    
    print(f"  ✓ Indexed: {success} documents")
    if failed:
        print(f"  ✗ Failed: {len(failed)} documents")
    
    # Refresh index
    es.indices.refresh(index=index_name)
    
    return success

def main():
    print("=" * 60)
    print("Loading Sample Travel Data with ELSER")
    print("=" * 60)
    print()
    
    # Load data file
    with open('../../data/travel-data.json', 'r') as f:
        data = json.load(f)
    
    # Load cities
    load_data(
        "travel-cities",
        "travel-cities-elser-pipeline",
        data['cities']
    )
    print()
    
    # Load activities
    load_data(
        "travel-activities",
        "travel-activities-elser-pipeline",
        data['activities']
    )
    print()
    
    # Load hotels
    load_data(
        "travel-hotels",
        "travel-hotels-elser-pipeline",
        data['hotels']
    )
    print()
    
    print("=" * 60)
    print("✅ All data loaded successfully!")
    print()
    print("Next: Test ELSER semantic search")
    print("  python3 test_elser_search.py")
    print("=" * 60)

if __name__ == '__main__':
    main()
```

### 2.3 Load the Data

```bash
chmod +x load_sample_data.py
python3 load_sample_data.py
```

Expected output:
```
============================================================
Loading Sample Travel Data with ELSER
============================================================

Loading 3 documents into travel-cities...
  ✓ Indexed: 3 documents

Loading 3 documents into travel-activities...
  ✓ Indexed: 3 documents

Loading 3 documents into travel-hotels...
  ✓ Indexed: 3 documents

============================================================
✅ All data loaded successfully!

Next: Test ELSER semantic search
  python3 test_elser_search.py
============================================================
```

✅ **Checkpoint**: Sample data loaded with ELSER embeddings!

---

I'll continue with Step 3 and the MCP integration. Would you like me to continue with the complete module including:
- ELSER semantic search examples
- Cross-lingual search demonstrations  
- MCP server implementation for travel tools
- Performance comparisons
- Integration with Claude agents

Let me know if you want me to continue building out this comprehensive module!