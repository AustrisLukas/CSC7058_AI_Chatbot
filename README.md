AI Document Q&A Chatbot – README

1. Project Overview
   This project is a Streamlit-based AI Document Q&A Chatbot that allows users to upload documents or provide URLs and ask questions about their content. The system uses a Retrieval-Augmented Generation (RAG) pipeline, combining OpenAI embeddings, FAISS vector storage, and prompt-based response generation to produce context-aware answers grounded in the source material.

2. Key Features

- Document upload (PDF, DOCX, CSV, XLSX, PPTX)
- URL-based text extraction
- Semantic search using FAISS
- Context-aware responses using OpenAI API
- Summary generation
- Multilingual response support
- Configurable response style and creativity

3. Project Structure
   main.py - Streamlit application entry point
   helpers.py - Shared utility functions and wrappers
   pipeline.py - Core RAG pipeline (run_rag_pipeline)
   document_pipeline.py - Document ingestion pipeline (build_doc_pipeline)

services/
openai_service.py - OpenAI API interaction (responses, embeddings)
embedding_service.py - Embedding logic (embed_query, embed_documents)

vector_store/
faiss_store.py - FAISS vector store implementation (add/search)

tests/
test\_\*.py - Unit tests for core components

4. Installation Instructions
1. Clone the repository:
   git clone <https://github.com/AustrisLukas/CSC7058_AI_Chatbot>

1. Navigate into the project folder:
   cd CSC7058_AI_CHATBOT

1. Create a virtual environment:
   python -m venv venv

1. Activate the environment (Mac/Linux):
   source venv/bin/activate

1. Install dependencies:
   pip install -r requirements.txt

1. Environment Variables
   Create a secrets.toml file and set the following variable:

OPENAI_API_KEY=your_api_key_here

6. Running the Application
   Start the Streamlit app using:

streamlit run app/main.py

The application will open in your browser.

7. System Workflow (High-Level)
   1. User uploads a document or provides a URL
   2. Text is extracted using the document pipeline (build_doc_pipeline)
   3. For large documents, text is split into chunks
   4. Embeddings are generated using OpenAI
   5. Embeddings are stored in FAISS vector store
   6. User submits a query
   7. Query is embedded (embed_query)
   8. Relevant chunks are retrieved using FAISS similarity search
   9. Prompt is constructed (build_prompt)
   10. Response is generated using OpenAI
   11. Output is parsed and displayed in the UI

8. Testing
   Run unit tests using:

pytest

Tests cover:

- Document extraction
- Chunking logic
- Embedding handling (mocked API)
- FAISS vector operations
- RAG pipeline decision logic

9. Key Dependencies

- streamlit
- openai
- faiss-cpu
- pytest
- pandas
- pypdf
- python-docx
- trafilatura

Full dependency list is provided in requirements.txt.

10. Limitations

- Dependent on OpenAI API availability and latency
- No retry mechanism for API/network failures
- Fixed context handling (no user-defined context budget)
- Limited model selection (single model configuration)

11. Future Improvements

- Add retry handling for API failures
- Support multiple AI model selection
- Allow user-defined context budget
- Introduce persistent vector storage
- Improve retrieval optimisation and ranking
