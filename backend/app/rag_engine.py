"""
RAG Engine for document processing and retrieval
Handles document ingestion, vector storage, and conversational retrieval
"""
import os
import uuid
from typing import Optional, Dict
from datetime import datetime

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader
)

from app.models import ChatResponse, DocumentUploadResponse, SourceDocument


class RAGEngine:
    """
    Retrieval-Augmented Generation Engine
    Manages document processing, vector storage, and AI-powered chat
    """
    
    def __init__(self):
        """Initialize the RAG engine with OpenAI and vector store"""
        # Get OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI embeddings model
        self.embeddings = OpenAIEmbeddings(
            api_key=self.api_key,
            model="text-embedding-3-small"
        )
        
        # Initialize ChatGPT LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=self.api_key
        )
        
        # Setup vector store persistence
        self.vector_store_path = "/app/vector_db"
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        # Initialize text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Store conversation memories by session_id
        self.conversations: Dict[str, ConversationBufferMemory] = {}
        
        # Initialize ChromaDB vector store
        try:
            self.vector_store = Chroma(
                persist_directory=self.vector_store_path,
                embedding_function=self.embeddings,
                collection_name="rag_documents"
            )
            print(f"Vector store loaded with {self.vector_store._collection.count()} chunks")
        except Exception as e:
            print(f"Creating new vector store: {e}")
            self.vector_store = Chroma(
                persist_directory=self.vector_store_path,
                embedding_function=self.embeddings,
                collection_name="rag_documents"
            )
    
    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        use_rag: bool = True
    ) -> ChatResponse:
        """
        Process a chat message with optional RAG retrieval
        
        Args:
            message: User's input message
            session_id: Session identifier for conversation context
            use_rag: Whether to use document retrieval (RAG mode)
            
        Returns:
            ChatResponse with answer and optional source documents
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session_{uuid.uuid4()}"
        
        # Get or create conversation memory for this session
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        
        try:
            # Check if vector store has documents
            has_documents = self.vector_store._collection.count() > 0
            
            if use_rag and has_documents:
                # RAG Mode: Use document retrieval + LLM
                
                # First, retrieve relevant documents with scores
                docs_with_scores = self.vector_store.similarity_search_with_score(message, k=3)
                
                print(f"🔍 Query: '{message}'")
                print(f"📄 Found {len(docs_with_scores)} documents")
                for i, (doc, score) in enumerate(docs_with_scores):
                    print(f"  Doc {i+1}: {doc.metadata.get('filename', 'Unknown')} - Score: {score:.4f}")
                    print(f"    Content preview: {doc.page_content[:100]}...")
                
                # Extract just the documents for the chain
                retrieved_docs = [doc for doc, score in docs_with_scores]
                
                # Create QA chain with better prompting
                from langchain.prompts import PromptTemplate
                
                # Custom prompt that's more forgiving and helpful
                combine_docs_custom_prompt = PromptTemplate(
                    template="""You are a helpful AI assistant. Use the following pieces of context to answer the question at the end. 
If you can find ANY relevant information in the context, use it to provide a helpful answer.
If you're not completely certain, still try to provide helpful information based on what's available.
Only say you don't know if there is absolutely no relevant information in the context.

Context: {context}

Question: {question}

