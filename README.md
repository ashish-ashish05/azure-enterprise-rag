# Enterprise RAG

An enterprise Retrieval-Augmented Generation (RAG) application built with **Azure AI Search**, **Azure OpenAI**, **FastAPI**, and **Streamlit**.

The system ingests enterprise documents in PDF, DOCX, and XLSX formats, extracts metadata, creates embeddings, indexes chunks in Azure AI Search, retrieves relevant content with hybrid search, and generates grounded answers with source citations.

## Features

- PDF, DOCX, and XLSX ingestion
- Azure Blob Storage document source
- Document-family identification
- Document version and effective-date tracking
- Policy-owner metadata extraction
- Page-aware PDF chunking
- Whole-document chunking for DOCX/XLSX
- Overlapping word-based chunks
- Azure OpenAI embeddings
- Azure AI Search hybrid retrieval
- Metadata filtering
- Current-version resolution
- Grounded Azure OpenAI answers
- Source citations
- FastAPI REST API
- Streamlit web UI
- Multi-document RAG evaluation
- Safe document re-indexing without duplicate chunks

## Architecture

```text
Azure Blob Storage
        |
        v
Document Loaders (PDF / DOCX / XLSX)
        |
        v
Metadata Extraction
        |
        v
Document Chunking
        |
        v
Azure OpenAI Embeddings
        |
        v
Azure AI Search
        |
        +--------------------+
        |                    |
        v                    v
    FastAPI              Streamlit UI
        |
        v
    RAG Service
        |
        +--------------------+
        |                    |
        v                    v
 Azure AI Search       Azure OpenAI Chat
        |                    |
        +---------+----------+
                  |
                  v
          Grounded Answer
          + Source Citations
```

## Project Structure

```text
azure-enterprise-rag/
├── src/
│   └── enterprise_rag/
│       ├── api/
│       ├── application/
│       ├── config/
│       ├── domain/
│       ├── ingestion/
│       │   ├── chunking/
│       │   ├── loaders/
│       │   └── metadata/
│       ├── infrastructure/
│       │   ├── azure_openai/
│       │   ├── azure_search/
│       │   └── azure_storage/
│       └── rag/
├── scripts/
├── tests/
├── ui/
│   └── app.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- Azure subscription
- Azure Blob Storage
- Azure AI Search
- Azure OpenAI
- Azure OpenAI embedding deployment
- Azure OpenAI chat deployment

Main Python dependencies include:

- `azure-search-documents`
- `azure-storage-blob`
- `openai`
- `pypdf`
- `python-docx`
- `openpyxl`
- `fastapi`
- `uvicorn`
- `streamlit`
- `pydantic`

## Configuration

Create a `.env` file in the project root.

Example:

```env
AZURE_STORAGE_CONNECTION_STRING=your-storage-connection-string
AZURE_STORAGE_CONTAINER_NAME=your-container-name

AZURE_SEARCH_ENDPOINT=https://<search-service>.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_NAME=enterprise-rag-index

AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-embedding-deployment
AZURE_OPENAI_CHAT_DEPLOYMENT=your-chat-deployment
```

Never commit Azure credentials or `.env` to source control.

## Document Ingestion

Documents are uploaded to the configured Azure Blob Storage container.

The ingestion pipeline:

1. Lists documents in Blob Storage.
2. Determines the document family.
3. Selects the appropriate loader.
4. Extracts document text.
5. Extracts structured metadata.
6. Splits the document into chunks.
7. Generates embeddings with Azure OpenAI.
8. Deletes existing chunks for the document.
9. Uploads the new chunks and embeddings to Azure AI Search.

Supported formats:

```text
.pdf
.docx
.xlsx
```

### Run ingestion

```bash
source .venv/bin/activate
PYTHONPATH=src python3 scripts/index_one_document.py
```

A successful current run:

```text
============================================================
INGESTION SUMMARY
============================================================
Documents indexed: 11
Chunks indexed: 19
```

The exact chunk count depends on the documents and chunking configuration.

## Metadata

Documents can contain:

```text
document_family_id
document_version
effective_date
policy_owner
department
```

Example:

```text
Document family: ExpensePolicy
Document version: 5.1
Effective date: 2026-02-01
Policy owner: Corporate Controller
```

Metadata is stored with the indexed content and can be used during retrieval.

## Chunking

Default configuration:

```python
chunk_size = 700
chunk_overlap = 100
```

PDFs are chunked page-by-page when page information is available.

DOCX and XLSX files are chunked as whole documents because they do not provide PDF-style page metadata. Their page metadata is therefore:

```text
page = None
```

## Azure AI Search

The search layer supports:

- Text search
- Vector search
- Hybrid retrieval
- Metadata filters

The vector field is:

```text
content_vector
```

Metadata available to retrieval includes:

```text
document_family_id
department
document_version
effective_date
```

The system also supports current-version resolution.

## RAG Pipeline

```text
User Question
      |
      v
Query Embedding
      |
      v
Azure AI Search Hybrid Search
      |
      v
Relevant Chunks
      |
      v
Grounded Context
      |
      v
Azure OpenAI Chat
      |
      v
