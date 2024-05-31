import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.chat_history import InMemoryChatMessageHistory
import chainlit as cl
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk, ToolMessage
from langchain_core.runnables import RunnableConfig
from uuid import uuid4
from src.agents.jcb_agent.index import runnable
from configs.index import REDIS_URL
import chainlit as cl

@cl.on_chat_start
async def init():
    session_id = uuid4().hex
    cl.user_session.set(key="session_id", value=session_id)

@cl.on_message
async def run_convo(message: cl.Message):
    session_id = cl.user_session.get(key="session_id")
    history = RedisChatMessageHistory(url=REDIS_URL,session_id=session_id, key_prefix="jcb:")
    await history.aadd_messages(messages=[HumanMessage(content=message.content)])
    inputs = {"messages": history.messages[-4:]}
    stream = runnable.astream_log(
        input={"messages": history.messages[-4:]}
    )

    msg = cl.Message(content="")

    async for chunk in stream:
        for o in chunk.ops:
            
            op = o["op"]
            value = o["value"]
            path = o["path"]
            
            # stream final output
            if op == "add" and path.startswith("/logs/researcher") and path.endswith("streamed_output_str/-"):
                await msg.stream_token(value)
            # stream steps
            # if op == "add" and path.startswith("/logs/call_model/final_output"):
            #     messages:list[AIMessage] = value["messages"]
            #     tool_name = messages[0].additional_kwargs["tool_calls"][0]["function"]["name"]
            #     tool_arg = messages[0].additional_kwargs["tool_calls"][0]["function"]["arguments"]
            #     async with cl.Step(name=tool_name) as step:
            #         step.input = json.dumps(tool_arg, indent=4)
            #         step.output = tool_arg
            #         await step.send()
            # if op == "add" and path.startswith("/logs/search_promotion/final_output"):
            #     outputs = value["output"]
            #     async with cl.Step(name=outputs[0].additional_kwargs[""]) as step:
            #         step.input = json.dumps(inputs, indent=4)
            #         step.output = json.dumps(outputs, indent=4)
            #     # async with cl.Step(name="Test") as step:
            #     #     # Step is sent as soon as the context manager is entered
            #     #     step.input = "hello"
            #     #     step.output = "world"
            #         await step.send()
    await msg.send()


# @cl.on_chat_start
# async def on_chat_start():
#     model = ChatOpenAI(streaming=True)
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
#             ),
#             ("human", "{question}"),
#         ]
#     )
#     runnable = prompt | model | StrOutputParser()
#     cl.user_session.set("runnable", runnable)


# @cl.on_message
# async def on_message(message: cl.Message):
#     runnable = cl.user_session.get("runnable")  # type: Runnable

#     msg = cl.Message(content="")

#     async for chunk in runnable.astream(
#         {"question": message.content},
#         config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
#     ):
#         await msg.stream_token(chunk)

#     await msg.send()
