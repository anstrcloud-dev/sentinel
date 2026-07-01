"""Build the SOP knowledge base in pgvector.

Run this ONCE (or whenever the SOPs change), after the pgvector container
is up:

    python scripts/build_kb.py

Creates the 'sops' table, embeds each SOP, and inserts it.
"""

import sys
from pathlib import Path

# Allow importing from src/ when run as a script.
sys.path.append(str(Path(__file__).resolve().parent.parent))

import psycopg
from src.config import DB_CONFIG, EMBED_DIM
from src.rag import embed

SOPS = [
    "Vehicle fire with fuel leak: Establish a 100-meter perimeter. Dispatch HazMat unit alongside fire engines. Do not approach until fuel source is contained. Risk of explosion.",
    "Structure fire with people trapped: Prioritize search and rescue. Dispatch ladder truck for upper floors. Coordinate with EMS for smoke inhalation victims.",
    "Cardiac arrest: Dispatch nearest ALS ambulance immediately. Instruct caller to begin CPR. Send paramedic unit. Time-critical, target response under 8 minutes.",
    "Armed suspect on scene: Do not approach. Establish containment perimeter. Dispatch multiple patrol units and request supervisor. Stage EMS at safe distance until scene secured.",
    "Multi-vehicle collision with injuries: Dispatch fire for extrication, multiple ambulances for casualties, and police for traffic control. Establish triage if 3+ casualties.",
    "Gas leak in residential building: Evacuate occupants immediately. Dispatch fire and HazMat. Do not operate electrical switches. Shut off gas supply at the main if safe.",
]


def main():
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("DROP TABLE IF EXISTS sops;")
            cur.execute(f"""
                CREATE TABLE sops (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding VECTOR({EMBED_DIM})
                );
            """)
            print("Table 'sops' created.")

            for sop in SOPS:
                cur.execute(
                    "INSERT INTO sops (content, embedding) VALUES (%s, %s);",
                    (sop, embed(sop)),
                )
        conn.commit()
    print(f"Inserted {len(SOPS)} SOPs. Knowledge base built.")


if __name__ == "__main__":
    main()
