import chainlit as cl
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import HumanMessage
from uuid import uuid4
from src.agents.jcb_agent.index import runnable
from configs.index import REDIS_URL
import chainlit as cl
from langchain_core.messages import AIMessageChunk
from chainlit.types import ThreadDict
import chainlit as cl

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

  
@cl.on_chat_start
async def init():
    session_id = uuid4().hex
    history = RedisChatMessageHistory(url=REDIS_URL or "",session_id=session_id or "", key_prefix="jcb:")
    cl.user_session.set(key="session_id", value=session_id)
    cl.user_session.set(key="memory", value=history)
    message = cl.Message(content="Hello! I am JCB Promotion Assistant. I excel in finding good JCB deals. How can I help you today?")
    await message.send()

@cl.on_message
async def run_convo(message: cl.Message):
    history = cl.user_session.get(key="memory")
    cl.user_session.get(key="memory")
    history.add_user_message(HumanMessage(content=message.content)) # type: ignore
    stream = runnable.astream_events(
        input={"messages": history.messages[-4:]}, # type: ignore
        version="v2"
    )

    msg = cl.Message(content="")

    async for chunk in stream:
        if chunk["name"] == "researcher" and chunk["event"] == "on_chat_model_stream":
            if "data" not in chunk:
                continue
            if "chunk" not in chunk["data"]:
                continue
            data : AIMessageChunk = chunk["data"]["chunk"]
            await msg.stream_token(str(data.content))
        elif chunk["event"] == "on_tool_start":
            if "data" not in chunk:
                continue
            if "input" not in chunk["data"]:
                continue
            data = chunk["data"]["input"]

            async with cl.Step(name=chunk["name"], language="json") as step:
                step.output = data # type: ignore
        elif chunk["event"] == "on_tool_end":
            if "data" not in chunk:
                continue
            if "output" not in chunk["data"]:
                continue
            data = chunk["data"]["output"]
            async with cl.Step(name=chunk["name"], language="markdown") as step:
                step.output = data # type: ignore
        elif chunk["name"] == "recommendation_agent_output_parser" and chunk["event"] == "on_parser_end":
            if "data" not in chunk:
                continue
            if "output" not in chunk["data"]:
                continue
            data = chunk["data"]["output"]
            questions : list[str] = data.text # type: ignore
            actions = []
            for question in questions: # type: ignore
                actions.append(cl.Action(name=question, value=question, label=question))

            # res = await cl.AskActionMessage(
            #     content="You might want to ask:",
            #     actions=actions,
            #     author="JCB Agent",
            # ).send()

            # # TODO: fix user action as user input
            # if res:
            #     human_message = res["value"]
                
    await msg.send()

    history.add_ai_message(msg.content) # type: ignore

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    history = RedisChatMessageHistory(url=REDIS_URL or "",session_id=thread["id"] or "", key_prefix="jcb:")
    root_messages = [m for m in thread["steps"] if m["parentId"] == None] # type: ignore
    for message in root_messages:
        if message["type"] == "user_message": # type: ignore
            history.add_user_message(message["output"]) # type: ignore
        else:
            history.add_ai_message(message["output"]) # type: ignore

    cl.user_session.set("memory", history)
