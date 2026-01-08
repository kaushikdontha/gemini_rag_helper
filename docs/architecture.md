# Architecture Diagram

## System Overview

The Document Q&A Assistant uses a Retrieval-Augmented Generation (RAG) architecture to answer questions based on uploaded documents.

## Data Flow Diagram

```mermaid
flowchart TB
    subgraph Frontend["Frontend (Streamlit)"]
        A[File Upload] --> B[Document List]
        C[Chat Input] --> D[Answer Display]
        D --> E[Citation Panel]
    end

    subgraph DocumentProcessing["Document Processing"]
        F[Format Detection] --> G[Text Extraction]
        G --> H[Sentence Splitting]
        H --> I[Token-Based Chunking]
        I --> J[Metadata Enrichment]
    end

    subgraph EmbeddingPipeline["Embedding Pipeline"]
        K[Google Embedding API] --> L[Vector Generation]
    end

    subgraph Storage["MongoDB Atlas"]
        M[(Document Chunks)]
        N[(Embeddings)]
        O[(Metadata)]
    end

    subgraph RAGEngine["RAG Query Engine"]
        P[Query Processing] --> Q[Similarity Search]
        Q --> R[Context Assembly]
        R --> S[Grounded Generation]
        S --> T[Citation Extraction]
    end

    subgraph LLM["Google Gemini"]
        U[Gemini 1.5 Flash]
    end

    A --> F
    J --> K
    L --> M
    L --> N
    J --> O

    C --> P
    N --> Q
    M --> R
    U --> S
    T --> D
```

## Component Details

### 1. Frontend (Streamlit)

| Component | Description |
|-----------|-------------|
| File Upload | Drag & drop interface for PDF, DOCX, TXT, MD files |
| Document List | Shows indexed documents with delete option |
| Chat Input | Text field for user questions |
| Answer Display | Formatted response from the assistant |
| Citation Panel | Expandable sources with document excerpts |

### 2. Document Processing

| Step | Description |
|------|-------------|
| Format Detection | Identifies file type by extension |
| Text Extraction | Uses PyPDF, python-docx, or native reading |
| Sentence Splitting | Regex-based sentence boundary detection |
| Token Chunking | 750 tokens per chunk with 100 token overlap |
| Metadata Enrichment | Adds document name, page/section info |

### 3. Embedding Pipeline

| Component | Details |
|-----------|---------|
| Model | Google Generative AI Embeddings |
| Model ID | `models/embedding-001` |
| Dimensions | 768 |
| Batch Processing | Per-chunk embedding generation |

### 4. MongoDB Storage

| Collection | Fields |
|------------|--------|
| document_chunks | content, embedding, metadata, chunk_id, token_count |

**Indexes:**
- `metadata.document_name` - For document filtering
- `vector_index` - Atlas Vector Search index on embeddings

### 5. RAG Query Engine

| Step | Description |
|------|-------------|
| Query Processing | Converts question to embedding |
| Similarity Search | Cosine similarity via Vector Search |
| Context Assembly | Formats top-K chunks with metadata |
| Grounded Generation | LLM generates answer from context only |
| Citation Extraction | Parses sources for display |

### 6. Google Gemini LLM

| Setting | Value |
|---------|-------|
| Model | `models/gemini-1.5-flash` |
| Temperature | 0.1 (factual) |
| System Prompt | Strict grounding + citation rules |

## Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant DP as Doc Processor
    participant MS as Mongo Store
    participant RE as RAG Engine
    participant G as Gemini API

    Note over U,G: Document Upload Flow
    U->>F: Upload Document
    F->>DP: Process File
    DP->>DP: Extract Text
    DP->>DP: Create Chunks
    DP->>G: Generate Embeddings
    G-->>DP: Embeddings (768d)
    DP->>MS: Store Chunks + Embeddings
    MS-->>F: Success
    F-->>U: Document Indexed

    Note over U,G: Question Answering Flow
    U->>F: Ask Question
    F->>RE: Query(question)
    RE->>G: Embed Question
    G-->>RE: Query Embedding
    RE->>MS: Similarity Search (top-K)
    MS-->>RE: Relevant Chunks
    RE->>RE: Format Context
    RE->>G: Generate Answer
    G-->>RE: Grounded Response
    RE-->>F: Answer + Sources
    F-->>U: Display Answer + Citations
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | Python 3.9+ |
| Document Processing | PyPDF, python-docx, tiktoken |
| Vector Store | MongoDB Atlas |
| Embeddings | Google Generative AI |
| LLM | Google Gemini 1.5 Flash |
| Framework | LangChain |
