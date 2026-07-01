"""Central configuration: models, database settings, and tunable constants.

Keeping these in one place means changing a model name or the DB password
is a one-line edit, not a hunt across the codebase.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM (Groq) ────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Model cascading: fast model for the common case, strong model on low confidence.
FAST_MODEL = "openai/gpt-oss-20b"     # primary — quick, handles most incidents
STRONG_MODEL = "openai/gpt-oss-120b"  # fallback — better reasoning for hard cases
CONFIDENCE_THRESHOLD = 0.7            # below this, escalate to STRONG_MODEL

# ── Embeddings (RAG) ──────────────────────────────────────────────────
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # local sentence-transformers model
EMBED_DIM = 384                        # output dimension of the model above
RAG_TOP_K = 2                          # how many SOPs to retrieve per incident

# ── Database (pgvector) ───────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "sentinel",
    "user": "postgres",
    "password": "sentinel",
}
