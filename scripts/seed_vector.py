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
    await db.connect()
    pc = Pinecone(api_key=PINECONE_API_KEY,host=PINECONE_HOST_URL)
    index = pc.Index(name="promotions", host=PINECONE_HOST_URL or "")
    # index.delete(deleteAll=True,namespace="promotions")
    from llama_index.core import VectorStoreIndex, StorageContext
    from llama_index.vector_stores.pinecone import PineconeVectorStore
    from llama_index.core.schema import TextNode
    from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType

    embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY,model=OpenAIEmbeddingModelType.TEXT_EMBED_3_LARGE)
    db_promotions = db.promotion.find_many()
    nodes = []
    for promo in db_promotions:
        node = TextNode(
            text=promo.businessDescription or "",
        )
        for key, value in promo.model_dump().items():
            node.metadata[key] = value
        nodes.append(node)

    vector_store = PineconeVectorStore(
        pinecone_index=index, namespace="promotions"
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True, use_async=True, embed_model=embed_model)
