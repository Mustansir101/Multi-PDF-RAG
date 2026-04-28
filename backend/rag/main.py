import os
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from typing import List, Dict, Any
import google.generativeai as genai
from openai import OpenAI
from google.genai import types

# QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_URL = os.getenv("QDRANT_URL", "https://qdrant-8wg1.onrender.com")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "MultiPDFChat")

# converts list of raw page dicts to list of LangChain Documents
def build_documents(pages: List[Dict[str, Any]]) -> List[Document]:
    docs: List[Document] = []
    for pg in pages:
        content = pg.get("page_content", "") # p["page_content"]
        if not isinstance(content, str) or not content.strip():
            continue
        metadata = {
            "source": pg["source"],
            "page_label": pg["page_label"],
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs

# document is tuple of (page_content, metadata) where metadata is a dict
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
        model = "gemini-embedding-001",
        google_api_key = google_api_key,
        config = types.EmbedContentConfig(output_dimensionality=2048)
    )

def create_vector_store(chunks):
    embedding_model = get_embedding_model()

    vector_store = QdrantVectorStore.from_documents(
        documents = chunks,
        embedding = embedding_model,
        url = QDRANT_URL,
        batch_size = 10,
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

    SYSTEM_PROMPT = f"""You are an AI assistant that generates questions based only on the provided context from PDF documents, including page_contents and page_numbers.

    Your task is to create clear, relevant, and meaningful questions that can be answered using the given context.

    Rules:
    - Generate questions strictly from the context. Do not use outside knowledge.
    - Questions should test understanding, not be trivial or copied directly.
    - Include a mix of question types such as factual, conceptual, and analytical when possible.
    - For each question, mention the page number it is derived from.
    - Do NOT provide answers.

    If the context is insufficient to generate questions, respond with:
    "I am sorry, I could not generate questions from the provided document."

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