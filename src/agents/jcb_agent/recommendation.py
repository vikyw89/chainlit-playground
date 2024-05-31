from pydantic import BaseModel, Field
from configs.index import OPENAI_API_KEY
from .state import AgentState
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai.chat_models import ChatOpenAI

if not (OPENAI_API_KEY):
    raise Exception("OPENAI_API_KEY is not set")


async def arun(state: AgentState):
    # will generate recommendation

    model = ChatOpenAI(
        model="gpt-3.5-turbo", api_key=OPENAI_API_KEY, name="recommendation"  # type: ignore
    )

    class Questions(BaseModel):
        text: list[str] = Field(description="text suggestions for human")

    query = f"""Given a chat history, generate 3 possible questions related to JCB promotions the user is interested in.
Text:
{state["messages"][:1].content}"""

    parser = PydanticOutputParser(pydantic_object=Questions, name="recommendation_agent_output_parser")  # type: ignore

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    await chain.ainvoke({"query": query})

    return state