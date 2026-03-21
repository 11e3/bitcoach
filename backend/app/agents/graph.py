"""LangGraph coaching pipeline.

Flow:
  classify (Haiku) → statistics (Python) → patterns (Haiku) → coaching (Sonnet) → actions (Sonnet)

Each node updates the shared CoachingState.
Errors in individual nodes don't block the pipeline — it degrades gracefully.
"""

from langgraph.graph import StateGraph

from app.agents.nodes.actions import extract_actions
from app.agents.nodes.classify import classify_trades
from app.agents.nodes.coaching import generate_coaching
from app.agents.nodes.patterns import detect_patterns
from app.agents.nodes.statistics import compute_statistics
from app.agents.state import CoachingState


def build_coaching_graph() -> StateGraph:
    """Build the coaching analysis pipeline."""

    graph = StateGraph(CoachingState)

    # Add nodes
    graph.add_node("classify", classify_trades)
    graph.add_node("statistics", compute_statistics)
    graph.add_node("patterns", detect_patterns)
    graph.add_node("coaching", generate_coaching)
    graph.add_node("actions", extract_actions)

    # Linear flow
    graph.add_edge("classify", "statistics")
    graph.add_edge("statistics", "patterns")
    graph.add_edge("patterns", "coaching")
    graph.add_edge("coaching", "actions")

    # Entry and exit
    graph.set_entry_point("classify")
    graph.set_finish_point("actions")

    return graph


# Compiled graph — reusable across requests
coaching_pipeline = build_coaching_graph().compile()
