from fastapi import APIRouter
from Service.agent_chat import chat_with_agent
from Models.userquery import userquery


router  = APIRouter(prefix="/chat",tags=["Chat"])

@router.post("/chat")
async def chat(question:userquery):
    agent_result = await chat_with_agent(question.userq)
    return {"response":agent_result}

