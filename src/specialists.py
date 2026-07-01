"""Domain specialist agents: fire, medical, police.

Each agent is the same skeleton specialized by a domain-specific prompt:
  1. retrieve relevant SOPs (RAG)
  2. reason over the incident + retrieved protocol
  3. return a structured report, tagged with its domain

Each call is wrapped in a try/except so one agent's LLM failure degrades to
a flagged fallback report rather than taking down the whole dispatch.
"""

import json

from groq import Groq

from src.config import GROQ_API_KEY, FAST_MODEL
from src.state import IncidentState
from src.rag import retrieve_context

client = Groq(api_key=GROQ_API_KEY)

FIRE_PROMPT = """You are a fire response coordinator for emergency dispatch.
Given an incident, decide the fire/rescue response.
Return a JSON object with exactly these fields:
  "units": a list of unit names (e.g. ["Engine-1", "Ladder-2", "HazMat-3"])
  "hazard_note": a brief note, MAXIMUM 15 words, no line breaks
  "priority": one of "immediate", "high", or "standard"
Only recommend fire/rescue units — other agents handle medical and police.
"""

MEDICAL_PROMPT = """You are a medical response coordinator for emergency dispatch.
Given an incident, decide the medical/EMS response.
Return a JSON object with exactly these fields:
  "units": a list of unit names (e.g. ["Ambulance-7", "Paramedic-2"])
  "hazard_note": a brief note, MAXIMUM 15 words, no line breaks
  "priority": one of "immediate", "high", or "standard"
Only recommend medical/EMS units — other agents handle fire and police.
"""

POLICE_PROMPT = """You are a police response coordinator for emergency dispatch.
Given an incident, decide the police response.
Return a JSON object with exactly these fields:
  "units": a list of unit names (e.g. ["Patrol-4", "K9-1"])
  "hazard_note": a brief note, MAXIMUM 15 words, no line breaks
  "priority": one of "immediate", "high", or "standard"
Only recommend police units — other agents handle fire and medical.
"""

_FALLBACK = {
    "units": ["TBD"],
    "hazard_note": "analysis failed, manual review needed",
    "priority": "high",
}


def _run_specialist(domain: str, prompt: str, state: IncidentState) -> dict:
    """Shared logic for every specialist: retrieve SOPs, reason, return report."""
    print(f"  [{domain}] retrieving protocol + analyzing...")
    context = retrieve_context(state["raw_input"])
    user_message = (
        f"Incident: {state['raw_input']}\n\n"
        f"Relevant standard operating procedures:\n{context}\n\n"
        f"Based on the incident AND the procedures above, decide the {domain} response."
    )
    try:
        response = client.chat.completions.create(
            model=FAST_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        report = json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"  [{domain}] ⚠️ failed ({e}); using fallback report")
        report = dict(_FALLBACK)
    report["domain"] = domain
    return {"specialist_reports": [report]}


# Thin wrappers so the graph has one node function per domain.
def fire_node(state: IncidentState) -> dict:
    return _run_specialist("fire", FIRE_PROMPT, state)


def medical_node(state: IncidentState) -> dict:
    return _run_specialist("medical", MEDICAL_PROMPT, state)


def police_node(state: IncidentState) -> dict:
    return _run_specialist("police", POLICE_PROMPT, state)
