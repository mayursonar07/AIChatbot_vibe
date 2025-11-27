import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Send, Upload, Trash2, FileText, AlertCircle, 
  CheckCircle, Loader, MessageSquare, Database, ChevronDown, X, MessageCircle, Menu
} from 'lucide-react';
import '../App.css';
import entitiesData from '../data/entities.json';

// Load entities from JSON file
const entities = entitiesData;

const API_URL = 'http://localhost:8000';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Array<{
    content: string;
    filename: string;
    page?: number;
    relevance_score: number;
  }>;
  matchedEntities?: Array<{
    name: string;
    shortCode: string;
    category: string;
  }>;
}

interface UploadedFile {
  file_id: string;
  filename: string;
  chunks_created: number;
  uploaded_at: string;
}

interface EntityDropdownProps {
  label: string;
  value: number | null;
  onChange: (id: number) => void;
  onAskAI: () => void;
}

function EntityDropdown({ label, value, onChange, onAskAI }: EntityDropdownProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const filtered = entities.filter(e =>
    e.name.toLowerCase().includes(search.toLowerCase()) ||
    e.shortCode.toLowerCase().includes(search.toLowerCase()) ||
    e.category.toLowerCase().includes(search.toLowerCase())
  );

  const selected = entities.find(e => e.id === value);

  return (
    <div ref={ref} className="entity-dropdown">
      <label>{label}</label>
      <div className="entity-dropdown-trigger" onClick={() => setOpen(!open)}>
        <span className={selected ? '' : 'placeholder'}>
          {selected ? `${selected.name} (${selected.shortCode})` : 'Select entity...'}
        </span>
        <ChevronDown className={`chevron ${open ? 'open' : ''}`} />
      </div>
      
      {open && (
        <div className="entity-dropdown-panel">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search entities..."
            className="entity-search-input"
            autoFocus
          />
          <div className="entity-list">
            {filtered.map(e => (
              <div
                key={e.id}
                onClick={() => {
                  onChange(e.id);
                  setOpen(false);
                  setSearch('');
                }}
                className="entity-item"
              >
                <div className="entity-item-name">{e.name}</div>
                <div className="entity-item-meta">{e.shortCode} • {e.category}</div>
                <div className="entity-item-description">{e.description}</div>
              </div>
            ))}
          </div>
          <div className="entity-ask-ai" onClick={() => { onAskAI(); setOpen(false); }}>
            Need help choosing? Ask AI
          </div>
        </div>
      )}
    </div>
  );
}

interface ChatSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  useRag: boolean;
  uploadedFiles: UploadedFile[];
}

