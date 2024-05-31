# Must precede any llm module imports
from langgraph.graph import StateGraph, END
from . import recommendation, researcher, router
from .state import AgentState

# Define a new graph
graph = StateGraph(AgentState)
graph.add_node("researcher", researcher.astream)
# graph.add_node("reviewer", reviewer_agent.astream)
# graph.add_node("recommendations", recommendation.arun)

# define edges
graph.set_entry_point("researcher")

# graph.add_edge("reviewer", "post_reviewer")

# graph.add_edge("researcher", "recommendations")
graph.add_edge("researcher", END)

runnable = graph.compile()