Helpful Answer:""",
                    input_variables=["context", "question"]
                )
                
                qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=self.vector_store.as_retriever(
                        search_type="similarity",
                        search_kwargs={"k": 5}  # Increased from 3 to 5 for more context
                    ),
                    memory=self.conversations[session_id],
                    return_source_documents=True,
                    verbose=True,  # Enable verbose for debugging
                    combine_docs_chain_kwargs={"prompt": combine_docs_custom_prompt}
                )
                
                result = qa_chain({"question": message})
                response_text = result["answer"]
                
                # Log token usage if available
                if hasattr(result, 'response_metadata') and 'token_usage' in result.get('response_metadata', {}):
                    token_usage = result['response_metadata']['token_usage']
                    print(f"🔢 Token Usage - Prompt: {token_usage.get('prompt_tokens', 0)}, "
                          f"Completion: {token_usage.get('completion_tokens', 0)}, "
                          f"Total: {token_usage.get('total_tokens', 0)}")
                
                # Format source documents with actual relevance scores
                sources = []
                for (doc, score) in docs_with_scores:
                    # ChromaDB uses distance (lower is better), convert to similarity score
                    similarity_score = 1.0 / (1.0 + score) if score > 0 else 1.0
                    
                    sources.append(SourceDocument(
                        content=doc.page_content[:300],  # Truncate for display
                        filename=doc.metadata.get("filename", "Unknown"),
                        page=doc.metadata.get("page", None),
                        relevance_score=round(similarity_score, 4)
                    ))
                
                print(f"📚 Retrieved {len(sources)} sources with scores: {[s.relevance_score for s in sources]}")
                
            elif use_rag and not has_documents:
                # No documents uploaded yet
                response_text = (
                    "I'm in RAG mode but no documents have been uploaded yet. "
                    "Please upload some documents first, or toggle RAG mode off "
                    "to chat without document context."
                )
                sources = []
                
            else:
                # Direct LLM mode without RAG
                # Still maintain conversation context
                memory = self.conversations[session_id]
                
                # Build conversation context
                chat_history = memory.load_memory_variables({}).get("chat_history", [])
                
                # Use invoke instead of deprecated predict method
                from langchain_core.messages import HumanMessage, SystemMessage
                
                messages_for_llm = []
                if chat_history:
                    # Include previous messages for context
                    messages_for_llm.append(SystemMessage(content="You are a helpful AI assistant."))
                    messages_for_llm.extend(chat_history)
                    messages_for_llm.append(HumanMessage(content=message))
                else:
                    # First message in conversation
                    messages_for_llm = [
                        SystemMessage(content="You are a helpful AI assistant."),
                        HumanMessage(content=message)
                    ]
                
                # Invoke LLM and get response with metadata
                response = self.llm.invoke(messages_for_llm)
                response_text = response.content
                
                # Log token usage
                if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
                    token_usage = response.response_metadata['token_usage']
                    print(f"Token Usage - Prompt: {token_usage.get('prompt_tokens', 0)}, "
                          f"Completion: {token_usage.get('completion_tokens', 0)}, "
                          f"Total: {token_usage.get('total_tokens', 0)}")
                
                # Save to memory
                memory.save_context({"question": message}, {"answer": response_text})
                sources = []
            
            return ChatResponse(
                response=response_text,
                sources=sources
            )
        
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return ChatResponse(
                response=f"I apologize, but I encountered an error: {str(e)}",
                sources=[]
            )
    
    async def process_document(
        self,
        file_path: str,
        filename: str
    ) -> DocumentUploadResponse:
        """
        Process and index a document into the vector store
        
        Args:
            file_path: Absolute path to the uploaded file
            filename: Original filename
            
        Returns:
            DocumentUploadResponse with processing results
        """
        try:
            # Determine file type and select appropriate loader
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == ".pdf":
                loader = PyPDFLoader(file_path)
            elif file_extension == ".txt":
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_extension in [".docx", ".doc"]:
                loader = Docx2txtLoader(file_path)
            elif file_extension in [".pptx", ".ppt"]:
                loader = UnstructuredPowerPointLoader(file_path)
            elif file_extension in [".xlsx", ".xls"]:
                loader = UnstructuredExcelLoader(file_path)
            else:
                return DocumentUploadResponse(
                    success=False,
                    message=f"Unsupported file type: {file_extension}",
                    file_id=None,
                    filename=filename,
                    chunks_created=0
                )
            
            # Load document
            documents = loader.load()
            
            # Log what was extracted
            total_text = "".join([doc.page_content for doc in documents])
            print(f"📄 Extracted {len(total_text)} characters from {len(documents)} pages")
            print(f"📝 First 500 chars: {total_text[:500]}")
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "file_id": file_id,
                    "filename": filename,
                    "upload_date": datetime.now().isoformat(),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                
                # Extract page number if available (for PDFs)
                if "page" in chunk.metadata:
                    chunk.metadata["page"] = chunk.metadata["page"] + 1  # 0-indexed to 1-indexed
            
            # Add chunks to vector store
            self.vector_store.add_documents(chunks)
            
            # Persist to disk
            self.vector_store.persist()
            
            print(f"Successfully processed {filename}: {len(chunks)} chunks created")
            
            return DocumentUploadResponse(
                success=True,
                message=f"Successfully processed {filename}",
                file_id=file_id,
                filename=filename,
                chunks_created=len(chunks)
            )
        
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return DocumentUploadResponse(
                success=False,
                message=f"Error processing document: {str(e)}",
                file_id=None,
                filename=filename,
                chunks_created=0
            )
    
    def get_vector_store_stats(self) -> dict:
        """Get statistics about the vector store"""
        try:
            count = self.vector_store._collection.count()
            return {
                "total_chunks": count,
                "status": "active" if count > 0 else "empty"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    def clear_vector_store(self) -> dict:
        """Clear all documents from the vector store"""
        try:
            # Delete the entire collection
            self.vector_store._client.delete_collection(name="rag_documents")
            
            # Recreate empty collection
            self.vector_store = Chroma(
                persist_directory=self.vector_store_path,
                embedding_function=self.embeddings,
                collection_name="rag_documents"
            )
            
            print("✅ Vector store cleared successfully")
            return {
                "success": True,
                "message": "All documents cleared from knowledge base"
            }
        except Exception as e:
            print(f"Error clearing vector store: {str(e)}")
            return {
                "success": False,
                "message": f"Error clearing vector store: {str(e)}"
            }

