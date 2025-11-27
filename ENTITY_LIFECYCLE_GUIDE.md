# Entity Lifecycle Management - Complete Guide

## 🔄 Overview

Prevent stale data in your RAG system with **full entity lifecycle management**. You can now CREATE, UPDATE, and DELETE individual documents to keep your knowledge base perfectly synchronized with your source systems.

## ⚠️ The Problem

**Without lifecycle management:**
- Entities get updated in your database, but old embeddings remain
- Deleted entities still appear in AI responses
- Multiple versions of the same entity cause confusion
- Manual cleanup required to keep data fresh

**With lifecycle management:**
- ✅ Entities stay synchronized with your source
- ✅ Updates automatically refresh embeddings
- ✅ Deletions remove all traces
- ✅ No stale data = accurate AI responses

## 🎯 Three Operations

| Operation | Method | Endpoint | Purpose |
|-----------|--------|----------|---------|
| **CREATE** | POST | `/api/ingest` | Add new entity |
| **UPDATE** | PUT | `/api/document/{id}` | Modify existing entity |
| **DELETE** | DELETE | `/api/document/{id}` | Remove entity |

---

## 📝 1. CREATE (Ingest New Entity)

### API Call
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Apple Inc. (AAPL) - Technology company",
    "document_name": "apple_entity",
    "metadata": {"source": "database", "entity_id": "123"}
  }'
```

### Response
```json
{
  "success": true,
  "message": "Successfully ingested apple_entity",
  "file_id": "uuid-here",  // ⭐ Save this ID!
  "filename": "apple_entity",
  "chunks_created": 1
}
```

### Python Example
```python
import requests

def create_entity(entity_data):
    response = requests.post("http://localhost:8000/api/ingest", json={
        "content": entity_data["description"],
        "document_name": f"entity_{entity_data['id']}",
        "metadata": {
            "source": "database",
            "entity_id": str(entity_data["id"]),
            "created_at": entity_data["created_at"]
        }
    })
    
    result = response.json()
    # Store this document_id in your database!
    return result["file_id"]

# Usage
entity = {
    "id": 123,
    "name": "Apple Inc.",
    "ticker": "AAPL",
    "description": "Apple Inc. (AAPL) - Technology company...",
    "created_at": "2024-11-25T10:00:00Z"
}

document_id = create_entity(entity)
# Save document_id to your database for future updates/deletes!
```

---

## 🔄 2. UPDATE (Modify Existing Entity)

When an entity changes in your system, update its embeddings:

### API Call
```bash
curl -X PUT http://localhost:8000/api/document/{document_id} \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "uuid-here",
    "content": "Apple Inc. (AAPL) - Technology company. NEW: Vision Pro launched!",
    "document_name": "apple_entity",
    "metadata": {"source": "database", "version": "2.0"}
  }'
```

### Response
```json
{
  "success": true,
  "message": "Successfully updated apple_entity",
  "file_id": "same-uuid",  // Same ID preserved
  "filename": "apple_entity",
  "chunks_created": 1  // New chunks replace old ones
}
```

### Python Example
```python
def update_entity(document_id, updated_entity_data):
    """Update entity when it changes in your database"""
    response = requests.put(
        f"http://localhost:8000/api/document/{document_id}",
        json={
            "document_id": document_id,
            "content": updated_entity_data["description"],
            "document_name": f"entity_{updated_entity_data['id']}",
            "metadata": {
                "source": "database",
                "entity_id": str(updated_entity_data["id"]),
                "updated_at": updated_entity_data["updated_at"],
                "version": "2.0"
            }
        }
    )
    return response.json()

# Usage - triggered by database update
updated_entity = {
    "id": 123,
    "name": "Apple Inc.",
    "ticker": "AAPL",
    "description": "Apple Inc. (AAPL) - Technology company. Products: iPhone, iPad, Mac, Vision Pro (NEW)",
    "updated_at": "2024-11-25T15:00:00Z"
}

result = update_entity(document_id, updated_entity)
print(f"Updated: {result['chunks_created']} new chunks")
```

### What Happens During Update
1. ✅ Old chunks are deleted from vector store
2. ✅ New content is chunked and embedded
3. ✅ Same document_id is preserved
4. ✅ Metadata is updated/merged
5. ✅ No orphaned data remains

---

## 🗑️ 3. DELETE (Remove Entity)

When an entity is deleted from your system, remove it from RAG:

### API Call
```bash
curl -X DELETE http://localhost:8000/api/document/{document_id}
```

### Response
```json
{
  "success": true,
  "message": "Successfully deleted apple_entity",
  "document_id": "uuid-here",
  "chunks_deleted": 1  // All chunks removed
}
```

### Python Example
```python
def delete_entity(document_id):
    """Delete entity from RAG when removed from database"""
    response = requests.delete(
        f"http://localhost:8000/api/document/{document_id}"
    )
    return response.json()

