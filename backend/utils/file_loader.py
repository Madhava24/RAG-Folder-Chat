from pathlib import Path
from typing import List
import pandas as pd
from langchain_core.documents import Document
from pypdf import PdfReader
from docx import Document as DocxDocument

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".csv", ".xlsx", ".txt"}

TABLES = []

def get_tables() -> List[tuple[str, pd.DataFrame]]:
    return TABLES

def load_txt(path: Path) -> List[Document]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        text = path.read_text(errors="ignore")
    return [Document(page_content=text, metadata={"source": str(path), "file_type": "txt"})]


def load_pdf(path: Path) -> List[Document]:
    docs: List[Document] = []
    reader = PdfReader(str(path))
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        docs.append(Document(page_content=text, metadata={"source": str(path), "file_type": "pdf", "page": i}))
    return docs


def load_docx(path: Path) -> List[Document]:
    d = DocxDocument(str(path))
    paragraphs = [p.text.strip() for p in d.paragraphs if p.text.strip()]
    content = "\n".join(paragraphs)
    return [Document(page_content=content, metadata={"source": str(path), "file_type": "docx"})]


def load_csv(path: Path) -> List[Document]:
    df = pd.read_csv(path)
    # Represent each row as a simple pipe-separated string
    rows = []
    for _, row in df.iterrows():
        row_str = " | ".join(f"{col}={row[col]}" for col in df.columns)
        rows.append(row_str)
    content = "\n".join(rows)
    table_name = path.stem.replace(" ", "_").lower()
    TABLES.append((table_name, df))
    # head_content = df.head(8).to_markdown(index=False)
    return [Document(page_content=content, metadata={"source": str(path), "table_name": table_name, "file_type": "csv", "rows": len(df)})]


def load_xlsx(path: Path) -> List[Document]:
    docs: List[Document] = []
    xls = pd.ExcelFile(path)
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        rows = []
        for _, row in df.iterrows():
            row_str = " | ".join(f"{col}={row[col]}" for col in df.columns)
            rows.append(row_str)
        content = "\n".join(rows)
        docs.append(Document(page_content=content, metadata={"source": str(path), "table_name": table_name, "file_type": "xlsx", "sheet": sheet, "rows": len(df)}))
        table_name = f"{path.stem.replace(' ', '_').lower()}_{sheet.replace(' ', '_').lower()}"
        TABLES.append((table_name, df))
        # head_content = df.head(8).to_markdown(index=False)
    return docs

LOADER_MAP = {
    ".txt": load_txt,
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".csv": load_csv,
    ".xlsx": load_xlsx,
}


def load_documents(input_dir: str) -> List[Document]:
    """Traverse input_dir and load all supported documents into LangChain Documents."""
    root = Path(input_dir)
    if not root.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    all_docs: List[Document] = []
    # for path in root.rglob('*'):
    for path in root.iterdir():
        if path.is_file():
            ext = path.suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                loader = LOADER_MAP.get(ext)
                if loader:
                    try:
                        docs = loader(path)
                        all_docs.extend(docs)
                    except Exception as e:
                        # Skip problematic files but record minimal metadata
                        # all_docs.append(Document(page_content="", metadata={"source": str(path), "file_type": ext, "error": str(e)}))
                        print(f"[Warning] Failed to load {path.absolute()}: {e}")
    return all_docs

__all__ = ["load_documents", "SUPPORTED_EXTENSIONS"]
