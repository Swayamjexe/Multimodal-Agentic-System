from langgraph.graph import StateGraph, END
from app.models.state import AgentState
from app.langgraph.nodes import (
    content_extractor,
    intent_classifier,
    followup_agent,
    task_executor
)

graph = StateGraph(AgentState)

graph.add_node("content_extractor", content_extractor)
graph.add_node("intent_classifier", intent_classifier)
graph.add_node("followup_agent", followup_agent)
graph.add_node("task_executor", task_executor)

graph.set_entry_point("content_extractor")
graph.add_edge("content_extractor", "intent_classifier")

def needs_clarification(state: AgentState):
    return state.intent_confidence < 0.65

graph.add_conditional_edges(
    "intent_classifier",
    needs_clarification,
    {
        True: "followup_agent",
        False: "task_executor"
    }
)

graph.add_edge("followup_agent", "task_executor")
graph.add_edge("task_executor", END)

app_graph = graph.compile()