# Usage - triggered by database deletion
result = delete_entity(document_id)
print(f"Deleted {result['chunks_deleted']} chunks")
```

---

## 🔗 Database Integration Patterns

### Pattern 1: Store document_id in Your Database

**Recommended approach** - Track document_id alongside your entity:

```sql
-- Add column to your entities table
ALTER TABLE entities ADD COLUMN rag_document_id VARCHAR(255);

-- When creating entity
INSERT INTO entities (name, ticker, description, rag_document_id)
VALUES ('Apple', 'AAPL', '...', 'uuid-from-rag-api');

-- When updating entity
UPDATE entities SET description = '...updated...' WHERE id = 123;
-- Then call RAG update API with rag_document_id

-- When deleting entity
DELETE FROM entities WHERE id = 123;
-- Then call RAG delete API with rag_document_id
```

### Pattern 2: Database Triggers (Automatic Sync)

```python
# PostgreSQL trigger example
from sqlalchemy import event

@event.listens_for(Entity, 'after_insert')
def create_in_rag(mapper, connection, target):
    """Automatically create RAG document when entity is inserted"""
    doc_id = requests.post("http://localhost:8000/api/ingest", json={
        "content": target.description,
        "document_name": f"entity_{target.id}",
        "metadata": {"entity_id": str(target.id)}
    }).json()["file_id"]
    
    # Update the entity record with document_id
    connection.execute(
        "UPDATE entities SET rag_document_id = %s WHERE id = %s",
        (doc_id, target.id)
    )

@event.listens_for(Entity, 'after_update')
def update_in_rag(mapper, connection, target):
    """Automatically update RAG document when entity is updated"""
    if target.rag_document_id:
        requests.put(
            f"http://localhost:8000/api/document/{target.rag_document_id}",
            json={
                "document_id": target.rag_document_id,
                "content": target.description,
                "metadata": {"entity_id": str(target.id), "updated_at": str(target.updated_at)}
            }
        )

@event.listens_for(Entity, 'after_delete')
def delete_from_rag(mapper, connection, target):
    """Automatically delete RAG document when entity is deleted"""
    if target.rag_document_id:
        requests.delete(f"http://localhost:8000/api/document/{target.rag_document_id}")
```

### Pattern 3: Webhook Handler

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook/entity-created")
async def entity_created(request: Request):
    """Handle entity creation from external system"""
    entity = await request.json()
    
    # Create in RAG
    doc_id = requests.post("http://localhost:8000/api/ingest", json={
        "content": entity["description"],
        "document_name": f"entity_{entity['id']}",
        "metadata": {"entity_id": entity["id"], "source": "webhook"}
    }).json()["file_id"]
    
    # Send document_id back to source system
    return {"document_id": doc_id}

@app.post("/webhook/entity-updated")
async def entity_updated(request: Request):
    """Handle entity updates from external system"""
    data = await request.json()
    
    # Update in RAG
    requests.put(
        f"http://localhost:8000/api/document/{data['document_id']}",
        json={
            "document_id": data["document_id"],
            "content": data["updated_description"],
            "metadata": {"entity_id": data["entity_id"], "updated_at": data["timestamp"]}
        }
    )
    
    return {"status": "updated"}

@app.post("/webhook/entity-deleted")
async def entity_deleted(request: Request):
    """Handle entity deletion from external system"""
    data = await request.json()
    
    # Delete from RAG
    requests.delete(f"http://localhost:8000/api/document/{data['document_id']}")
    
    return {"status": "deleted"}
```

### Pattern 4: Batch Synchronization (Scheduled)

