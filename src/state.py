"""The shared state ("incident chart") that flows through the graph.

Every node receives this, reads what it needs, and returns the fields it
updates. LangGraph merges those updates back in.
"""

import operator
from typing import TypedDict, Annotated


class IncidentState(TypedDict):
    raw_input: str          # original emergency report text
    entities: dict          # extracted details (intake)
    incident_type: str      # medical | fire | police | multi (classifier)
    severity: int           # 1-5 (classifier)
    confidence: float       # 0.0-1.0 (classifier)
    dispatch_note: str      # human-readable summary (consolidate/outcome)
    human_decision: str     # yes | no (human approval gate)

    # Reducer field: specialists run in parallel and each append one report.
    # operator.add concatenates the lists instead of overwriting (no collisions).
    specialist_reports: Annotated[list[dict], operator.add]
