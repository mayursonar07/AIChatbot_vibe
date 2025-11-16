# 🤖 AI RAG Chatbot - Production Ready

A modern, production-grade AI chatbot with **Retrieval Augmented Generation (RAG)** capabilities. Built with React (TypeScript) frontend and Python (FastAPI + LangChain) backend, fully containerized with Docker.

## ✨ Features

- 💬 **Intelligent Chat Interface** - Modern, responsive UI with real-time messaging
- 📚 **RAG Technology** - Upload documents to create a custom knowledge base
- 🔍 **Smart Retrieval** - Vector similarity search for relevant context
- 🎨 **Beautiful UI** - Glassmorphism design with smooth animations
- 🐳 **Docker Ready** - Separate containers for frontend and backend
- 📄 **Multi-Format Support** - PDF, TXT, DOCX, PPTX, XLSX
- 🔄 **Chat History** - Persistent conversation context
- 📊 **Source Citations** - See which documents informed each response
- ⚡ **Fast & Scalable** - Production-ready architecture

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  React Frontend │◄───────►│  FastAPI Backend │
│   (Port 3000)   │  HTTP   │   (Port 8000)    │
└─────────────────┘         └──────────────────┘
                                      │
                            ┌─────────┴─────────┐
                            ▼                   ▼
                    ┌──────────────┐   ┌──────────────┐
                    │ Vector Store │   │  LLM (GPT-4) │
                    │  (ChromaDB)  │   │    OpenAI    │
                    └──────────────┘   └──────────────┘
```

## 📁 Complete Project Structure

```
ai-rag-chatbot/
├── frontend/                      # React TypeScript Application
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── App.tsx               # Main React component
│   │   ├── App.css               # Styles
│   │   ├── index.tsx             # React entry point
│   │   └── index.css             # Global styles
│   ├── package.json               # Frontend dependencies
│   ├── tsconfig.json              # TypeScript config
│   ├── Dockerfile                 # Frontend Docker image
│   └── .env                       # Frontend environment variables
│
├── backend/                       # Python FastAPI Application
│   ├── app/
│   │   ├── __init__.py           # Package initializer
│   │   ├── main.py               # FastAPI application
│   │   ├── models.py             # Pydantic models
│   │   └── rag_engine.py         # RAG logic (LangChain)
│   ├── uploads/                   # Document storage (created automatically)
│   ├── vector_db/                 # Vector database (created automatically)
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Backend Docker image
│   └── .env                       # Backend environment variables
│
├── docker-compose.yml             # Docker orchestration
├── .env                           # Root environment variables
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** installed ([Download](https://www.docker.com/products/docker-desktop))
- **OpenAI API Key** ([Get one](https://platform.openai.com/api-keys))
- **Git** (optional, for cloning)

### Step 1: Create Project Structure

```bash
# Create main directory
mkdir ai-rag-chatbot
cd ai-rag-chatbot

# Create subdirectories
mkdir -p frontend/src frontend/public
mkdir -p backend/app
```

### Step 2: Copy All Files

Copy the provided files into their respective directories:

**Frontend Files:**
- `frontend/src/App.tsx`
- `frontend/src/App.css`
- `frontend/package.json`
- `frontend/Dockerfile`
- `frontend/.env`

**Backend Files:**
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/rag_engine.py`
- `backend/requirements.txt`
- `backend/Dockerfile`
- `backend/.env`

**Root Files:**
- `docker-compose.yml`
- `.env`

### Step 3: Configure API Keys

Edit the `.env` file in the root directory and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

Also update `backend/.env` with the same key.

### Step 4: Create Missing React Files

Create these minimal required files for React:

**frontend/public/index.html:**
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="AI RAG Chatbot" />
    <title>AI RAG Chatbot</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
```

**frontend/src/index.tsx:**
```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**frontend/src/index.css:**
```css
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
}
```

**frontend/tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

### Step 5: Build and Run with Docker

```bash
# From the project root directory
docker-compose up --build
```

This will:
1. Build both frontend and backend Docker images
2. Start both containers
3. Set up networking between them
4. Create necessary volumes

**Wait for these messages:**
- `✅ RAG Engine initialized successfully`
- `Compiled successfully!` (from frontend)

### Step 6: Access the Application

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. Upload Documents

1. Click **"Upload Document"** button in the sidebar
2. Select a PDF, TXT, DOCX, PPTX, or XLSX file
3. Wait for processing (you'll see chunk count)
4. Document is now in your knowledge base!

### 2. Chat with AI

1. Type your question in the input box
2. Press Enter or click Send
3. AI will retrieve relevant context and respond
4. View source citations below responses

### 3. Toggle RAG Mode

- **RAG ON**: Uses uploaded documents for context
- **RAG OFF**: Uses only AI's general knowledge

### 4. Clear Chat

Click the "Clear" button to start a fresh conversation.

## 🔧 Development Mode

### Run Locally (Without Docker)

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```

## 🐳 Docker Commands Cheat Sheet

```bash
# Start application (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Rebuild after changes
docker-compose up --build

# Restart a specific service
docker-compose restart backend
docker-compose restart frontend

# View running containers
docker ps

# Clean everything (including volumes)
docker-compose down -v
docker system prune -a
```

## 🔒 Security Notes

- Never commit `.env` files with real API keys
- Use environment variables for sensitive data
- Add `.env` to `.gitignore`
- In production, use secrets management (AWS Secrets Manager, etc.)

## 🚢 Production Deployment

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy 'build' folder
```

### Backend (AWS ECS/Railway/Render)
```bash
docker build -t rag-backend ./backend
docker push your-registry/rag-backend:latest
```

### Vector Database
- Use managed Pinecone (instead of local ChromaDB)
- Or deploy ChromaDB with persistent storage

## 🐛 Troubleshooting

**Problem: Port already in use**
```bash
# Solution: Change ports in docker-compose.yml
ports:
  - "3001:3000"  # Frontend
  - "8001:8000"  # Backend
```

**Problem: Docker build fails**
```bash
# Solution: Clear cache
docker system prune -a
docker-compose build --no-cache
```

**Problem: CORS errors**
- Check `REACT_APP_API_URL` in `frontend/.env`
- Verify CORS settings in `backend/app/main.py`

**Problem: No API key error**
- Ensure `OPENAI_API_KEY` is set in `.env` and `backend/.env`
- Restart Docker containers after adding keys

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/upload` | Upload document |
| POST | `/api/chat` | Send message |
| GET | `/api/history/{session_id}` | Get chat history |
| DELETE | `/api/session/{session_id}` | Clear session |
| GET | `/api/stats` | Get system stats |
| POST | `/api/clear-knowledge-base` | Clear all documents |

Full API documentation: http://localhost:8000/docs

## 🎯 Next Steps

1. ✅ **Add Authentication** - JWT tokens, OAuth
2. ✅ **Persistent Storage** - PostgreSQL for chat history
3. ✅ **Advanced RAG** - Multiple retrieval strategies
4. ✅ **Streaming Responses** - Real-time token streaming
5. ✅ **Multi-User Support** - User accounts and permissions
6. ✅ **Analytics Dashboard** - Usage metrics and insights
7. ✅ **Mobile App** - React Native version

## 📝 License

MIT License - Free to use and modify

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 💬 Support

For issues or questions:
- Open a GitHub issue
- Check API documentation at `/docs`
- Review Docker logs: `docker-compose logs`

---

**Built with ❤️ using React, FastAPI, LangChain, and Docker**
