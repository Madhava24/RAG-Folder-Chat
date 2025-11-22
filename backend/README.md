# FolderChat RAG System

An end-to-end Retrieval-Augmented Generation (RAG) pipeline for chatting with mixed-format local documents (PDF, DOCX, CSV, XLSX, TXT) using open-source components: LangChain, FAISS, Sentence-Transformers embeddings, and Mistral Instruct LLM.

## Architecture Overview
1. Ingestion
   - Load raw files (`utils/file_loader.py`) producing LangChain `Document` objects with rich metadata (page, sheet, rows).
   - Chunk text (`utils/chunker.py`) via recursive character splitter (configurable size & overlap).
   - Embed chunks with `sentence-transformers/all-MiniLM-L6-v2` (configurable in `config.py`).
   - Build FAISS index and persist locally (`scripts/ingest.py`).
2. Retrieval + Generation
   - Load FAISS index and embeddings (`chat.py` / `server.py`).
   - Retrieve top-k relevant chunks per query.
   - Optional reranking pass with cross-encoder (`utils/reranker.py`).
   - Provide top reranked chunks as context to Mistral 7B Instruct or quantized llama.cpp model.
   - Maintain conversational history manually in advanced chat mode.

## Components
- `config.py`: Central configuration (paths, model names, chunk params, device detection).
- `utils/file_loader.py`: Unified loading for supported file types.
- `utils/chunker.py`: Document chunking logic.
- `scripts/ingest.py`: Pipeline orchestration to produce vector store.
- `chat.py`: Interactive RAG chat loop.
- `read_folder.py`: Quick CLI to list documents and optionally trigger ingestion.

## Setup
```powershell
# (Optional) Create virtual environment
python -m venv .venv
./.venv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Ingest Documents
Place documents inside the `data/` directory (you can create subdirectories). Then run:
```powershell
python scripts/ingest.py --input-dir data
```
This creates a FAISS index under `vectorstore/faiss_index/`.

Alternatively list files + ingest in one go:
```powershell
python read_folder.py --ingest
```

## Start Chat
Ensure the FAISS index exists, then launch:
```powershell
python chat.py
```
Type questions referencing your documents. Use `exit` to quit.

### FastAPI Service
Run the API server:
```powershell
uvicorn server:app --reload
```
Endpoints:
- `POST /ingest` body: `{ "input_dir": "data" }`
- `POST /chat` body: `{ "question": "...", "history": [["User", "Hi"]], "top_k": 8, "use_rerank": true }`
- `GET /health` simple status.

### Reranking
Cross-encoder reranking (model `BAAI/bge-reranker-base`) improves relevance by scoring query-chunk pairs. Toggle via `USE_RERANKING` in `config.py` or per-request `use_rerank` in API.

### Quantized Model Option
Set `USE_LLAMA_CPP = True` and adjust `LLAMA_CPP_MODEL_PATH` to a local GGUF file (e.g. downloaded Mistral quantized). Install `llama-cpp-python` (already in requirements). Adjust `LLAMA_CPP_N_THREADS` per CPU and reduce `MAX_NEW_TOKENS` if memory constrained.

## Configuration Adjustments
Edit `config.py` to change:
- Embedding model: e.g. `BAAI/bge-small-en-v1.5` for better semantic performance.
- LLM model: keep a Mistral variant (`mistralai/Mistral-7B-Instruct-v0.2`).
- Chunk parameters: `CHUNK_SIZE`, `CHUNK_OVERLAP`.
- Reranking: `USE_RERANKING`, `RERANK_MODEL_NAME`, `RERANK_TOP_K`.
- Quantized model: `USE_LLAMA_CPP`, path + context size + threads.

## Extensibility
- Add new loaders (e.g. HTML, Markdown) by extending `SUPPORTED_EXTENSIONS` and `LOADER_MAP` in `file_loader.py`.
- Swap vector store: Use `Chroma` or `Qdrant` with minimal changes in ingestion & chat scripts.
- Add re-ranking: Insert a second-pass scoring (e.g. using `bge-reranker-base`) before sending context to LLM.
- Caching: Integrate `langchain` cache for repeated queries.
- Streaming: Implement token streaming via websockets or SSE in API.
- Guardrails: Add simple PII or hallucination detection before returning answers.

## Security & Privacy
All processing is local; no proprietary / closed APIs are used. Large models may require GPU VRAM (~7B). Use quantized GGUF versions with llama.cpp or ollama if memory constrained (would need minor wrapper changes).

## Troubleshooting
- Missing packages: Ensure `pip install -r requirements.txt` succeeded.
- CUDA OOM: Switch to CPU or quantized model; reduce `max_new_tokens`.
- Empty answers: Increase `k` in `chat.py` retriever or reduce chunk size.

## License
All utilized models and libraries are open-source; review respective repositories for their specific licenses.

## Next Ideas
- Add FastAPI service endpoint wrapping retrieval & generation.
- Implement streaming token output.
- Persist conversation state to disk or a lightweight database.

Happy chatting with your documents!
