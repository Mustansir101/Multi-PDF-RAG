from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel  
from dotenv import load_dotenv
import uvicorn 
from typing import Any, Dict
from rag.main import answer_question

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# maps unique session_id to vector store id
VECTOR_STORES: Dict[str, Any] = {}

# Extract raw page data
class AskQuestionRequest(BaseModel):
    user_query: str
    
@app.post("/ask-question")
async def ask_question(payload: AskQuestionRequest):
    try:
        answer = answer_question(payload.user_query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {e}")

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")