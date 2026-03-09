from langchain_text_splitters import RecursiveCharacterTextSplitter
from helpers.exceptions import DocumentChunkingError
import logging


logger = logging.getLogger(__name__)

CHUNKING_THERESHOLD = 1500


# SPLITS THE INPUT TEXT INTO OVERLAPING CHUNKS FOR RAG PROCESSING.
# RETURNS LIST OF TEXT CHUNKS
def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150):

    # SMALL TEXTS ARE NOT CHUNKED
    if len(text) < CHUNKING_THERESHOLD:
        logger.info(
            f"Chunking bypassed due to small document size - length {len(text)}. Whole text returned."
        )
        return [text]

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_text(text)
    if len(chunks) == 0:
        raise DocumentChunkingError("Chunking process returned 0 rows.")
    logger.info(f"Text sucessifully chunked to {len(chunks)} chunks.")

    return chunks
