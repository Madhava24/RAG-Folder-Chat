from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DIR = BASE_DIR / "vectorstore"
DB_PATH = BASE_DIR / "database" / "data.db"

"""Central configuration for FolderChat RAG system and advanced features."""

# Embedding model (efficient, open-source). Alternatives: "sentence-transformers/all-MiniLM-L6-v2", "BAAI/bge-small-en-v1.5"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Primary HF LLM model (Mistral instruct). Auto-downloaded via transformers.
LLM_MODEL_NAME = "ministral-8b-2410" #"mistralai/Mistral-7B-Instruct-v0.2"


# Quantized model support (llama.cpp). Provide path to a local GGUF file to enable.
USE_LLAMA_CPP = False
LLAMA_CPP_MODEL_PATH = "./models/mistral-7b-instruct.Q4_K_M.gguf"  # adjust to actual path
LLAMA_CPP_N_CTX = 4096
LLAMA_CPP_N_THREADS = 8  # tune per your CPU

# Reranking configuration
USE_RERANKING = True
RERANK_MODEL_NAME = "BAAI/bge-reranker-base"  # cross-encoder
RERANK_TOP_K = 4  # number of reranked docs retained

# Generation parameters
MAX_NEW_TOKENS = 3000
TEMPERATURE = 0
TOP_P = 1
LAST_FEW_MESSAGES=5  # for prompt context window

# Chunking parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Vector store filename
FAISS_INDEX_PATH = VECTOR_DIR / "faiss_index"

__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "VECTOR_DIR",
    "EMBEDDING_MODEL_NAME",
    "LLM_MODEL_NAME",
    "USE_LLAMA_CPP",
    "LLAMA_CPP_MODEL_PATH",
    "LLAMA_CPP_N_CTX",
    "LLAMA_CPP_N_THREADS",
    "USE_RERANKING",
    "RERANK_MODEL_NAME",
    "RERANK_TOP_K",
    "MAX_NEW_TOKENS",
    "TEMPERATURE",
    "TOP_P",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "FAISS_INDEX_PATH",
]
