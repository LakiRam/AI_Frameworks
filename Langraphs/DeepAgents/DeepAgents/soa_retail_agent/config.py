"""Centralized configuration loaded from environment variables."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Resolve project root so paths work whether launched from CWD or elsewhere
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ----- LLM -----
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()  # "ollama" | "gemini"
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# Ollama (local)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ----- Data -----
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "soa_retail_agent" / "data"))

# ----- Persistence -----
CHECKPOINT_DB = os.getenv("CHECKPOINT_DB", str(PROJECT_ROOT / ".langgraph_checkpoints.sqlite"))

# ----- API -----
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8080"))
APPROVAL_REQUIRED = os.getenv("APPROVAL_REQUIRED", "true").lower() == "true"

# ----- LangSmith -----
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
if LANGSMITH_TRACING:
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault(
        "LANGCHAIN_PROJECT", os.getenv("LANGSMITH_PROJECT", "soa-retail-agent")
    )
