#!/usr/bin/env python3
"""
Test script to verify methodology question detection
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_chat_endpoint(message, session_id):
    """Test the chat endpoint"""
    url = f"{API_BASE}/api/chat"
    payload = {
        "message": message,
        "session_id": session_id,
        "use_rag": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("response", ""), result.get("sources", [])
    except Exception as e:
        return f"Error: {e}", []

def main():
    # Wait for backend to be ready
    print("Waiting for backend to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{API_BASE}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!\n")
                break
        except:
            pass
        time.sleep(2)
    else:
        print("❌ Backend not ready after 20 seconds\n")
        return
    
    # Test 1: With typo "wnsure"
    print("=" * 70)
    print("Test 1: How do you wnsure that these entities are from investment domains?")
    print("=" * 70)
    response, sources = test_chat_endpoint(
        "How do you wnsure that these entities are from investment domains?",
        "test_session_1"
    )
    print(f"Response length: {len(response)} chars")
    print(f"Number of sources: {len(sources)}")
    print(f"First 200 chars: {response[:200]}...")
    print()
    
    # Test 2: Without "how" but with ensure + domain + entity
    print("=" * 70)
    print("Test 2: Ensure these entities are from investment domain")
    print("=" * 70)
    response, sources = test_chat_endpoint(
        "Ensure these entities are from investment domain",
        "test_session_2"
    )
    print(f"Response length: {len(response)} chars")
    print(f"Number of sources: {len(sources)}")
    print(f"First 200 chars: {response[:200]}...")
    print()
    
    # Test 3: Regular entity query (should work normally)
    print("=" * 70)
    print("Test 3: Show me custodian entities (should return actual entities)")
    print("=" * 70)
    response, sources = test_chat_endpoint(
        "Show me custodian entities",
        "test_session_3"
    )
    print(f"Response length: {len(response)} chars")
    print(f"Number of sources: {len(sources)}")
    print(f"First 200 chars: {response[:200]}...")
    print()
    
    # Test 4: Another methodology variant
    print("=" * 70)
    print("Test 4: How can you verify entities belong to investment domain?")
    print("=" * 70)
    response, sources = test_chat_endpoint(
        "How can you verify entities belong to investment domain?",
        "test_session_4"
    )
    print(f"Response length: {len(response)} chars")
    print(f"Number of sources: {len(sources)}")
    print(f"First 200 chars: {response[:200]}...")

if __name__ == "__main__":
    main()
