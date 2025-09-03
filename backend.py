from fastapi import FastAPI,HTTPException
import uuid
import requests
from pydantic import BaseModel

DEEPSEEK_API_KEY="sk-e4a3846d6f064c17988d59f4900aefa7"

app=FastAPI()
tokens={}
MAX_TOKENS=75
class AskRequest(BaseModel):
    token:str
    question:str
    tokens_used:int
@app.get("/generate_link")
def generate_link():
    """Generate a temporary demo link with only quota."""
    token=str(uuid.uuid4())
    tokens[token]={
        "used":0,
        "max":MAX_TOKENS
    }
    return {"token":token}
@app.post("/ask")
def ask(req:AskRequest):
    token=req.token
    question=req.question
    tokens_used=req.tokens_used
    if token not in tokens:
        raise HTTPException(status_code=400,detail="Invalid or expired token")
    remaining=tokens[token]["max"]-tokens[token]["used"]
    if remaining<=0:
        raise HTTPException(status_code=403,detail="Quota exceeded")
    if tokens_used>remaining:
        raise HTTPException(status_code=403,detail="Token quota will be exceeded with this query")
    response=requests.post("https://api.deepseek.com/v1/chat/completions",
    headers={"Authorization":f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type":"application/json"},
    json={
        "model":"deepseek-chat",
        "messages":[
            {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content":question}
        ],
        "stream":False
    })
    if response.status_code==200:
        data=response.json()
        deepseek_answer=data["choices"][0]["message"]["content"]
        tokens[token]["used"]+=tokens_used
        remaining=tokens[token]["max"]-tokens[token]["used"]
        return {"answer":deepseek_answer,"tokens_remaining":remaining}
    else:
        raise HTTPException(status_code=500,detail=f"Deepseek error:{response.text}")