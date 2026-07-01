"""Entry point: run a single incident through the dispatch graph.

Usage:
    python main.py

Requires the pgvector container running and the knowledge base built
(see scripts/build_kb.py).
"""

from langgraph.types import Command

from src.graph import build_graph


def run_incident(graph, incident_text: str, thread_id: str = "incident-1"):
    config = {"configurable": {"thread_id": thread_id}}

    print("\n--- PHASE 1: running until human gate ---")
    result = graph.invoke({"raw_input": incident_text}, config=config)

    print("\n>>> GRAPH PAUSED. Waiting for dispatcher approval.")
    print(">>> Proposed dispatch:")
    print("   ", result["__interrupt__"][0].value)

    decision = input("\n   >>> Approve dispatch? Type yes or no: ").strip().lower()
    if decision not in ("yes", "no"):
        print("   Invalid input — treating as 'no' for safety.")
        decision = "no"

    final = graph.invoke(Command(resume=decision), config=config)

    print("\n--- FINAL STATE ---")
    print("   incident_type:", final["incident_type"])
    print("   confidence:   ", final["confidence"])
    print("   dispatch_note:\n", final["dispatch_note"])
    print("   human_decision:", final["human_decision"])


if __name__ == "__main__":
    graph = build_graph()
    run_incident(
        graph,
        "Car crashed into a building, people trapped, fuel leaking.",
    )
