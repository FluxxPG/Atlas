import hashlib
import math
import re

import httpx

from worker.config import settings


def build_company_embedding_text(company: dict) -> str:
    enrichment = company.get("enrichment", {})
    metadata = company.get("metadata", {})
    parts = [
        company.get("name", ""),
        company.get("industry", ""),
        company.get("city", ""),
        company.get("region", ""),
        company.get("country", ""),
        company.get("description", ""),
        company.get("ai_summary", ""),
        " ".join(enrichment.get("technology_stack", [])),
        " ".join(enrichment.get("social_profiles", [])),
        " ".join(metadata.get("expanding_regions", [])),
        " ".join(metadata.get("intent_topics", [])),
    ]
    return " ".join(part for part in parts if part)


def generate_embedding(text: str, dimensions: int | None = None) -> list[float]:
    hosted = _generate_hosted_embedding(text)
    if hosted:
        return hosted

    size = dimensions or settings.embedding_dimensions
    vector = [0.0] * size
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    if not tokens:
        tokens = ["empty"]

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for offset in range(0, len(digest), 4):
            chunk = digest[offset : offset + 4]
            if len(chunk) < 4:
                continue
            bucket = int.from_bytes(chunk, "little") % size
            sign = 1.0 if digest[(offset + 1) % len(digest)] % 2 == 0 else -1.0
            magnitude = 0.25 + (digest[(offset + 2) % len(digest)] / 255.0) * 0.75
            vector[bucket] += sign * magnitude

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 6) for value in vector]


def format_vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{value:.6f}" for value in vector) + "]"


def _generate_hosted_embedding(text: str) -> list[float] | None:
    if not settings.openai_api_key or not settings.hosted_embedding_model:
        return None

    try:
        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={"model": settings.hosted_embedding_model, "input": text},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        return [round(float(value), 6) for value in payload["data"][0]["embedding"]]
    except Exception:
        return None
