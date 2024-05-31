from langchain_core.tools import StructuredTool
from configs.index import db


async def arun(location: str, category: str):
    await db.connect()

    promotions = await db.promotion.find_many(
        where={
            "location": {"contains": location},
            "category1": {"contains": category},
        },
        take=5,
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
