"""Retrieval-Augmented Generation: semantic search over SOPs via pgvector.

The embedding model is loaded once at import and reused for every retrieval.
retrieve_context() embeds an incident and returns the closest SOPs as text
to inject into a specialist's prompt.
"""

import psycopg
from sentence_transformers import SentenceTransformer

from src.config import DB_CONFIG, EMBED_MODEL_NAME, RAG_TOP_K

# Loaded once (this import runs a single time per process).
print("Loading embedding model...")
_embed_model = SentenceTransformer(EMBED_MODEL_NAME)


def embed(text: str) -> list[float]:
    """Turn text into its embedding vector."""
    return _embed_model.encode(text).tolist()


def retrieve_context(incident_text: str, top_k: int = RAG_TOP_K) -> str:
    """Return the top_k most relevant SOPs for an incident, as a text block.

    Wrapped in a try/except so a database hiccup degrades gracefully to an
    empty context rather than crashing the whole graph.
    """
    try:
        query_embedding = embed(incident_text)
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT content FROM sops
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                    """,
                    (query_embedding, top_k),
                )
                rows = cur.fetchall()
        return "\n".join(f"- {row[0]}" for row in rows)
    except Exception as e:
        print(f"  [rag] ⚠️ retrieval failed ({e}); proceeding without context")
        return "(no protocols retrieved)"
