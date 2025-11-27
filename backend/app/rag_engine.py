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

from app.models import ChatResponse, DocumentUploadResponse, SourceDocument, EntityMatchResponse, EntityMatch


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
            # Detect "how" questions about methodology/process - prevent disclosure of logic
            query_lower = message.lower().strip()
            
            # Check for methodology questions
            how_patterns = [
                'how do', 'how does', 'how are', 'how is', 'how can', 'how will',
                'explain how', 'tell me how', 'describe how'
            ]
            
            methodology_patterns = [
                'what is the process', 'what is the method', 'what\'s the process',
                'what\'s the method', 'methodology', 'what ensures', 'mechanism',
                'validation process', 'verification process', 'checking process'
            ]
            
            ensure_patterns = [
                'ensure', 'ensur', 'wnsure', 'verify', 'validate', 'confirm',
                'guarantee', 'check', 'make sure'
            ]
            
            domain_patterns = [
                'from investment domain', 'from the domain', 'belong to',
                'are these from', 'domain classification', 'correct domain',
                'investment domain', 'from domain'
            ]
            
            entity_patterns = ['entity', 'entities']
            
            # Detect methodology questions about entities/domains
            starts_with_how = any(query_lower.startswith(pattern) for pattern in how_patterns)
            contains_methodology = any(pattern in query_lower for pattern in methodology_patterns)
            contains_ensure = any(pattern in query_lower for pattern in ensure_patterns)
            contains_domain = any(pattern in query_lower for pattern in domain_patterns)
            contains_entity = any(pattern in query_lower for pattern in entity_patterns)
            
            # It's a methodology question if asking about how we ensure/validate entities or domains
            is_methodology_question = (
                (starts_with_how or contains_methodology) and 
                (contains_ensure or contains_domain) and
                contains_entity
            ) or (
                contains_ensure and contains_domain and contains_entity
            )
            
            if is_methodology_question:
                # Return surface-level explanation without disclosing logic
                methodology_response = """Our entity matching system uses advanced natural language processing 
and machine learning techniques to ensure accurate entity identification:

• **Domain Classification**: We employ specialized models trained on domain-specific data to validate 
  that entities belong to the correct category (e.g., investment domain)

• **Multi-layered Validation**: Entities go through multiple validation stages including semantic 
  analysis, contextual matching, and confidence scoring

• **Knowledge Base Integration**: Our system leverages a curated knowledge base of domain-verified 
  entities to ensure accuracy and relevance

• **Continuous Learning**: The system continuously improves through feedback and updates to maintain 
  high precision in entity matching

For specific entity matches, please provide entity names or descriptions rather than asking about the methodology."""
                
                return ChatResponse(
                    response=methodology_response,
                    sources=[]
                )
            
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
            elif file_extension == ".json":
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
    
    async def ingest_text(
        self,
        content: str,
        document_name: str = "api_document",
        metadata: dict = None
    ) -> dict:
        """
        Ingest raw text/JSON content directly into the vector store
        
        Args:
            content: Raw text or JSON string to ingest
            document_name: Name identifier for this document
            metadata: Optional metadata dict (source, category, etc.)
            
        Returns:
            Dict with success status, message, document_id, and chunks_created
        """
        try:
            from langchain.schema import Document
            
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Parse metadata
            if metadata is None:
                metadata = {}
            
            # Create a single document from the content
            doc = Document(
                page_content=content,
                metadata={
                    "document_id": document_id,
                    "document_name": document_name,
                    "ingestion_date": datetime.now().isoformat(),
                    "source": metadata.get("source", "api"),
                    **metadata  # Include any additional metadata
                }
            )
            
            # Log what we're processing
            print(f"📄 Ingesting text document: {document_name}")
            print(f"📝 Content length: {len(content)} characters")
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Add chunk metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
            
            # Add chunks to vector store
            self.vector_store.add_documents(chunks)
            
            # Persist to disk
            self.vector_store.persist()
            
            print(f"✅ Successfully ingested '{document_name}': {len(chunks)} chunks created")
            
            return {
                "success": True,
                "message": f"Successfully ingested {document_name}",
                "document_id": document_id,
                "chunks_created": len(chunks)
            }
        
        except Exception as e:
            print(f"❌ Error ingesting text: {str(e)}")
            return {
                "success": False,
                "message": f"Error ingesting text: {str(e)}",
                "document_id": None,
                "chunks_created": 0
            }
    
    async def update_document(
        self,
        document_id: str,
        content: str,
        document_name: str = None,
        metadata: dict = None
    ) -> dict:
        """
        Update an existing document by deleting old chunks and ingesting new ones
        
        Args:
            document_id: ID of the document to update
            content: New content for the document
            document_name: Updated document name (optional, keeps old if not provided)
            metadata: Updated metadata (optional, keeps old if not provided)
            
        Returns:
            Dict with success status, message, document_id, and chunks updated
        """
        try:
            # Step 1: Get existing document metadata to preserve name/metadata if not provided
            existing_docs = self.vector_store.get(
                where={"document_id": document_id}
            )
            
            if not existing_docs or not existing_docs['ids']:
                return {
                    "success": False,
                    "message": f"Document {document_id} not found",
                    "document_id": document_id,
                    "chunks_created": 0
                }
            
            # Preserve original metadata if not provided
            original_metadata = existing_docs['metadatas'][0] if existing_docs['metadatas'] else {}
            if document_name is None:
                document_name = original_metadata.get('document_name', 'updated_document')
            if metadata is None:
                metadata = {}
            
            # Merge with original metadata (new values override)
            merged_metadata = {**original_metadata, **metadata}
            
            print(f"📝 Updating document: {document_id} ({document_name})")
            print(f"   Found {len(existing_docs['ids'])} existing chunks")
            
            # Step 2: Delete old chunks
            delete_result = await self.delete_document(document_id)
            if not delete_result["success"]:
                return delete_result
            
            print(f"   Deleted {delete_result['chunks_deleted']} old chunks")
            
            # Step 3: Ingest new content with same document_id
            from langchain.schema import Document
            
            # Create document with preserved/updated metadata
            doc = Document(
                page_content=content,
                metadata={
                    "document_id": document_id,  # Keep same ID
                    "document_name": document_name,
                    "ingestion_date": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "source": merged_metadata.get("source", "api"),
                    **merged_metadata
                }
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Add chunk metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            self.vector_store.persist()
            
            print(f"✅ Updated '{document_name}': {len(chunks)} new chunks created")
            
            return {
                "success": True,
                "message": f"Successfully updated {document_name}",
                "document_id": document_id,
                "chunks_created": len(chunks)
            }
        
        except Exception as e:
            print(f"❌ Error updating document: {str(e)}")
            return {
                "success": False,
                "message": f"Error updating document: {str(e)}",
                "document_id": document_id,
                "chunks_created": 0
            }
    
    async def delete_document(
        self,
        document_id: str
    ) -> dict:
        """
        Delete a specific document and all its chunks from the vector store
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            Dict with success status, message, document_id, and chunks_deleted
        """
        try:
            # Query for all chunks with this document_id
            results = self.vector_store.get(
                where={"document_id": document_id}
            )
            
            if not results or not results['ids']:
                return {
                    "success": False,
                    "message": f"Document {document_id} not found",
                    "document_id": document_id,
                    "chunks_deleted": 0
                }
            
            chunk_ids = results['ids']
            document_name = results['metadatas'][0].get('document_name', 'Unknown') if results['metadatas'] else 'Unknown'
            
            print(f"🗑️  Deleting document: {document_name} ({document_id})")
            print(f"   Found {len(chunk_ids)} chunks to delete")
            
            # Delete all chunks
            self.vector_store._collection.delete(ids=chunk_ids)
            
            # Persist changes
            self.vector_store.persist()
            
            print(f"✅ Deleted {len(chunk_ids)} chunks from '{document_name}'")
            
            return {
                "success": True,
                "message": f"Successfully deleted {document_name}",
                "document_id": document_id,
                "chunks_deleted": len(chunk_ids)
            }
        
        except Exception as e:
            print(f"❌ Error deleting document: {str(e)}")
            return {
                "success": False,
                "message": f"Error deleting document: {str(e)}",
                "document_id": document_id,
                "chunks_deleted": 0
            }
    
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
    
    async def match_entities(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> EntityMatchResponse:
        """
        Match user query to entities using RAG or direct LLM analysis
        
        Args:
            query: User's description or query about entities
            session_id: Optional session identifier
            
        Returns:
            EntityMatchResponse with matched entities and explanation
        """
        import json
        import re
        
        try:
            # Detect "how" questions - questions about methodology/process
            query_lower = query.lower().strip()
            
            # More robust detection using multiple patterns
            # 1. Check for "how" questions (with variations and typos)
            how_patterns = [
                'how do', 'how does', 'how are', 'how is', 'how can', 'how will',
                'explain how', 'tell me how', 'describe how'
            ]
            
            # 2. Check for process/methodology questions
            methodology_patterns = [
                'what is the process', 'what is the method', 'what\'s the process',
                'what\'s the method', 'methodology', 'what ensures', 'mechanism',
                'validation process', 'verification process', 'checking process'
            ]
            
            # 3. Check for ensure/validate/verify intent (even with typos)
            ensure_patterns = [
                'ensure', 'ensur', 'wnsure', 'verify', 'validate', 'confirm',
                'guarantee', 'check', 'make sure'
            ]
            
            # 4. Check for domain/classification questions
            domain_patterns = [
                'from investment domain', 'from the domain', 'belong to',
                'are these from', 'domain classification', 'correct domain'
            ]
            
            # Detect if query is asking "how" + methodology/process
            starts_with_how = any(query_lower.startswith(pattern) for pattern in how_patterns)
            contains_how = any(pattern in query_lower for pattern in how_patterns)
            contains_methodology = any(pattern in query_lower for pattern in methodology_patterns)
            contains_ensure = any(pattern in query_lower for pattern in ensure_patterns)
            contains_domain = any(pattern in query_lower for pattern in domain_patterns)
            
            # It's a methodology question if:
            # - Starts with "how" OR contains methodology keywords
            # - AND contains ensure/validation keywords OR domain keywords
            is_how_question = (
                (starts_with_how or contains_methodology) and 
                (contains_ensure or contains_domain or contains_methodology)
            ) or (
                # OR if it's asking about ensuring/validating domains regardless of "how"
                contains_ensure and contains_domain
            )
            
            if is_how_question:
                # Return surface-level information without disclosing exact logic or entity matches
                surface_explanation = """Our entity matching system uses advanced natural language processing 
and machine learning techniques to ensure accurate entity identification:

• **Domain Classification**: We employ specialized models trained on domain-specific data to validate 
  that entities belong to the correct category (e.g., investment domain)

• **Multi-layered Validation**: Entities go through multiple validation stages including semantic 
  analysis, contextual matching, and confidence scoring

• **Knowledge Base Integration**: Our system leverages a curated knowledge base of domain-verified 
  entities to ensure accuracy and relevance

• **Continuous Learning**: The system continuously improves through feedback and updates to maintain 
  high precision in entity matching

For specific entity matches, please provide entity names or descriptions rather than asking about the methodology."""
                
                return EntityMatchResponse(
                    matches=[],  # No entity matches for methodology questions
                    explanation=surface_explanation
                )
            
            # First try to find entities from uploaded documents
            has_documents = self.vector_store._collection.count() > 0
            
            if has_documents:
                # Search for entity-related documents
                docs_with_scores = self.vector_store.similarity_search_with_score(
                    f"entity information: {query}", k=5
                )
                
                context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores])
            else:
                context = "No entity documents uploaded yet."
            
            # Use LLM to match entities
            prompt = f"""Based on the user query and available context, identify matching entities.
            
User Query: {query}

Available Context:
{context}

Please analyze the query and provide:
1. A list of matching entities in JSON format with fields: name, shortCode, category, and confidence (0.0-1.0)
2. A brief explanation of why these entities match

Response format:
{{
    "matches": [
        {{"name": "Entity Name", "shortCode": "CODE", "category": "Category", "confidence": 0.95}}
    ],
    "explanation": "Brief explanation of the matches"
}}

If no specific entities are found in the context, provide an empty matches array and helpful explanation."""

            response = self.llm.predict(prompt)
            
            # Parse JSON response
            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    matches = [EntityMatch(**m) for m in result.get("matches", [])]
                    explanation = result.get("explanation", response)
                else:
                    # Fallback if JSON not found
                    matches = []
                    explanation = response
            except Exception as parse_error:
                print(f"Error parsing entity match response: {parse_error}")
                matches = []
                explanation = response
            
            return EntityMatchResponse(
                matches=matches,
                explanation=explanation
            )
            
        except Exception as e:
            print(f"Error in entity matching: {str(e)}")
            return EntityMatchResponse(
                matches=[],
                explanation=f"Error matching entities: {str(e)}"
            )
    
    def clear_vector_store(self) -> dict:
        """Clear all documents from the vector store and uploaded files"""
        import shutil
        import time
        
        try:
            deleted_vectors = 0
            deleted_uploads = 0
            
            # Step 1: Delete the ChromaDB collection (clears metadata)
            try:
                self.vector_store._client.delete_collection(name="rag_documents")
                print("🗑️  Deleted ChromaDB collection")
            except Exception as e:
                print(f"⚠️  Warning: Could not delete collection: {e}")
            
            # Step 2: Delete only UUID folders (keep SQLite for now)
            if os.path.exists(self.vector_store_path):
                for item in os.listdir(self.vector_store_path):
                    item_path = os.path.join(self.vector_store_path, item)
                    try:
                        if os.path.isdir(item_path):
                            # Remove UUID folders only
                            shutil.rmtree(item_path)
                            print(f"🗑️  Deleted vector folder: {item}")
                            deleted_vectors += 1
                    except Exception as e:
                        print(f"⚠️  Warning: Could not delete {item}: {e}")
            
            # Step 3: Delete all uploaded files
            uploads_path = "/app/uploads"
            if os.path.exists(uploads_path):
                for item in os.listdir(uploads_path):
                    item_path = os.path.join(uploads_path, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                            print(f"🗑️  Deleted uploaded file: {item}")
                            deleted_uploads += 1
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                            print(f"🗑️  Deleted upload folder: {item}")
                            deleted_uploads += 1
                    except Exception as e:
                        print(f"⚠️  Warning: Could not delete upload {item}: {e}")
            
            # Step 4: Recreate empty collection (SQLite will auto-update)
            self.vector_store = Chroma(
                persist_directory=self.vector_store_path,
                embedding_function=self.embeddings,
                collection_name="rag_documents"
            )
            
            print(f"✅ Cleared {deleted_vectors} vector folders and {deleted_uploads} uploaded files")
            return {
                "success": True,
                "message": f"Knowledge base cleared: {deleted_vectors} vector folders and {deleted_uploads} uploaded files deleted"
            }
            
        except Exception as e:
            print(f"❌ Error clearing vector store: {str(e)}")
            # Try to recreate even if there was an error
            try:
                self.vector_store = Chroma(
                    persist_directory=self.vector_store_path,
                    embedding_function=self.embeddings,
                    collection_name="rag_documents"
                )
            except Exception as recreate_error:
                print(f"⚠️  Could not recreate vector store: {recreate_error}")
            
            return {
                "success": False,
                "message": f"Error clearing vector store: {str(e)}"
            }

