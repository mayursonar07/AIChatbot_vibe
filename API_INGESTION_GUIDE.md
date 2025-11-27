# API Text Ingestion Guide

## Overview

The `/api/ingest` endpoint allows you to programmatically add data to your RAG system **without uploading files**. This is perfect for:

- **Dynamic entity updates** from databases
- **Real-time data ingestion** from external systems
- **Programmatic knowledge base management**
- **Integration with other services**

## Endpoint Details

### POST `/api/ingest`

Ingest raw text or JSON content directly into the knowledge base.

**Request Body:**
```json
{
  "content": "string (required) - Text or JSON string to ingest",
  "document_name": "string (optional) - Name for this document (default: 'api_document')",
  "metadata": {
    "source": "string",
    "category": "string",
    "any_custom_field": "value"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully ingested document_name",
  "file_id": "uuid",
  "filename": "document_name",
  "chunks_created": 3
}
```

## Usage Examples

### 1. Simple Text Ingestion

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Investment entities: Apple (AAPL), Microsoft (MSFT), Tesla (TSLA)",
    "document_name": "tech_entities",
    "metadata": {
      "source": "api",
      "category": "investment_domain"
    }
  }'
```

### 2. JSON Entities Ingestion

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{\"entities\": [{\"name\": \"Apple Inc.\", \"shortCode\": \"AAPL\", \"category\": \"Technology\"}]}",
    "document_name": "structured_entities",
    "metadata": {
      "source": "database",
      "category": "investment_domain",
      "type": "structured"
    }
  }'
```

### 3. Python Example

```python
import requests
import json

def ingest_entities(entities_data):
    """Ingest entity data into RAG system"""
    url = "http://localhost:8000/api/ingest"
    
    # Convert dict to JSON string
    content = json.dumps(entities_data)
    
    payload = {
        "content": content,
        "document_name": "entity_update_2024",
        "metadata": {
            "source": "entity_management_system",
            "category": "investment_domain",
            "timestamp": "2024-11-25T10:00:00Z"
        }
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Example usage
entities = {
    "entities": [
        {"name": "Apple Inc.", "shortCode": "AAPL", "sector": "Technology"},
        {"name": "Microsoft", "shortCode": "MSFT", "sector": "Technology"}
    ]
}

result = ingest_entities(entities)
print(f"Ingested {result['chunks_created']} chunks")
```

### 4. JavaScript/Node.js Example

```javascript
async function ingestData(content, documentName, metadata = {}) {
  const response = await fetch('http://localhost:8000/api/ingest', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content: content,
      document_name: documentName,
      metadata: metadata
    })
  });
  
  return await response.json();
}

// Usage
const entities = JSON.stringify({
  entities: [
    { name: "Tesla Inc.", shortCode: "TSLA", category: "Automotive" }
  ]
});

const result = await ingestData(
  entities,
  "tesla_entity",
  { source: "api", category: "investment_domain" }
);

console.log(`Created ${result.chunks_created} chunks`);
```

## Best Practices

### 1. Document Naming
Use descriptive, unique names:
```json
{
  "document_name": "entities_investment_2024_q4",
  "content": "..."
}
```

### 2. Metadata Strategy
Include relevant metadata for filtering and tracking:
```json
{
  "metadata": {
    "source": "entity_management_db",
    "category": "investment_domain",
    "version": "1.0",
    "timestamp": "2024-11-25T10:00:00Z",
    "updated_by": "api_service"
  }
}
```

### 3. Content Formatting

**For Better RAG Retrieval:**
```json
{
  "content": "Entity: Apple Inc.\nShort Code: AAPL\nCategory: Technology\nSector: Consumer Electronics\nDescription: Designs and manufactures consumer electronics"
}
```

**For Structured Data:**
```json
{
  "content": "{\"entities\": [{\"name\": \"Apple\", \"code\": \"AAPL\"}]}"
}
```

### 4. Batch Ingestion
For multiple documents:
```python
documents = [
    {"content": "...", "document_name": "doc1", "metadata": {...}},
    {"content": "...", "document_name": "doc2", "metadata": {...}},
]

for doc in documents:
    response = requests.post(api_url, json=doc)
    print(f"Ingested {doc['document_name']}")
```

## Workflow: Replacing entities.json File Upload

### Old Workflow (File Upload)
```bash
# 1. Upload file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@entities.json"
```

