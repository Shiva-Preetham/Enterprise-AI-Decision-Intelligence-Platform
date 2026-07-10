import asyncio
from langchain_core.messages import HumanMessage
from agent.graph import app
from agent.memory import get_memory_saver

async def main():
    try:
        checkpointer = get_memory_saver()
        input_state = {
            "messages": [HumanMessage(content="hello")],
            "customer_id": None
        }
        config = {"configurable": {"thread_id": "test_123"}}
        
        # If checkpointer is valid, we must pass it to ainvoke, wait, graph is compiled.
        # Let's just run it the exact same way router.py does
        if checkpointer:
            pass # Actually router.py does this:
        
        from agent.graph import app
        # Wait, router.py uses app.ainvoke directly!
        final_state = await app.ainvoke(input_state, config=config)
        print("SUCCESS:", final_state)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
