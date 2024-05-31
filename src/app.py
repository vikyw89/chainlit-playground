from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl


from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

@cl.on_message
async def run_convo(message: cl.Message):
    #"what is the weather in sf"
    inputs = {"messages": [HumanMessage(content=message.content)]}
    from src.agents.jcb_agent.index import runnable
    res = await runnable.ainvoke(inputs, config=RunnableConfig(callbacks=[
        cl.LangchainCallbackHandler(
            to_ignore=["ChannelRead", "RunnableLambda", "ChannelWrite", "__start__", "_execute"]
            # can add more into the to_ignore: "agent:edges", "call_model"
            # to_keep=

        )]))

    await cl.Message(content=res["messages"][-1].content).send()
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
