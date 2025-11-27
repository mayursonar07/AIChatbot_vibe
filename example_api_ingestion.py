#!/usr/bin/env python3
"""
Example: How to ingest data into RAG system via API
This allows programmatic updates to the knowledge base without file uploads
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def ingest_text_data(content: str, document_name: str, metadata: dict = None):
    """
    Ingest raw text or JSON data into the RAG system
    
    Args:
        content: Text content or JSON string to ingest
        document_name: Name identifier for this document
        metadata: Optional metadata (source, category, etc.)
    
    Returns:
        Response dict with success status and details
    """
    url = f"{API_BASE_URL}/api/ingest"
    
    payload = {
        "content": content,
        "document_name": document_name,
        "metadata": metadata or {}
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()


def check_knowledge_base_stats():
    """Check how many chunks are in the vector store"""
    url = f"{API_BASE_URL}/api/stats"
    response = requests.get(url)
    return response.json()


def query_rag(message: str, use_rag: bool = True):
    """Query the RAG system"""
    url = f"{API_BASE_URL}/api/chat"
    
    payload = {
        "message": message,
        "session_id": "api_test_session",
        "use_rag": use_rag
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()


# Example 1: Ingest simple text
def example_text_ingestion():
    print("=" * 60)
    print("Example 1: Ingesting Simple Text")
    print("=" * 60)
    
    content = """
Investment Portfolio Guidelines:

Risk Tolerance Levels:
- Conservative: 70% bonds, 30% stocks
- Moderate: 50% bonds, 50% stocks  
- Aggressive: 30% bonds, 70% stocks

Diversification is key to managing risk across asset classes.
    """
    
    result = ingest_text_data(
        content=content,
        document_name="investment_guidelines",
        metadata={
            "source": "api_example",
            "category": "investment_domain",
            "type": "guidelines"
        }
    )
    
    print(f"✅ Success: {result['success']}")
    print(f"📄 Document ID: {result['file_id']}")
    print(f"📊 Chunks created: {result['chunks_created']}")
    print()


# Example 2: Ingest structured JSON entities
def example_json_ingestion():
    print("=" * 60)
    print("Example 2: Ingesting Structured JSON")
    print("=" * 60)
    
    entities = {
        "entities": [
            {
                "name": "Goldman Sachs",
                "shortCode": "GS",
                "category": "Financial Services",
                "sector": "Investment Banking"
            },
            {
                "name": "Berkshire Hathaway",
                "shortCode": "BRK.B",
                "category": "Conglomerate",
                "sector": "Diversified Holdings"
            }
        ]
    }
    
    # Convert dict to JSON string for content
    content = json.dumps(entities, indent=2)
    
    result = ingest_text_data(
        content=content,
        document_name="financial_entities",
        metadata={
            "source": "api_example",
            "category": "investment_domain",
            "type": "structured_entities",
            "version": "1.0"
        }
    )
    
    print(f"✅ Success: {result['success']}")
    print(f"📄 Document ID: {result['file_id']}")
    print(f"📊 Chunks created: {result['chunks_created']}")
    print()


# Example 3: Query the RAG system
def example_query():
    print("=" * 60)
    print("Example 3: Querying RAG System")
    print("=" * 60)
    
    # Check stats first
    stats = check_knowledge_base_stats()
    print(f"📊 Vector Store Status: {stats['status']}")
    print(f"📚 Total Chunks: {stats['total_chunks']}\n")
    
    # Query the system
    question = "What is the recommended portfolio allocation for moderate risk tolerance?"
    print(f"❓ Question: {question}\n")
    
    result = query_rag(question)
    
    print(f"💬 Answer: {result['response']}\n")
    
    if result.get('sources'):
        print(f"📎 Sources: {len(result['sources'])} documents")
        for i, source in enumerate(result['sources'], 1):
            print(f"  {i}. {source['filename']} (score: {source['relevance_score']})")
    print()


# Example 4: Batch ingestion
def example_batch_ingestion():
    print("=" * 60)
    print("Example 4: Batch Ingestion")
    print("=" * 60)
    
    documents = [
        {
            "content": "Equity markets represent ownership in companies. Common types include large-cap, mid-cap, and small-cap stocks.",
            "document_name": "equity_basics",
            "metadata": {"category": "education", "topic": "equities"}
        },
        {
            "content": "Fixed income securities include bonds, treasury notes, and corporate debt instruments.",
            "document_name": "fixed_income_basics",
            "metadata": {"category": "education", "topic": "bonds"}
        },
        {
            "content": "Alternative investments include real estate, commodities, hedge funds, and private equity.",
            "document_name": "alternative_investments",
            "metadata": {"category": "education", "topic": "alternatives"}
        }
    ]
    
    for doc in documents:
        result = ingest_text_data(**doc)
        print(f"✅ Ingested: {doc['document_name']} ({result['chunks_created']} chunks)")
    
    print()


if __name__ == "__main__":
    try:
        print("\n🚀 RAG API Ingestion Examples\n")
        
        # Run examples
        example_text_ingestion()
        example_json_ingestion()
        example_batch_ingestion()
        example_query()
        
        print("✨ All examples completed successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
