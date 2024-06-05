from typing import Annotated, Literal
from chainlit import cache
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from configs.index import db
from prisma.models import Promotion
from prisma.types import StringFilter, PromotionWhereInput, PromotionWhereInputRecursive1

async def arun(location: str, category: Literal["Retail Store", "Restaurant", "Entertainment","Hotel","Relaxation","Other","Leisure","None"]  = "None"):
    """useful to search JCB promotion by location"""

    # parse location
    location = location.title()
    promotions = None

    if category != "None":
        promotions = db.promotion.find_many(
            where=PromotionWhereInput(
                OR=[PromotionWhereInputRecursive1(
                    location=StringFilter(contains=location),
                    address=StringFilter(contains=location),
                )],
                category1=StringFilter(contains=category),
            ),
            take=3,
        )
    else:
        promotions = db.promotion.find_many(
            where=PromotionWhereInput(
                OR=[PromotionWhereInputRecursive1(
                    location=StringFilter(contains=location),
                    address=StringFilter(contains=location),
                )],
            ),
            take=3,
        )

    parsed_promotions = []
    for promo in promotions:
        parsed_promotions.append(
            promo.model_dump()
        )

    return parsed_promotions




tool = StructuredTool.from_function(
    name="search_promotion",
    description="useful to search JCB promotion by location",
    coroutine=arun,
)
