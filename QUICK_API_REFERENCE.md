# Text Ingestion API - Quick Reference

## 🎯 Purpose

Replace file-based entity uploads with **programmatic API ingestion** for real-time knowledge base updates.

## ⚡ Quick Start

### Basic Text Ingestion
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your text content here",
    "document_name": "my_document",
    "metadata": {"source": "api"}
  }'
```

### Response
```json
{
  "success": true,
  "message": "Successfully ingested my_document",
  "file_id": "uuid-here",
  "filename": "my_document",
  "chunks_created": 2
}
```

## 📝 Request Schema

```typescript
{
  content: string;           // Required - Text or JSON string
  document_name?: string;    // Optional - Default: "api_document"
  metadata?: {              // Optional - Custom metadata
    source?: string;
    category?: string;
    [key: string]: any;
  }
}
```

## 🔥 Common Use Cases

### 1. Entity Sync from Database
```python
import requests
import json

# Fetch from database
entities = [
    {"name": "Apple Inc.", "code": "AAPL", "sector": "Technology"},
    {"name": "Microsoft", "code": "MSFT", "sector": "Technology"}
]

# Ingest to RAG
requests.post("http://localhost:8000/api/ingest", json={
    "content": json.dumps(entities),
    "document_name": f"entities_{datetime.now().date()}",
    "metadata": {"source": "database", "category": "investment"}
})
```

### 2. Webhook Integration
```python
@app.post("/webhook/entity-update")
def entity_updated(data: dict):
    # Forward to RAG system
    requests.post("http://localhost:8000/api/ingest", json={
        "content": json.dumps(data),
        "document_name": f"entity_{data['id']}",
        "metadata": {"source": "webhook", "entity_id": data['id']}
    })
```

### 3. Scheduled Sync (Cron)
```bash
# crontab: Daily at 2 AM
0 2 * * * python3 /path/to/sync_entities.py
```

```python
# sync_entities.py
def daily_sync():
    entities = fetch_from_database()
    requests.post("http://localhost:8000/api/ingest", json={
        "content": json.dumps(entities),
        "document_name": f"daily_sync_{date.today()}",
        "metadata": {"source": "scheduled"}
    })
```

## 🛠️ Management Commands

### Check Vector Store Stats
```bash
curl http://localhost:8000/api/stats
# {"total_chunks": 42, "status": "active"}
```

### Clear All Data
```bash
curl -X DELETE http://localhost:8000/api/clear
# Clears embeddings + uploaded files
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 📊 Comparison: Old vs New

| Feature | File Upload | API Ingestion |
|---------|-------------|---------------|
| Method | Manual upload | Programmatic |
| Automation | ❌ No | ✅ Yes |
| Real-time | ❌ No | ✅ Yes |
| Integration | Limited | Easy |
| Use Case | User uploads | System sync |

## 🚀 Benefits

1. **No File Management** - Direct text/JSON ingestion
2. **Real-time Updates** - Sync as data changes
3. **Automation Ready** - Perfect for cron jobs, webhooks
4. **Flexible Metadata** - Track source, version, timestamps
5. **Scalable** - Handle dynamic data updates

## 📚 Documentation

- **Complete Guide**: [API_INGESTION_GUIDE.md](./API_INGESTION_GUIDE.md)
- **Python Examples**: [example_api_ingestion.py](./example_api_ingestion.py)
- **API Docs**: http://localhost:8000/docs

## 💡 Example Workflow

```python
# 1. Clear old data
requests.delete("http://localhost:8000/api/clear")

# 2. Ingest new entities
entities = fetch_latest_entities()
requests.post("http://localhost:8000/api/ingest", json={
    "content": json.dumps(entities),
    "document_name": "entities_latest",
    "metadata": {"version": "2.0", "timestamp": datetime.now().isoformat()}
})

# 3. Verify
stats = requests.get("http://localhost:8000/api/stats").json()
print(f"Knowledge base has {stats['total_chunks']} chunks")

# 4. Query
response = requests.post("http://localhost:8000/api/chat", json={
    "message": "What entities do we have?",
    "use_rag": True
})
print(response.json()["response"])
```

## 🎯 Next Steps

1. Run the example: `python3 example_api_ingestion.py`
2. Read the full guide: [API_INGESTION_GUIDE.md](./API_INGESTION_GUIDE.md)
3. Test with your data: Use the `/api/ingest` endpoint
4. Integrate into your workflow: Set up automation

---

**Need help?** Check the Swagger UI at http://localhost:8000/docs
