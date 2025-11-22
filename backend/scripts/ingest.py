from pathlib import Path
from langchain_mistralai import MistralAIEmbeddings
from tqdm import tqdm

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from utils.file_loader import load_documents, get_tables
from utils.chunker import chunk_documents
from utils.sql_db import create_tables_from_df
import config


def build_vector_store(docs):
    # embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
    embeddings = MistralAIEmbeddings(model="mistral-embed")
    return FAISS.from_documents(docs, embeddings)


def persist_store(store: FAISS, path: Path):
    path.mkdir(parents=True, exist_ok=True)
    store.save_local(str(path))


def run_ingestion(input_dir: Path):
    print(f"[Ingest] Loading documents from {input_dir} ...")
    raw_docs = load_documents(str(input_dir))
    print(f"[Ingest] Loaded {len(raw_docs)} raw document units.")

    print("[Ingest] Chunking documents ...")
    chunks = chunk_documents(
        raw_docs,
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    print(f"[Ingest] Created {len(chunks)} chunks.")

    print("[Ingest] Building embeddings + FAISS index ...")
    store = build_vector_store(chunks)
    print("[Ingest] Persisting index ...")
    persist_store(store, config.FAISS_INDEX_PATH)
    print(f"[Ingest] Done. Index stored at {config.FAISS_INDEX_PATH}")
    tables = get_tables()
    if tables:
        print("[Ingest] Creating SQL tables from dataframes ...")
        table_count  = create_tables_from_df(tables)
    return {"total_files": len(raw_docs), "total_chunks": len(chunks), "table_count": table_count}
