# Legal AI RAG System

FastAPI-based Legal AI Retrieval-Augmented Generation (RAG) System.

## Getting Started

### Prerequisites
- Python 3.8+
- Poetry

### Installation

```bash
poetry install
```

### Running the Application

```bash
poetry run uvicorn main:app --reload --port 8000
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check