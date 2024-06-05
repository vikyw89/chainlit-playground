from typing import Annotated, Literal
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from configs.index import db


async def arun(location: str, category: Literal["Retail Store", "Restaurant", "Entertainment","Hotel","Relaxation","Other","Leisure"] = "Other"):
    """useful to search JCB promotion"""
    await db.connect()

    # parse location
    location = location.title()
    promotions = await db.promotion.find_many(
        where={
            "location": {"contains": location},
            "category1": {"contains": category},
        },
        take=3,
    )

    parsed_promotions = []
    for promo in promotions:
        parsed_promotions.append(
            promo.model_dump()
        )

    await db.disconnect()
    return parsed_promotions




tool = StructuredTool.from_function(
    name="search_promotion",
    description="useful to search JCB promotion",
    coroutine=arun,
)
