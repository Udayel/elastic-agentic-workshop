#!/usr/bin/env python3
"""
Test ELSER semantic search with various examples
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

def search_with_elser(index_name, query_text, top_k=3):
    """
    Perform ELSER semantic search
    """
    print(f"\n{'='*60}")
    print(f"🔍 Query: '{query_text}'")
    print(f"{'='*60}")

    # ELSER search query
    search_body = {
        "query": {
            "text_expansion": {
                "description_embedding": {
                    "model_id": ".elser_model_2",
                    "model_text": query_text
                }
            }
        },
        "size": top_k,
        "_source": ["name", "description", "city", "tags", "rating"]
    }

    results = es.search(index=index_name, body=search_body)

    print(f"\nFound {results['hits']['total']['value']} results:\n")

    for i, hit in enumerate(results['hits']['hits'], 1):
        score = hit['_score']
        source = hit['_source']

        print(f"{i}. {source.get('name', 'N/A')} (Score: {score:.2f})")
        if 'city' in source:
            print(f"   City: {source['city']}")
        if 'rating' in source:
            print(f"   Rating: {source['rating']}/5.0")
        print(f"   {source['description'][:150]}...")
        if 'tags' in source:
            print(f"   Tags: {', '.join(source['tags'][:5])}")
        print()

def test_semantic_understanding():
    """
    Test ELSER's semantic understanding
    """
    print("\n" + "="*60)
    print("TEST 1: Semantic Understanding")
    print("="*60)
    print("Query uses different words than document content")

    # Query for "romantic dinner" - should find Paris restaurants
    search_with_elser(
        "travel-cities",
        "romantic dinner spot with sunset views",
        top_k=3
    )

def test_cross_lingual():
    """
    Test cross-lingual capabilities
    """
    print("\n" + "="*60)
    print("TEST 2: Cross-Lingual Search")
    print("="*60)
    print("Searching in Spanish for content in English")

    # Search in Spanish
    search_with_elser(
        "travel-activities",
        "museo de arte interactivo",  # Interactive art museum
        top_k=2
    )

    print("\n" + "-"*60)
    print("Searching in Japanese for content in English")

    # Search in Japanese
    search_with_elser(
        "travel-cities",
        "技術と食文化",  # Technology and food culture
        top_k=2
    )

def test_intent_understanding():
    """
    Test understanding of user intent
    """
    print("\n" + "="*60)
    print("TEST 3: Intent Understanding")
    print("="*60)
    print("Query describes desired experience, not specific keywords")

    # Vague query about experience
    search_with_elser(
        "travel-activities",
        "something fun for kids who love technology",
        top_k=3
    )

def test_context_awareness():
    """
    Test contextual understanding
    """
    print("\n" + "="*60)
    print("TEST 4: Context Awareness")
    print("="*60)
    print("Understanding 'hidden gems' and 'off-the-beaten-path'")

    search_with_elser(
        "travel-cities",
        "hidden gems and local experiences, not touristy",
        top_k=3
    )

def compare_with_traditional():
    """
    Compare ELSER with traditional keyword search
    """
    print("\n" + "="*60)
    print("TEST 5: ELSER vs Traditional Search Comparison")
    print("="*60)

    query = "luxury beach relaxation"

    print(f"Query: '{query}'")
    print("\n--- Traditional Keyword Search (BM25) ---")

    # Traditional search
    traditional_results = es.search(
        index="travel-hotels",
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "description"]
                }
            },
            "size": 2
        }
    )

    for i, hit in enumerate(traditional_results['hits']['hits'], 1):
        print(f"{i}. {hit['_source']['name']} (Score: {hit['_score']:.2f})")

    print("\n--- ELSER Semantic Search ---")

    # ELSER search
    search_with_elser("travel-hotels", query, top_k=2)

def test_compound_concepts():
    """
    Test understanding of compound concepts
    """
    print("\n" + "="*60)
    print("TEST 6: Compound Concepts")
    print("="*60)
    print("Understanding complex multi-faceted queries")

    search_with_elser(
        "travel-cities",
        "destination for tech-savvy foodies who appreciate modern design",
        top_k=3
    )

def main():
    print("="*60)
    print("ELSER Semantic Search Demonstration")
    print("="*60)
    print("\nThis demo shows ELSER's capabilities:")
    print("• Semantic understanding (beyond keywords)")
    print("• Cross-lingual search (any language)")
    print("• Intent recognition")
    print("• Context awareness")
    print("• Complex query handling")

    # Run tests
    test_semantic_understanding()
    test_cross_lingual()
    test_intent_understanding()
    test_context_awareness()
    compare_with_traditional()
    test_compound_concepts()

    print("\n" + "="*60)
    print("✅ ELSER Demo Complete!")
    print("="*60)
    print("\nKey Takeaways:")
    print("• ELSER understands meaning, not just keywords")
    print("• Works across languages automatically")
    print("• Captures user intent from natural language")
    print("• No training data or fine-tuning needed")
    print("• Runs entirely within Elasticsearch")

if __name__ == '__main__':
    main()
