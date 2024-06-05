import chainlit as cl
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import HumanMessage
from uuid import uuid4
from src.agents.jcb_agent.index import runnable
from configs.index import REDIS_URL
import chainlit as cl
from langchain_core.messages import AIMessageChunk


@cl.on_chat_start
async def init():
    session_id = uuid4().hex
    cl.user_session.set(key="session_id", value=session_id)

@cl.on_message
async def run_convo(message: cl.Message):
    session_id = cl.user_session.get(key="session_id")
    history = RedisChatMessageHistory(url=REDIS_URL or "",session_id=session_id or "", key_prefix="jcb:")
    await history.aadd_messages(messages=[HumanMessage(content=message.content)])
    stream = runnable.astream_events(
        input={"messages": history.messages[-4:]},
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
    


