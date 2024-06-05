from configs.index import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_HOST_URL
from pinecone import Pinecone
from configs.index import db

def run():
    import asyncio
    from nest_asyncio import apply

    apply()
    asyncio.run(seed())




async def seed():
    # load data
    pc = Pinecone(api_key=PINECONE_API_KEY,host=PINECONE_HOST_URL)
    index = pc.Index(host=PINECONE_HOST_URL or "")
    # index.delete(deleteAll=True,namespace="promotions")
    from llama_index.core import VectorStoreIndex, StorageContext
    from llama_index.vector_stores.pinecone import PineconeVectorStore
    from llama_index.core.schema import TextNode
    from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
    from prisma.types import PromotionScalarFieldKeys
    embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY,model=OpenAIEmbeddingModelType.TEXT_EMBED_3_LARGE)
    db_locations = db.query_raw(
        query="""
SELECT DISTINCT location
FROM Promotion
WHERE location IS NOT NULL"""
    )
    nodes = []

    for location in db_locations:
        node = TextNode(
            text=location["location"] or "",
        )
        nodes.append(node)

        for key, value in location.items():
            node.metadata[key] = value
        nodes.append(node)

    vector_store = PineconeVectorStore(
        pinecone_index=index, namespace="locations"
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True, use_async=True, embed_model=embed_model, store_nodes_override=True)
