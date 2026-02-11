from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.helpers.exceptions import DocumentChunkingError


# SPLITS THE INPUT TEXT INTO OVERLAPING CHUNKS FOR RAG PROCESSING.
# RETURNS LIST OF TEXT CHUNKS
def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_text(text)

    if len(chunks) == 0:
        raise DocumentChunkingError("Chunking process returned 0 rows.")

    return chunks
