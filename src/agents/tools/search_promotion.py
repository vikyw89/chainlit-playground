from typing import Literal
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class ArgsSchema(BaseModel):
    start_date: str | None = Field(
        description="start date in yyyy-mm-dd format",
        examples=["2022-01-01"],
        default=None,
    )
    end_date: str | None = Field(
        description="end date in yyyy-mm-dd format",
        examples=["2022-01-01"],
        default=None,
    )
    city: str | None = Field(
        description="city all lowercase", examples=["seoul"], default=None
    )
    country: str | None = Field(
        description="country all lowercase", examples=["korea"], default=None
    )
    category: Literal["Relaxation", "Retail Store"] | None = Field(
        description="category, leave none to get all",
        examples=["Relaxation"],
        default=None,
    )


async def arun(
    start_date: str,
    end_date: str,
    city: str,
    country: str,
    category: Literal["Relaxation", "Retail Store"],
) -> str:

    return "no promotion found"


tool = StructuredTool.from_function(
    name="search_promotion",
    description="useful to search JCB promotion",
    coroutine=arun,
    # args_schema=ArgsSchema,
)