function ChatSidebar({ isOpen, onClose, useRag, uploadedFiles }: ChatSidebarProps) {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Hello! I can help you find the right entity for your file transfer. Ask me about specific services or firms, or upload entities.json for better assistance.', timestamp: new Date().toISOString() }
  ]);
  const [input, setInput] = useState('');
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [loading, setLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  // Helper function to extract entity names from text
  const findMatchedEntities = (text: string): Array<{name: string, shortCode: string, category: string}> => {
    const matched: Array<{name: string, shortCode: string, category: string}> = [];
    entities.forEach(entity => {
      const regex = new RegExp(`\\b${entity.name}\\b|\\b${entity.shortCode}\\b`, 'gi');
      if (regex.test(text)) {
        matched.push({
          name: entity.name,
          shortCode: entity.shortCode,
          category: entity.category
        });
      }
    });
    return matched;
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { 
      id: Date.now().toString(), 
      role: 'user', 
      content: input, 
      timestamp: new Date().toISOString() 
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Enhanced prompt to include entity context
      const enhancedMessage = uploadedFiles.some(f => f.filename.toLowerCase().includes('entities'))
        ? input
        : `${input}\n\nContext: I'm looking for entities from this list: ${entities.map(e => `${e.name} (${e.shortCode}) - ${e.category}`).slice(0, 5).join(', ')}...`;

      const response = await axios.post(`${API_URL}/api/chat`, {
        message: enhancedMessage,
        session_id: sessionId,
        use_rag: useRag
      });

      const matchedEntities = findMatchedEntities(response.data.response);
      
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
        sources: response.data.sources,
        matchedEntities: matchedEntities.length > 0 ? matchedEntities : undefined
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (error: any) {
      console.error('Chat error:', error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`ai-chat-sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="ai-chat-header">
        <h3>AI Assistant</h3>
        <button onClick={onClose} className="ai-chat-close">
          <X />
        </button>
      </div>

      <div ref={chatRef} className="ai-chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`ai-chat-message ${msg.role}`}>
            {/* Display matched entities first */}
            {msg.matchedEntities && msg.matchedEntities.length > 0 && (
              <div className="matched-entities">
                <div className="matched-entities-header">✅ Matched Entities:</div>
                {msg.matchedEntities.map((entity, idx) => (
                  <div key={idx} className="matched-entity-item">
                    <strong>{entity.name}</strong> ({entity.shortCode}) - {entity.category}
                  </div>
                ))}
              </div>
            )}
            
            {/* Display message content only if no entities are matched */}
            {(!msg.matchedEntities || msg.matchedEntities.length === 0) && (
              <div className="ai-chat-message-content">{msg.content}</div>
            )}
          </div>
        ))}
        {loading && (
          <div className="ai-chat-message assistant">
            <div className="ai-chat-message-content">
              <Loader size={16} className="spinner" /> Thinking...
            </div>
          </div>
        )}
      </div>

      <div className="ai-chat-input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
          placeholder="Ask about entities..."
          className="ai-chat-input"
          disabled={loading}
        />
        <button onClick={handleSend} className="ai-chat-send" disabled={loading}>
          {loading ? <Loader size={18} className="spinner" /> : <Send />}
        </button>
      </div>
    </div>
  );
}

function Home() {
  const navigate = useNavigate();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [useRag, setUseRag] = useState(true);
  const [from, setFrom] = useState<number | null>(null);
  const [to, setTo] = useState<number | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };
  
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    const allowedTypes = ['.pdf', '.txt', '.docx', '.pptx', '.xlsx', '.json'];
    const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
      showNotification('error', `Unsupported file type. Allowed: ${allowedTypes.join(', ')}`);
      return;
    }
    
    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const uploadedFile: UploadedFile = {
        file_id: response.data.file_id,
        filename: response.data.filename,
        chunks_created: response.data.chunks_created,
        uploaded_at: new Date().toISOString()
      };
      
      setUploadedFiles(prev => [...prev, uploadedFile]);
      showNotification('success', `${file.name} uploaded successfully! ${response.data.chunks_created} chunks created.`);
      
    } catch (error: any) {
      console.error('Upload error:', error);
      showNotification('error', error.response?.data?.detail || 'Upload failed');
      
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };
  
  const handleClearKnowledgeBase = async () => {
    if (!window.confirm('Clear all uploaded documents from knowledge base? This cannot be undone.')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/api/clear`);
      setUploadedFiles([]);
      showNotification('success', 'Knowledge base cleared successfully');
    } catch (error: any) {
      console.error('Clear error:', error);
      showNotification('error', error.response?.data?.detail || 'Failed to clear knowledge base');
    }
  };
  
  return (
    <div className="app-container">
      
      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
          <span>{notification.message}</span>
        </div>
      )}
      
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <Menu />
            </button>
            <MessageSquare size={32} />
            <h1>Global File Transfer System</h1>
          </div>
          <div className="header-actions">
            <button className="btn btn-secondary" onClick={() => navigate('/registration')}>
              New Registration
            </button>
            <button className="btn btn-secondary" onClick={() => setUseRag(!useRag)}>
              <Database size={18} />
              {useRag ? 'RAG ON' : 'RAG OFF'}
            </button>
          </div>
        </div>
      </header>
      
      <div className="main-content">
        <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
          <div className="sidebar-section">
            <h3>📚 Knowledge Base</h3>
            
            <div className="upload-section">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.docx,.pptx,.xlsx,.json"
                onChange={handleFileUpload}
                className="file-input-hidden"
                disabled={uploading}
              />
              <button 
                className="btn btn-primary btn-block"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
              >
                {uploading ? (
                  <>
                    <Loader size={18} className="spinner" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload size={18} />
                    Upload Document
                  </>
                )}
              </button>
              <p className="upload-hint">
                Supported: PDF, TXT, DOCX, PPTX, XLSX, JSON
              </p>
            </div>
            
            <div className="files-list">
              {uploadedFiles.length === 0 ? (
                <p className="empty-state">No documents uploaded yet</p>
              ) : (
                <>
                  {uploadedFiles.map(file => (
                    <div key={file.file_id} className="file-item">
                      <FileText size={16} />
                      <div className="file-info">
                        <span className="file-name">{file.filename}</span>
                        <span className="file-chunks">{file.chunks_created} chunks</span>
                      </div>
                    </div>
                  ))}
                  
                  <button className="btn btn-secondary btn-block" onClick={handleClearKnowledgeBase}>
                    <Trash2 size={16} />
                    Clear Knowledge Base
                  </button>
                </>
              )}
            </div>
          </div>
        </aside>
        
        <main className="chat-container">
          <div className="transfer-form-container">
            <div className="transfer-form-header">
              <h2>Transfer Configuration</h2>
              <p>Securely transfer files across entities.</p>
            </div>

            <EntityDropdown
              label="Transfer From"
              value={from}
              onChange={setFrom}
              onAskAI={() => setChatOpen(true)}
            />

            <EntityDropdown
              label="Transfer To"
              value={to}
              onChange={setTo}
              onAskAI={() => setChatOpen(true)}
            />

            <button disabled={!from || !to} className="btn btn-primary btn-block btn-transfer">
              Initiate Transfer
            </button>
          </div>
        </main>
      </div>

      <button className="floating-chat-button" onClick={() => setChatOpen(!chatOpen)}>
        <MessageCircle />
      </button>

      <ChatSidebar 
        isOpen={chatOpen} 
        onClose={() => setChatOpen(false)} 
        useRag={useRag}
        uploadedFiles={uploadedFiles}
      />
    </div>
  );
}

export default Home;

