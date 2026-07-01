"""Supporting nodes: intake, consolidate, human approval, and outcome.

These are the non-LLM (or non-specialist) steps that structure the flow
around the classifier and the specialist agents.
"""

from langgraph.types import interrupt

from src.state import IncidentState


def intake_node(state: IncidentState) -> dict:
    """First station: extract basic details from the raw report."""
    print("  [intake] extracting entities...")
    return {"entities": {"length": len(state["raw_input"])}}


def consolidate_node(state: IncidentState) -> dict:
    """Fan-in: merge the parallel specialist reports into one summary."""
    print("  [consolidate] merging specialist reports...")
    lines = []
    for r in state["specialist_reports"]:
        units = ", ".join(r["units"])
        lines.append(f"{r['domain'].upper()}: {units} ({r['priority']}) — {r['hazard_note']}")
    return {"dispatch_note": "\n".join(lines)}


def human_approval_node(state: IncidentState) -> dict:
    """Human-in-the-loop gate: pause the graph and wait for a decision.

    interrupt() freezes execution here. The graph cannot proceed to dispatch
    until a human resumes it with a decision.
    """
    print("  [human] pausing for dispatcher approval...")
    decision = interrupt({
        "incident_type": state["incident_type"],
        "severity": state["severity"],
        "proposed_dispatch": state["dispatch_note"],
        "question": "Approve this dispatch? (yes/no)",
    })
    print(f"  [human] dispatcher said: {decision}")
    return {"human_decision": decision}


def outcome_node(state: IncidentState) -> dict:
    """Carry out the human's decision: dispatch or reject."""
    if state["human_decision"] == "yes":
        print(f"  [outcome] ✅ DISPATCHED: {state['dispatch_note']}")
        return {"dispatch_note": f"DISPATCHED — {state['dispatch_note']}"}
    print("  [outcome] ❌ REJECTED by dispatcher. Nothing dispatched.")
    return {"dispatch_note": "REJECTED — no units sent"}