```python
#!/usr/bin/env python3
# sync_entities_daily.py

import requests
from datetime import datetime, timedelta

def sync_entities():
    """Daily sync - update only changed entities"""
    
    # 1. Get entities modified in last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    modified_entities = fetch_modified_entities_since(yesterday)
    
    print(f"Found {len(modified_entities)} modified entities")
    
    for entity in modified_entities:
        if entity.get("rag_document_id"):
            # Update existing
            print(f"Updating entity {entity['id']}...")
            requests.put(
                f"http://localhost:8000/api/document/{entity['rag_document_id']}",
                json={
                    "document_id": entity["rag_document_id"],
                    "content": entity["description"],
                    "metadata": {"entity_id": str(entity["id"]), "synced_at": datetime.now().isoformat()}
                }
            )
        else:
            # Create new
            print(f"Creating entity {entity['id']}...")
            doc_id = requests.post("http://localhost:8000/api/ingest", json={
                "content": entity["description"],
                "document_name": f"entity_{entity['id']}",
                "metadata": {"entity_id": str(entity["id"])}
            }).json()["file_id"]
            
            # Save document_id
            save_document_id_to_db(entity["id"], doc_id)
    
    # 2. Handle deletions
    deleted_entity_ids = fetch_deleted_entities_since(yesterday)
    for entity_id in deleted_entity_ids:
        doc_id = get_document_id_from_db(entity_id)
        if doc_id:
            print(f"Deleting entity {entity_id}...")
            requests.delete(f"http://localhost:8000/api/document/{doc_id}")

if __name__ == "__main__":
    sync_entities()
```

**Crontab entry:**
```
0 2 * * * python3 /path/to/sync_entities_daily.py >> /var/log/entity_sync.log 2>&1
```

---

## 🎯 Complete Example: Entity CRUD

```python
import requests
from typing import Dict, Optional

class RAGEntityManager:
    """Manage entity lifecycle in RAG system"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def create(self, entity: Dict) -> str:
        """Create entity in RAG, returns document_id"""
        response = requests.post(f"{self.base_url}/api/ingest", json={
            "content": self._format_entity(entity),
            "document_name": f"entity_{entity['id']}",
            "metadata": {
                "entity_id": str(entity["id"]),
                "source": "api",
                "created_at": entity.get("created_at", "")
            }
        })
        response.raise_for_status()
        return response.json()["file_id"]
    
    def update(self, document_id: str, entity: Dict) -> bool:
        """Update entity in RAG"""
        response = requests.put(
            f"{self.base_url}/api/document/{document_id}",
            json={
                "document_id": document_id,
                "content": self._format_entity(entity),
                "document_name": f"entity_{entity['id']}",
                "metadata": {
                    "entity_id": str(entity["id"]),
                    "updated_at": entity.get("updated_at", ""),
                    "version": entity.get("version", "1.0")
                }
            }
        )
        response.raise_for_status()
        return response.json()["success"]
    
    def delete(self, document_id: str) -> bool:
        """Delete entity from RAG"""
        response = requests.delete(f"{self.base_url}/api/document/{document_id}")
        response.raise_for_status()
        return response.json()["success"]
    
    def _format_entity(self, entity: Dict) -> str:
        """Format entity data as text for embedding"""
        return f"""
Entity: {entity['name']}
Short Code: {entity.get('ticker', 'N/A')}
Category: {entity.get('category', 'N/A')}
Description: {entity.get('description', '')}
"""

# Usage
manager = RAGEntityManager()

# Create
entity = {
    "id": 123,
    "name": "Apple Inc.",
    "ticker": "AAPL",
    "category": "Technology",
    "description": "Consumer electronics company",
    "created_at": "2024-11-25T10:00:00Z"
}

doc_id = manager.create(entity)
print(f"Created: {doc_id}")

# Update
entity["description"] = "Consumer electronics and software company (UPDATED)"
entity["version"] = "2.0"
manager.update(doc_id, entity)
print("Updated!")

# Delete
manager.delete(doc_id)
print("Deleted!")
```

---

## 📊 Monitoring & Best Practices

### Track Sync Status
```python
def check_sync_status():
    """Verify RAG is in sync with database"""
    stats = requests.get("http://localhost:8000/api/stats").json()
    db_count = count_entities_in_database()
    
    print(f"Database entities: {db_count}")
    print(f"RAG chunks: {stats['total_chunks']}")
    
    if db_count != stats['total_chunks']:
        print("⚠️ WARNING: Mismatch detected!")
```

### Error Handling
```python
try:
    result = manager.update(doc_id, entity)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        # Document not found - recreate it
        print("Document not found, creating new one...")
        doc_id = manager.create(entity)
    else:
        raise
```

### Batch Operations with Retry
```python
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def safe_update(doc_id, entity):
    """Update with automatic retry"""
    return manager.update(doc_id, entity)
```

---

## ✅ Summary

| Feature | Benefit |
|---------|---------|
| **CREATE** | Add entities as they're created in your system |
| **UPDATE** | Keep embeddings fresh when entities change |
| **DELETE** | Remove obsolete entities completely |
| **document_id** | Stable ID for tracking across systems |
| **Metadata** | Track versions, timestamps, sources |

**Result:** Your AI never works with stale data! 🎉
