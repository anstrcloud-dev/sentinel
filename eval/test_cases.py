"""Labeled test set — the ground truth for evaluation.

Each case is an incident paired with the classification a human considers
correct. Variety matters: clear single-domain cases, genuine multi-domain
cases, and deliberately ambiguous ones that SHOULD be hard.

expected_type is the ground-truth incident_type.
expected_routes is the set of specialists that SHOULD be triggered.
"""

TEST_CASES = [
    # ── Clear single-domain: fire ──
    {"text": "Smoke pouring out of a second-floor apartment window.",
     "expected_type": "fire", "expected_routes": {"fire"}},
    {"text": "Kitchen grease fire spreading to the cabinets.",
     "expected_type": "fire", "expected_routes": {"fire"}},

    # ── Clear single-domain: medical ──
    {"text": "Elderly man collapsed at the bus stop, not breathing.",
     "expected_type": "medical", "expected_routes": {"medical"}},
    {"text": "Woman in labor, contractions two minutes apart.",
     "expected_type": "medical", "expected_routes": {"medical"}},
    {"text": "Child having a severe allergic reaction, difficulty breathing.",
     "expected_type": "medical", "expected_routes": {"medical"}},

    # ── Clear single-domain: police ──
    {"text": "Someone is breaking into parked cars on the street.",
     "expected_type": "police", "expected_routes": {"police"}},
    {"text": "Shoplifter being detained by store security.",
     "expected_type": "police", "expected_routes": {"police"}},
    {"text": "Person with a knife threatening people in the parking lot.",
     "expected_type": "police", "expected_routes": {"police"}},

    # ── Multi-domain: should trigger several specialists ──
    {"text": "Car crashed into a building, people trapped, fuel leaking.",
     "expected_type": "multi", "expected_routes": {"fire", "medical", "police"}},
    {"text": "Bar fight, multiple people injured, one with stab wounds.",
     "expected_type": "multi", "expected_routes": {"fire", "medical", "police"}},
    {"text": "House fire with residents trapped inside on the top floor.",
     "expected_type": "multi", "expected_routes": {"fire", "medical", "police"}},
    {"text": "Highway pileup, several cars, injuries, traffic blocked.",
     "expected_type": "multi", "expected_routes": {"fire", "medical", "police"}},

    # ── Deliberately tricky / ambiguous ──
    {"text": "Gas smell in an apartment building, residents worried.",
     "expected_type": "fire", "expected_routes": {"fire"}},
    {"text": "Elderly woman fell down the stairs, conscious but in pain.",
     "expected_type": "medical", "expected_routes": {"medical"}},
    {"text": "Suspicious unattended backpack left at a train platform.",
     "expected_type": "police", "expected_routes": {"police"}},
]
