from pathlib import Path
from langchain_mistralai import ChatMistralAI
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import config
# from utils.sql_db import get_db_connection

from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri(database_uri=f"sqlite:///{config.DB_PATH}")

_vector_store = None
def _load_vector_store() -> FAISS:
    global _vector_store
    if _vector_store is None:
        # embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
        embeddings = MistralAIEmbeddings(model="mistral-embed")
        _vector_store = FAISS.load_local(
            str(config.FAISS_INDEX_PATH), embeddings, allow_dangerous_deserialization=True
        )
    return _vector_store

def reset_vector_store():
    global _vector_store
    _vector_store = None

def build_mistral_llm():
    llm = ChatMistralAI(
        model=config.LLM_MODEL_NAME, #"ministral-8b-2410",
        max_tokens=config.MAX_NEW_TOKENS,
        temperature=config.TEMPERATURE,
        top_p=config.TOP_P,
    )
    return llm
def _format_docs(docs) -> str:
    blocks = []
    for d in docs:
        meta = d.metadata or {}
        source = Path(meta.get("source", "unknown")).name
        page = meta.get("page")
        table_name = meta.get("table_name")
        tag = (f" table_name={table_name}" if table_name else "") + f"source={source}" + (f" page={page}" if page is not None else "")
        blocks.append(f"[{tag}]\n{d.page_content}")
    return "\n\n".join(blocks)

@tool("vector_search_tool", description="Use to fetch relevant data from the existing knowledge base")
def vector_search_tool(query:str):
    """Tool to search for relevant documents in the vector store."""

    vector_store = _load_vector_store()
    docs = vector_store.similarity_search(query, k=5)
    return _format_docs(docs)

# @tool
# def format_response_as_markdown(answer: str) -> str:
#     """Tool to format the final answer as markdown."""
#     return f"```markdown\n{answer}\n```"

# def generate_sql_query_tool(question: str):
#     """Tool to generate SQL query based on the question."""
#     # Placeholder implementation
#     pass
SYSTEM_PROMPT = (
    "You are a helpful assistant. Use the tools available to answer the user query. Retry the tools if the output is not sufficient or valid. "
    "Primarily use the `vector_search_tool` to fetch relevant context from the knowledge base. The  take a call intelligently uou need to use the SQL tools to fetch data from the SQL database. "
    "When using SQL tools, get table name from `vector_search_tool` results, make sure to generate syntactically correct SQL queries. and only return the final answer after executing the SQL queries. "
    "ALWAYS validate the response from the SQL tools, if the result is not correct, retry generating the SQL query and execute again. "
    "If the SQL tools do not return any relevant data, rely on the `vector_search_tool` results to answer the question. "
    "ALWAYS Cite sources by their basename and page/sheet when available at the end of your answer."
    "ALWAYS format your final answer in MARKDOWN and choose the best display structure for the answer (for example section-wise or tables for tabular data etc)."
    "When you DONOT KNOW the answer, just say that you don't have enough information. NEVER make up the answer. "
    "FINAL STEP: REMEMBER to return ONLY the final answer as a string in MARKDOWN format."
)
def get_chat_agent():
    llm = build_mistral_llm()
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = sql_toolkit.get_tools()
    tools.append(vector_search_tool)
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )
    # agent.stat = None  # reset state
    return agent