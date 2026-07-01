"""Graph construction: registers nodes, defines routing, wires edges.

Flow:
    START -> intake -> classifier -> [router]
                                        |-> fire ----+
                                        |-> medical -+-> consolidate -> human_approval -> outcome -> END
                                        |-> police --+
    (multi fans out to all three specialists in parallel, then they rejoin)
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import IncidentState
from src.classifier import classifier_node
from src.specialists import fire_node, medical_node, police_node
from src.nodes import (
    intake_node,
    consolidate_node,
    human_approval_node,
    outcome_node,
)


def route_by_type(state: IncidentState):
    """Deterministic routing (NOT an LLM): returns the specialist node(s) to run.

    Returning a list triggers parallel fan-out; 'multi' runs all three.
    """
    t = state["incident_type"]
    print(f"  [router] type '{t}' -> routing...")
    if t == "multi":
        return ["fire", "medical", "police"]
    if t in ("fire", "medical", "police"):
        return [t]
    return ["fire"]  # safe default for anything unexpected


def build_graph():
    """Assemble and compile the dispatch graph."""
    builder = StateGraph(IncidentState)

    # Register all nodes first.
    builder.add_node("intake", intake_node)
    builder.add_node("classifier", classifier_node)
    builder.add_node("fire", fire_node)
    builder.add_node("medical", medical_node)
    builder.add_node("police", police_node)
    builder.add_node("consolidate", consolidate_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("outcome", outcome_node)

    # Wire the edges in flow order.
    builder.add_edge(START, "intake")
    builder.add_edge("intake", "classifier")
    builder.add_conditional_edges(
        "classifier", route_by_type, ["fire", "medical", "police"]
    )
    builder.add_edge("fire", "consolidate")
    builder.add_edge("medical", "consolidate")
    builder.add_edge("police", "consolidate")
    builder.add_edge("consolidate", "human_approval")
    builder.add_edge("human_approval", "outcome")
    builder.add_edge("outcome", END)

    # Checkpointer is required for interrupt()/resume to work.
    return builder.compile(checkpointer=MemorySaver())
