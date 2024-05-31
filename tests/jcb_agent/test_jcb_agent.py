def test_jcb_agent():
    import asyncio

    async def run():
        from src.agents.jcb_agent.index import runnable
        from langchain_core.messages import HumanMessage
        stream = runnable.astream(input={"messages": [HumanMessage(content="Is there a good restaurant in Seoul ?")]}, debug=True)

        async for chunk in stream:
            print(chunk)

    asyncio.run(run())