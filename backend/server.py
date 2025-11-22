from typing import List, Set, Tuple
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import config
from scripts.ingest import run_ingestion
from utils.reranker import rerank
from agent import get_chat_agent, _load_vector_store, reset_vector_store, build_mistral_llm

from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_mistralai import ChatMistralAI
from langchain_mistralai import MistralAIEmbeddings

app = FastAPI(title="FolderChat API", version="0.1.0")
# apply cors to allow requests from frontend
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# _vector_store = None
_llm_callable = None

class ChatRequest(BaseModel):
    question: str
    history: List[Tuple[str, str]] = []
    top_k: int = 8
    use_rerank: bool = config.USE_RERANKING

class ChatResponse(BaseModel):
    answer: str
    sources: Set[str]

class IngestRequest(BaseModel):
    input_dir: str = str(config.DATA_DIR)

class IngestResponse(BaseModel):
    message: str
    chunks_indexed: int


# def _load_vector_store() -> FAISS:
#     global _vector_store
#     if _vector_store is None:
#         # embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
#         embeddings = MistralAIEmbeddings(model="mistral-embed")
#         _vector_store = FAISS.load_local(
#             str(config.FAISS_INDEX_PATH), embeddings, allow_dangerous_deserialization=True
#         )
#     return _vector_store

# def build_mistral_llm():
#     llm = ChatMistralAI(
#         model=config.LLM_MODEL_NAME, #"ministral-8b-2410",
#         max_tokens=config.MAX_NEW_TOKENS,
#         temperature=config.TEMPERATURE,
#         top_p=config.TOP_P,
#     )
#     return llm.invoke

def _get_llm_callable():
    global _llm_callable
    if _llm_callable is None:
        _llm_callable = build_mistral_llm()
    return _llm_callable

SYSTEM_PROMPT = (
    "You are a helpful assistant. Use the retrieved context delimited by <CTX></CTX> to answer the user's question. "
    "If the answer is not contained in the context, say you don't have enough information. "
    "Cite sources by their basename and page/sheet when available."
)


def _format_docs(docs) -> str:
    blocks = []
    for d in docs:
        meta = d.metadata or {}
        source = Path(meta.get("source", "unknown")).name
        page = meta.get("page")
        sheet = meta.get("sheet")
        tag = f"source={source}" + (f" page={page}" if page is not None else "") + (f" sheet={sheet}" if sheet else "")
        blocks.append(f"[{tag}]\n{d.page_content}")
    return "\n\n".join(blocks)


def _build_messages(history: List[Tuple[str, str]], question: str, context: str = "", mode:str = "chat") -> str:
    # history_text = "\n".join(f"{role}: {msg}" for role, msg in history[-10:])
    # return (
    #     f"{SYSTEM_PROMPT}\n<CTX>\n{context}\n</CTX>\nConversation History:\n{history_text}\n\nUser Question: {question}\nAssistant:"
    # )
    if mode == "chat":
        messages = [("system", SYSTEM_PROMPT),]
        if history and len(history)>0:
            messages.extend(history[:config.LAST_FEW_MESSAGES])
        messages.append(("user", f"<CTX>\n{context}\n</CTX>\nQuestion: {question}"))
    else:
        messages = []
        if history and len(history)>0:
            messages.extend(history[:config.LAST_FEW_MESSAGES])
        messages.append(("user", question))
    return messages

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not Path(config.FAISS_INDEX_PATH).exists():
        raise HTTPException(status_code=400, detail="Vector index missing. Run ingestion first.")
    store = _load_vector_store()
    # retriever = store.as_retriever(search_kwargs={"k": req.top_k})
    docs = store.search(req.question, search_type="similarity", k=req.top_k)
    if req.use_rerank and config.USE_RERANKING:
        docs = rerank(req.question, docs)
    context = _format_docs(docs)
    prompt = _build_messages(req.history, req.question, context)
    llm = _get_llm_callable()
    answer = llm.invoke(prompt)
    sources = set()
    for d in docs:
        meta = d.metadata or {}
        sources.add(Path(meta.get("source", "unknown")).name)
    return ChatResponse(answer=str(answer.content), sources=sources)

@app.post("/agent_chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    print("[Agent Chat] Received question:", req.question)
    if not Path(config.FAISS_INDEX_PATH).exists():
        raise HTTPException(status_code=400, detail="Vector index missing. Run ingestion first.")
    messages = _build_messages(req.history, req.question, mode="agent")
    agent = get_chat_agent()
    resp = agent.invoke({"messages": messages})
    answer = resp["messages"][-1].content
    return ChatResponse(answer=str(answer), sources=[])

@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    input_dir = Path(req.input_dir)
    if not input_dir.exists():
        raise HTTPException(status_code=404, detail="Input directory not found.")
    # Run ingestion pipeline
    resp = run_ingestion(input_dir)
    # After ingestion reset vector store so next chat reloads
    # global vector_store
    # _vector_store = None
    reset_vector_store()
    # We cannot easily know chunk count here without refactoring; return -1 placeholder
    return IngestResponse(message="Ingestion completed", chunks_indexed=resp["total_chunks"])

@app.get("/health")
def health():
    return {"status": "ok"}

# Run with: uvicorn server:app --host localhost --port 8000