Answer + Source Citations
```

The generation layer is instructed to answer from retrieved enterprise context and avoid unsupported information.

If the documents do not contain enough information, the system can state that the information is not present in the provided documents.

## REST API

Start the API:

```bash
PYTHONPATH=src uvicorn enterprise_rag.api.main:app --reload
```

API base URL:

```text
http://127.0.0.1:8000
```

### Health check

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{
  "status": "ok"
}
```

### Query endpoint

```text
POST /api/v1/query
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/query   -H "Content-Type: application/json"   -d '{
    "question": "What is the expense policy?",
    "document_family_id": "ExpensePolicy"
  }'
```

Request:

```json
{
  "question": "What is the expense policy?",
  "document_family_id": "ExpensePolicy",
  "top_k": 5
}
```

`document_family_id` is optional.

Example response:

```json
{
  "question": "What is the expense policy?",
  "answer": "...",
  "sources": [
    {
      "source": "ExpensePolicy.pdf",
      "document_family_id": "ExpensePolicy",
      "document_version": "5.1",
      "effective_date": "2026-02-01T00:00:00Z",
      "page": 1,
      "chunk_index": 0
    }
  ]
}
```

## Web UI

Start the API first:

```bash
PYTHONPATH=src uvicorn enterprise_rag.api.main:app --reload
```

In another terminal:

```bash
streamlit run ui/app.py
```

Open:

```text
http://localhost:8501
```

The UI provides:

- Natural-language question input
- Optional document-family filter
- Top-k source selection
- Grounded answer display
- Source citations
- Document family
- Document version
- Effective date
- Page
- Chunk index

The document-family field can be left empty for natural-language questions.

## Example Questions

```text
What is the expense policy?
What are the employee benefits?
What is the leave policy?
What are the password requirements?
What is the travel policy?
What are the VPN requirements?
What does the NDA require?
What is the current pricing?
What are the discounts?
What are the vendor contract terms?
```

## Testing

### Filtered search

```bash
PYTHONPATH=src python3 scripts/test_filtered_search.py
```

### Current version

```bash
PYTHONPATH=src python3 scripts/test_current_version.py
```

### RAG test

```bash
PYTHONPATH=src python3 scripts/test_rag.py
```

### Multi-document RAG test

```bash
PYTHONPATH=src python3 scripts/test_multi_document_rag.py
```

Current validation:

```text
Passed: 10/10
Failed: 0/10
```

### RAG evaluation

```bash
PYTHONPATH=src python3 scripts/evaluate_rag.py
```

Current evaluation:

```text
Passed: 3/3
```

### Full test suite

```bash
PYTHONPATH=src python3 -m pytest tests -v
```

### Lint

```bash
PYTHONPATH=src ruff check .
```

## Current Test Corpus

The current corpus contains:

```text
Benefits.pdf
Discounts.xlsx
ExpensePolicy.pdf
LeavePolicy.pdf
NDA.docx
PasswordPolicy.docx
Pricing2025.pdf
Pricing2026.pdf
TravelPolicy.docx
VPNGuide.pdf
VendorContract.pdf
```

Current ingestion validation:

```text
Documents indexed: 11
Chunks indexed: 19
```

## Design Principles

### Grounded generation

Answers should be based on retrieved enterprise content and should not invent unsupported facts.

### Metadata-aware retrieval

Document metadata is part of the retrieval architecture, not just display information.

### Version awareness

A document family can have multiple versions and effective dates.

Example:

```text
Pricing2025
Pricing2026
```

The retrieval layer can distinguish between them and resolve current versions.

### Source traceability

Answers expose source information including:

```text
Source
Family
Version
Effective Date
Page
Chunk
```

This makes responses easier to audit.

## Re-indexing

Before indexing a document, existing chunks for that document are deleted.

This prevents duplicate chunks during re-indexing.

```text
Existing:
ExpensePolicy.pdf
 ├── chunk 0
 └── chunk 1

Re-index
     |
     v
Delete existing chunks
     |
     v
Index new chunks
 ├── chunk 0
 └── chunk 1
```

## Security

Do not commit:

```text
.env
Azure API keys
Azure Storage connection strings
Azure Search admin keys
Azure OpenAI API keys
```

For production, add authentication and authorization to the API and enforce document-level access controls appropriate to the organization.

## Current Project Status

```text
Document ingestion             ✅
PDF support                    ✅
DOCX support                   ✅
XLSX support                   ✅
Metadata extraction            ✅
Document family support        ✅
Version support                ✅
Effective-date support        ✅
Chunking                       ✅
Azure OpenAI embeddings        ✅
Azure AI Search hybrid search ✅
Current-version retrieval      ✅
Grounded generation            ✅
Source citations               ✅
Multi-document evaluation      ✅
FastAPI REST API               ✅
Streamlit UI                   ✅
```

Validated corpus:

```text
11 documents
19 chunks
10/10 multi-document RAG tests passing
3/3 evaluation questions passing
```

## Roadmap

Potential next steps:

- API authentication and authorization
- User/document access control
- Production logging
- Observability and telemetry
- Improved API error handling
- Automated ingestion jobs
- Document upload API
- Chat history
- Streaming responses
- Dockerization
- Azure deployment
- CI/CD
- Automated evaluation datasets
- Retrieval quality metrics
- Production security hardening
