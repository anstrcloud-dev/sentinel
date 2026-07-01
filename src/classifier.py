"""Classifier node with model cascading.

Classifies an incident with the fast model; if confidence is below the
threshold, re-classifies with the stronger model. Deterministic escalation
based on the model's own confidence — cheap for the common case, accurate
for the hard ones.
"""

import json

from groq import Groq

from src.config import GROQ_API_KEY, FAST_MODEL, STRONG_MODEL, CONFIDENCE_THRESHOLD
from src.state import IncidentState

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are an emergency dispatch classifier.
Return a JSON object with exactly these fields:
  "incident_type": one of "medical", "fire", "police", or "multi"
  "severity": integer from 1 to 5
  "confidence": float from 0.0 to 1.0
"""


def _classify_with(model_name: str, incident_text: str) -> dict:
    """Run one classification pass with a given model."""
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": incident_text},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def classifier_node(state: IncidentState) -> dict:
    print(f"  [classifier] classifying with fast model ({FAST_MODEL})...")
    data = _classify_with(FAST_MODEL, state["raw_input"])

    if data["confidence"] < CONFIDENCE_THRESHOLD:
        print(f"  [classifier] low confidence ({data['confidence']}); "
              f"escalating to strong model ({STRONG_MODEL})...")
        data = _classify_with(STRONG_MODEL, state["raw_input"])
        print(f"  [classifier] strong model confidence: {data['confidence']}")

    return {
        "incident_type": data["incident_type"],
        "severity": data["severity"],
        "confidence": data["confidence"],
    }
