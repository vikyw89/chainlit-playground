from configs.index import OPENAI_API_KEY
from .state import AgentState
from langchain_openai.chat_models import ChatOpenAI
from src.agents.tools import search_promotion
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.prebuilt.chat_agent_executor import create_tool_calling_executor


import datetime
if not (OPENAI_API_KEY):
    raise Exception("OPENAI_API_KEY is not set")


async def astream(state: AgentState):
    model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY, streaming=True, name="researcher")  # type: ignore

    agent = create_tool_calling_executor(model=model, tools=[search_promotion.tool])
    import datetime
    input = {
        "messages": [
            SystemMessage(
                content=f"""Let's think step by step. Today is {datetime.datetime.now().strftime("%Y-%m-%d")}.You are a JCB agent customer service knowledgeable in JCB promotions. Use tool to search for promotions that might interest user. Provide details of the promotion. Be helpful friendly and proactive in recommending promotions."""
            )
        ]
        + state["messages"]
    }

    res = await agent.ainvoke(input)

    state["messages"] += res["messages"]
    return state