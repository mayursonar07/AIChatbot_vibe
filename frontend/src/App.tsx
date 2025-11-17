// frontend/src/App.tsx

/**
 * Main React Application Component
 * AI RAG Chatbot with document upload and chat interface
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import { 
  Send, Upload, Trash2, FileText, AlertCircle, 
  CheckCircle, Loader, MessageSquare, Database 
} from 'lucide-react';

// API configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// TypeScript interfaces for type safety
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: SourceDocument[];
}

interface SourceDocument {
  content: string;
  filename: string;
  page?: number;
  relevance_score: number;
}

interface UploadedFile {
  file_id: string;
  filename: string;
  chunks_created: number;
  uploaded_at: string;
}

function App() {
  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [useRag, setUseRag] = useState(true);
  
  // Refs for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Show notification with auto-dismiss
  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };
  
  /**
   * Handle sending a chat message
   */
  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      // Send message to backend
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: input,
        session_id: sessionId,
        use_rag: useRag
      });
      
      // Add assistant response
      const assistantMessage: Message = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
        sources: response.data.sources || []
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (error: any) {
      console.error('Chat error:', error);
      showNotification('error', error.response?.data?.detail || 'Failed to send message');
      
      // Add error message
      const errorMessage: Message = {
        id: `msg_${Date.now()}_error`,
        role: 'assistant',
        content: '❌ Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Handle file upload for RAG knowledge base
   */
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['.pdf', '.txt', '.docx', '.pptx', '.xlsx'];
    const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
      showNotification('error', `Unsupported file type. Allowed: ${allowedTypes.join(', ')}`);
      return;
    }
    
    setUploading(true);
    
    try {
      // Create form data for file upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Upload to backend
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      // Add to uploaded files list
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
  
  /**
   * Clear chat history
   */
  const handleClearChat = () => {
    if (window.confirm('Clear all messages?')) {
      setMessages([]);
      showNotification('success', 'Chat cleared');
    }
  };
  
  /**
   * Clear knowledge base (all uploaded documents)
   */
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
  
  /**
   * Handle Enter key press
   */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <div className="app-container">
      {/* Notification Banner */}
      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
          <span>{notification.message}</span>
        </div>
      )}
      
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <MessageSquare size={32} />
            <h1>AI RAG Chatbot</h1>
          </div>
          <div className="header-actions">
            <button 
              className="btn btn-secondary"
              onClick={() => setUseRag(!useRag)}
              title={useRag ? "RAG Mode ON" : "RAG Mode OFF"}
            >
              <Database size={18} />
              {useRag ? 'RAG ON' : 'RAG OFF'}
            </button>
            <button 
              className="btn btn-secondary"
              onClick={handleClearChat}
              title="Clear chat"
            >
              <Trash2 size={18} />
              Clear
            </button>
          </div>
        </div>
      </header>
      
      <div className="main-content">
        {/* Sidebar - Document Upload & History */}
        <aside className="sidebar">
          <div className="sidebar-section">
            <h3>📚 Knowledge Base</h3>
            
            {/* File Upload */}
            <div className="upload-section">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.docx,.pptx,.xlsx"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
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
                Supported: PDF, TXT, DOCX, PPTX, XLSX
              </p>
            </div>
            
            {/* Uploaded Files List */}
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
                  
                  {/* Clear Knowledge Base Button */}
                  <button 
                    className="btn btn-secondary btn-block"
                    onClick={handleClearKnowledgeBase}
                    style={{ marginTop: '10px' }}
                  >
                    <Trash2 size={16} />
                    Clear Knowledge Base
                  </button>
                </>
              )}
            </div>
          </div>
        </aside>
        
        {/* Chat Area */}
        <main className="chat-container">
          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="empty-chat">
                <MessageSquare size={64} color="#cbd5e1" />
                <h2>Welcome to AI RAG Chatbot</h2>
                <p>Upload documents to build your knowledge base, then start chatting!</p>
                <div className="suggestions">
                  <button className="suggestion" onClick={() => setInput("What can you help me with?")}>
                    What can you help me with?
                  </button>
                  <button className="suggestion" onClick={() => setInput("Explain the uploaded documents")}>
                    Explain the uploaded documents
                  </button>
                </div>
              </div>
            ) : (
              messages.map(message => (
                <div key={message.id} className={`message ${message.role}`}>
                  <div className="message-content">
                    <div className="message-header">
                      <span className="message-role">
                        {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
                      </span>
                      <span className="message-time">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="message-text">{message.content}</div>
                    
                    {/* Display sources if available */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="message-sources">
                        <p className="sources-title">📎 Sources:</p>
                        {message.sources.map((source, idx) => (
                          <div key={idx} className="source-item">
                            <strong>{source.filename}</strong>
                            {source.page && <span> (Page {source.page})</span>}
                            <p className="source-excerpt">{source.content}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            
            {/* Loading indicator */}
            {loading && (
              <div className="message assistant">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Input Area */}
          <div className="input-container">
            <textarea
              className="message-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
              rows={1}
              disabled={loading}
            />
            <button 
              className="btn btn-primary btn-send"
              onClick={handleSendMessage}
              disabled={loading || !input.trim()}
            >
              <Send size={20} />
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
