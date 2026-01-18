from fastapi import FastAPI, UploadFile, File, HTTPException #type: ignore
from fastapi.middleware.cors import CORSMiddleware  #type: ignore
from pydantic import BaseModel  #type: ignore
from dotenv import load_dotenv  #type: ignore
from PyPDF2 import PdfReader  #type: ignore
import uvicorn #type: ignore
from typing import Any, Dict, List
from uuid import uuid4
from rag.main import build_documents, get_text_chunks, create_vector_store, answer_question
# from client.client import queue

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# maps unique session_id to vector store id
VECTOR_STORES: Dict[str, Any] = {}

# Extract raw page data
def extract_pages_from_uploads ( files: List[UploadFile] ) -> List[Dict[str, Any]]:
    pages = []
    for upload in files:
        try:
            # Reset pointer to start of file
            upload.file.seek(0)
            reader = PdfReader(upload.file) #PyPDF2
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF '{upload.filename}': {e}")

        # loop through each page, start just changes idx 0 to 1 (still reads all pg)
        # enumerate instead of range(len(pages))
        for page_index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if not page_text.strip():
                continue
            pages.append(
                {
                    "page_content": page_text,
                    "source": upload.filename,
                    "page_label": page_index,
                }
            )
    return pages
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
        pages = extract_pages_from_uploads(files) # list of dicts (raw pages)
        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No extractable text found in the uploaded PDFs",
            )
        # Build LangChain Documents in rag.main
        documents = build_documents(pages)
        chunks = get_text_chunks(documents)
        vector_store = create_vector_store(chunks)

        session_id = str(uuid4()) # generate unique session ID
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
        # job = queue.enqueue(answer_question, vector_store, payload.user_query)
        # answer = job.return_value()
        # while answer is None:
        #     answer = job.return_value()
        
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {e}")

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")