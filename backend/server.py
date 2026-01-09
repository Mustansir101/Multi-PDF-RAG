from fastapi import FastAPI, UploadFile, File, HTTPException #type: ignore
from fastapi.middleware.cors import CORSMiddleware  #type: ignore
from pydantic import BaseModel  #type: ignore
import uvicorn #type: ignore
from typing import Any, Dict, List
from uuid import uuid4

from dotenv import load_dotenv  #type: ignore
from PyPDF2 import PdfReader  #type: ignore
from langchain_core.documents import Document  #type: ignore

from main import get_text_chunks, create_vector_store, answer_question

load_dotenv()

app = FastAPI()

# Allow the browser-based Next.js frontend to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep vector stores server-side; return a session id to the client.
VECTOR_STORES: Dict[str, Any] = {}


def extract_documents_from_uploads(files: List[UploadFile]) -> List[Document]:
    documents: List[Document] = []

    for upload in files:
        try:
            upload.file.seek(0)
            reader = PdfReader(upload.file)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF '{upload.filename}': {e}")

        for page_index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if not page_text.strip():
                continue
            documents.append(
                Document(
                    page_content=page_text,
                    metadata={"source": upload.filename, "page_label": page_index},
                )
            )

    return documents


class AskQuestionRequest(BaseModel):
    session_id: str
    user_query: str

@app.post("/process-pdfs")
async def upload_pdfs(
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    
    try:
        documents = extract_documents_from_uploads(files)
        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No extractable text found in the uploaded PDFs (scanned PDFs may need OCR).",
            )

        chunks = get_text_chunks(documents)
        vector_store = create_vector_store(chunks)

        session_id = str(uuid4())
        VECTOR_STORES[session_id] = vector_store

        return {
            "message": "PDFs processed successfully.",
            "session_id": session_id,
            "files": [f.filename for f in files],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDFs: {e}")
    
@app.post("/ask-question")
async def ask_question(payload: AskQuestionRequest):
    try:
        vector_store = VECTOR_STORES.get(payload.session_id)
        if vector_store is None:
            raise HTTPException(status_code=404, detail="Unknown session_id. Process PDFs again.")

        answer = answer_question(vector_store, payload.user_query)
        return {"answer": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {e}")


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")