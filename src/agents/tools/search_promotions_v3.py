from langchain_core.tools import StructuredTool
from configs.index import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_HOST_URL
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.postprocessor.llm_rerank import LLMRerank
from llama_index.llms.openai import OpenAI
from pinecone import Pinecone
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import MetadataMode
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType

async def arun(query: str):
    pc = Pinecone(api_key=PINECONE_API_KEY, host=PINECONE_HOST_URL)
    pinecone_index = pc.Index(host=PINECONE_HOST_URL or "")

    vector_store = PineconeVectorStore(
        pinecone_index=pinecone_index, namespace="promotions",
    )
    embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY, model=OpenAIEmbeddingModelType.TEXT_EMBED_3_LARGE)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    llm = OpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)

    # node postprocessors
    reranker = LLMRerank(llm=llm, top_n=3)

    retriever = VectorIndexRetriever(index=index, similarity_top_k=15, embed_model=embed_model)

    query_engine = CitationQueryEngine.from_args(
        llm=llm,
        index=index,
        retriever=retriever,
        citation_chunk_size=4000,
        citation_chunk_overlap=0,
        node_postprocessors=[reranker],
        use_async=True,
        metadata_mode=MetadataMode.LLM,
    )

    response = await query_engine.aquery(str_or_query_bundle=query)

    parsed_source_nodes = []

    for node in response.source_nodes:
        parsed_node = {
            "content": node.get_content(),
        }
        parsed_source_nodes.append(parsed_node)

    return {
        "search_query": query,
        "source_nodes": parsed_source_nodes,
        "result": response.response,  # type: ignore
    }


tool = StructuredTool.from_function(
    name="jcb_promotions",
    description="useful to search jcb promotions using semantic query",
    coroutine=arun,
)