### New Workflow (API Ingestion)
```python
import requests
import json

# 1. Load entities from database or generate dynamically
entities = fetch_entities_from_database()

# 2. Ingest directly via API
response = requests.post(
    "http://localhost:8000/api/ingest",
    json={
        "content": json.dumps(entities),
        "document_name": f"entities_{datetime.now().date()}",
        "metadata": {
            "source": "database",
            "category": "investment_domain",
            "auto_sync": True
        }
    }
)

print(f"✅ Synced {response.json()['chunks_created']} chunks")
```

## Integration Examples

### 1. Scheduled Entity Sync (Python + Cron)

```python
#!/usr/bin/env python3
# sync_entities.py
import requests
import json
from datetime import datetime

def sync_entities_to_rag():
    # Fetch from your database
    entities = fetch_from_database()
    
    # Ingest into RAG
    response = requests.post(
        "http://localhost:8000/api/ingest",
        json={
            "content": json.dumps(entities),
            "document_name": f"entities_sync_{datetime.now().isoformat()}",
            "metadata": {
                "source": "scheduled_sync",
                "timestamp": datetime.now().isoformat()
            }
        }
    )
    
    print(f"Sync completed: {response.json()}")

if __name__ == "__main__":
    sync_entities_to_rag()
```

**Crontab entry (daily at 2 AM):**
```
0 2 * * * /usr/bin/python3 /path/to/sync_entities.py >> /var/log/entity_sync.log 2>&1
```

### 2. Webhook Integration

```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook/entity-update', methods=['POST'])
def handle_entity_update():
    """Receive entity updates and sync to RAG"""
    entity_data = request.json
    
    # Ingest into RAG system
    response = requests.post(
        "http://localhost:8000/api/ingest",
        json={
            "content": json.dumps(entity_data),
            "document_name": f"entity_{entity_data['id']}",
            "metadata": {
                "source": "webhook",
                "entity_id": entity_data['id']
            }
        }
    )
    
    return {"status": "success", "rag_response": response.json()}
```

### 3. Database Trigger Integration

```python
# PostgreSQL trigger example
def on_entity_insert_or_update(entity_record):
    """Called by database trigger"""
    content = json.dumps({
        "name": entity_record.name,
        "short_code": entity_record.short_code,
        "category": entity_record.category,
        "description": entity_record.description
    })
    
    requests.post(
        "http://localhost:8000/api/ingest",
        json={
            "content": content,
            "document_name": f"entity_{entity_record.id}",
            "metadata": {
                "source": "database_trigger",
                "entity_id": str(entity_record.id),
                "updated_at": entity_record.updated_at.isoformat()
            }
        }
    )
```

## API Management Endpoints

### Check Vector Store Stats
```bash
curl http://localhost:8000/api/stats
```

**Response:**
```json
{
  "total_chunks": 42,
  "status": "active"
}
```

### Clear All Knowledge Base
```bash
curl -X DELETE http://localhost:8000/api/clear
```

**Response:**
```json
{
  "success": true,
  "message": "Knowledge base cleared: 15 vector folders and 7 uploaded files deleted"
}
```

## Error Handling

```python
try:
    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    result = response.json()
    
    if result['success']:
        print(f"✅ Success: {result['chunks_created']} chunks")
    else:
        print(f"⚠️ Failed: {result['message']}")
        
except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
except requests.exceptions.RequestException as e:
    print(f"❌ Request Error: {e}")
```

## Performance Considerations

1. **Chunk Size**: Default is 1000 characters with 200 overlap. Large documents are automatically split.

2. **Batch Ingestion**: For multiple documents, consider rate limiting:
   ```python
   import time
   
   for doc in documents:
       ingest_document(doc)
       time.sleep(0.1)  # Avoid overwhelming the API
   ```

3. **Embeddings Cost**: Each ingestion creates OpenAI embeddings. Monitor API usage:
   - Text embedding model: `text-embedding-3-small`
   - Approximate cost: $0.02 per 1M tokens

## Comparison: File Upload vs API Ingestion

| Feature | File Upload (`/api/upload`) | API Ingestion (`/api/ingest`) |
|---------|---------------------------|----------------------------|
| Use Case | Manual document upload | Programmatic data sync |
| File Types | PDF, DOCX, XLSX, TXT, JSON | Any text/JSON string |
| Integration | Manual/UI | Automated/Code |
| Metadata | Limited (filename only) | Full custom metadata |
| Automation | No | Yes |
| Real-time Sync | No | Yes |

## Complete Working Example

See `example_api_ingestion.py` for a complete, runnable example demonstrating all features.

```bash
# Run the example
python3 example_api_ingestion.py
```

## Support

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Interactive Testing: http://localhost:8000/docs (Swagger UI)
