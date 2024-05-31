from configs.index import OPENAI_API_KEY
from .state import AgentState
from langchain_openai.chat_models import ChatOpenAI
from src.agents.tools import search_promotion
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.prebuilt.chat_agent_executor import create_tool_calling_executor

if not (OPENAI_API_KEY):
    raise Exception("OPENAI_API_KEY is not set")


async def astream(state: AgentState):
    # model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY, streaming=True, name="researcher")  # type: ignore

    # agent = create_tool_calling_executor(model=model, tools=[search_promotion.tool])

    input = {
        "messages": [
            SystemMessage(
                content="""Let's think step by step. You are a JCB agent customer service equiped with all available promotions. Use tool to search for promotions."""
            )
        ]
        + state["messages"]
    }
    from langchain_community.agent_toolkits import create_sql_agent
    from langchain_openai import ChatOpenAI
    from langchain_community.utilities import SQLDatabase
    import datetime
    db = SQLDatabase.from_uri("sqlite:///prisma/dev.db")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, name="researcher")
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools")

    res = await agent_executor.ainvoke(input=f"Let's think step by step. Today is {datetime.date.today().strftime('%Y-%m-%d')}. Proactively search database to find promotions related to message from user. Extract clues of what promotion might be beneficial to user from user message: \n{state["messages"][-1].content}")
    print("res", res)
    state["messages"] += [AIMessage(content=res["output"])]
    return state