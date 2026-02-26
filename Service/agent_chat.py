from Service.agentpr import buildteam
import asyncio
from autogen_agentchat.messages import TextMessage



async def chat_with_agent(userquery):
    team = buildteam()
    last_text_answer = None
    await team.reset()
    async for msg in team.run_stream(task=userquery):
        if isinstance(msg, TextMessage):
             print(f"{msg.source}: {msg.content}")
             last_text_answer = msg.content
    return last_text_answer
    

