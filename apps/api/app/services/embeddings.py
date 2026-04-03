import hashlib
import json
import math
import re

import httpx

from app.core.config import settings


def build_company_embedding_text(company: dict) -> str:
    enrichment = company.get("enrichment", {})
    metadata = company.get("metadata", {})
    parts = [
        company.get("name", ""),
        company.get("industry", ""),
        company.get("subindustry", ""),
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


def rerank_companies(query: str, companies: list[dict]) -> list[dict]:
    if not companies:
        return companies

    hosted = _rerank_with_hosted_model(query, companies)
    if hosted:
        return hosted

    lowered = query.lower()
    scored = []
    for company in companies:
        score = 0.0
        haystack = " ".join(
            part
            for part in [
                company.get("name") or "",
                company.get("industry") or "",
                company.get("description") or "",
                company.get("ai_summary") or "",
                " ".join((company.get("enrichment") or {}).get("technology_stack", [])),
            ]
            if part
        ).lower()
        for token in re.findall(r"[a-z0-9]+", lowered):
            if token in haystack:
                score += 1.0
        score += float(company.get("opportunity_score", 0)) / 100
        score += float(company.get("growth_score", 0)) / 150
        scored.append((score, company))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [company for _, company in scored]


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


def _rerank_with_hosted_model(query: str, companies: list[dict]) -> list[dict] | None:
    if not settings.openai_api_key or not settings.hosted_rerank_model:
        return None

    company_index = {item["id"]: item for item in companies if item.get("id")}
    if not company_index:
        return None

    candidate_payload = [
        {
            "id": item["id"],
            "name": item.get("name"),
            "industry": item.get("industry"),
            "description": item.get("description"),
            "ai_summary": item.get("ai_summary"),
            "technology_stack": (item.get("enrichment") or {}).get("technology_stack", []),
            "opportunity_score": item.get("opportunity_score"),
            "growth_score": item.get("growth_score"),
        }
        for item in companies
    ]

    prompt = (
        "You are ranking business intelligence search results.\n"
        "Return JSON only in the shape {\"ranked_ids\": [\"id1\", \"id2\"]}.\n"
        "Rank the candidates by relevance to the user's search intent.\n"
        f"Query: {query}\n"
        f"Candidates: {json.dumps(candidate_payload)}"
    )

    try:
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.hosted_rerank_model,
                "input": prompt,
                "max_output_tokens": 300,
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        output_text = _extract_response_text(payload)
        parsed = json.loads(output_text)
        ranked_ids = parsed.get("ranked_ids") or []
        ranked = [company_index[item_id] for item_id in ranked_ids if item_id in company_index]
        remaining = [item for item in companies if item["id"] not in {row["id"] for row in ranked}]
        return [*ranked, *remaining]
    except Exception:
        return None


def _extract_response_text(payload: dict) -> str:
    if payload.get("output_text"):
        return payload["output_text"]

    chunks: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text_value = content.get("text")
            if text_value:
                chunks.append(text_value)
    return "".join(chunks)
