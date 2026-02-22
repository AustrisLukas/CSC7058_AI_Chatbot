from helpers import data_utils
from backend.ingestion.chunking import chunk_text
from backend.embeddings.embedder import embed_chunks
from backend.vector_store.faiss_store import FAISSStore
import logging

logger = logging.getLogger(__name__)


def extract_text(file):

    extracted_text = ""
    file_type = data_utils.detect_file_type(file)
    logger.info(f"detected file format -> {file_type}")

    if file_type == "pdf":
        extracted_text = data_utils.extract_pdf(file)

    elif file_type == "word":
        extracted_text = data_utils.extract_docx(file)

    elif file_type == "csv":
        extracted_text = data_utils.extract_csv(file)

    elif file_type == "excel":
        extracted_text = data_utils.extract_excel(file)
    elif file_type == "powerpoint":
        print("extract pptx")
        extracted_text = data_utils.extract_pptx(file)

    return extracted_text


def build_doc_pipeline(file, on_step=None):

    def step(msg):
        if on_step:
            on_step(msg)

    step("Extracting text from document...")
    extracted_text = extract_text(file)
    logger.info("text succesfully extracted from document")

    step("Chunking extracted text...")
    chunked_text = chunk_text(extracted_text)
    logger.info("text succesfully chunked")

    step("Embedding text chunks...")
    chunk_embeddings = embed_chunks(chunked_text)
    logger.info("text chunks succesfully embedded")

    step("Initialising vector database...")
    # Initialise FAISS store
    store = FAISSStore(dimension=len(chunk_embeddings[0]))
    store.add(chunk_embeddings, chunked_text)
    logger.info("vector database succesfully created")

    return extracted_text, chunked_text, chunk_embeddings, store
