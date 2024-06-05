from typing import Annotated, Literal
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from configs.index import PINECONE_API_KEY, PINECONE_HOST_URL, db
from pinecone import Pinecone
from langchain_community.agent_toolkits import create_sql_agent


async def arun(query: str, category: Literal["Retail Store", "Restaurant", "Entertainment","Hotel","Relaxation","Other","Leisure"] = "Other"):
    """useful to search JCB promotion"""
    from langchain_community.utilities import SQLDatabase

    db = SQLDatabase.from_uri(
        "sqlite:///./prisma/dev.db",
        # sample_rows_in_table_info=1,
        include_tables=["Promotion"],
    )  
    llm = ChatOpenAI(model="gpt-4o", temperature=0, name="sql_agent")
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", top_k=3)

    res = await agent_executor.ainvoke(f"""Let's think step by step. 
Ensure accuracy. 
Retrieve all promotions that match {query}. 
Category": {category}.
Limit to 3 top results.
""")  # type: ignore

    return res["output"]


tool = StructuredTool.from_function(
    name="search_promotion",
    description="useful to search JCB promotion",
    coroutine=arun,
)