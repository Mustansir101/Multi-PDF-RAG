import streamlit as st #type: ignore
import os
from dotenv import load_dotenv #type: ignore
from PyPDF2 import PdfReader #type: ignore
from langchain_text_splitters import CharacterTextSplitter #type: ignore
from langchain_google_genai import GoogleGenerativeAIEmbeddings #type: ignore
from langchain_qdrant import QdrantVectorStore #type: ignore
from langchain_core.documents import Document #type: ignore
from openai import OpenAI #type: ignore

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "MultiPDFChat")

def get_pdf_documents(pdf_docs):
    # Extract text and create Document objects with metadata
    documents = []
    for pdf in pdf_docs:
        reader = PdfReader(pdf)  # page wise
        source_name = getattr(pdf, "name", "uploaded.pdf")
        for page_index, page in enumerate(reader.pages, start=1): # enumerate?
            page_text = page.extract_text() or ""
            if not page_text.strip():
                continue
            documents.append(
                Document(
                    page_content=page_text,
                    metadata={
                        "source": source_name,
                        "page_label": page_index,
                    },
                )
            )
    return documents

def get_text_chunks(documents):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    # splitting documents instead of raw text
    chunks = splitter.split_documents(documents)
    return chunks

def get_embedding_model():
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("Missing GOOGLE_API_KEY")
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=google_api_key,
    )

def create_vector_store(chunks):
    embedding_model = get_embedding_model()

    vector_store = QdrantVectorStore.from_documents(
        documents = chunks,
        embedding = embedding_model,
        url = QDRANT_URL,
        collection_name = QDRANT_COLLECTION
    )
    return vector_store

def answer_question(vector_store, user_query):
    search_res = vector_store.similarity_search(query=user_query)

    context = "\n\n".join([
        (
            f"Page Content: {res.page_content}\n"
            f"Page Number: {res.metadata.get('page_label', 'N/A')}\n"
            f"File Location: {res.metadata.get('source', 'N/A')}"
        )
        for res in search_res
    ])

    SYSTEM_PROMPT = f"""You are a helpful AI assistant who answers user queries based only on the available context retrieved from the PDF files, along with page_contents and page_numbers.
    
    You should only answer based on the following context and navigate the user to the relevant page number for more details.
    
    If the answer is not found in the context, respond with: "I am sorry, I could not find any relevant information in the document provided."
    
    Context:
    {context}
    """

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError(
            "Missing GEMINI_API_KEY. Add it to your .env file (or Streamlit secrets)."
        )

    client = OpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
    )

    return response.choices[0].message.content

