import chainlit as cl
from langchain_core.messages import HumanMessage,AIMessageChunk
from src.agents.jcb_agent.index import runnable
from langchain.memory import ConversationBufferMemory

from chainlit.types import ThreadDict

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
    message = cl.Message(content="""Hello! I am JCB Promotion Assistant. 
I excel in finding good JCB deals. 
How can I help you today?""")
    await message.send()

@cl.on_message
async def run_convo(message: cl.Message):
    memory:ConversationBufferMemory | None = cl.user_session.get(key="memory") # type: ignore
    chat_history = memory.chat_memory.messages if memory else []

    stream = runnable.astream_events(
        input={"messages": chat_history[-4:] + [HumanMessage(content=message.content)]},
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
            # for question in questions: # type: ignore
            #     actions.append(cl.Action(name=question, value=question, label=question))

            # res = await cl.AskActionMessage(
            #     content="You might want to ask:",
            #     actions=actions,
            #     author="JCB Agent",
            # ).send()

            # # TODO: fix user action as user input
            # if res:
            #     human_message = res["value"]
                
    await msg.send()


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] == None] # type: ignore
    for message in root_messages:
        if message["type"] == "user_message": # type: ignore
            memory.chat_memory.add_user_message(message["output"]) # type: ignore
        else:
            memory.chat_memory.add_ai_message(message["output"]) # type: ignore

    cl.user_session.set("memory", memory)
