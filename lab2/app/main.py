"""FastAPI service that wraps a local Ollama server for SMS spam classification."""

from __future__ import annotations

import json
import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

app = FastAPI(
    title="SMS Spam Classifier",
    description="FastAPI wrapper over a local Ollama server with Qwen2.5:0.5B.",
    version="1.0.0",
)


class ClassificationRequest(BaseModel):
    """Input payload for SMS classification."""

    message: str = Field(..., min_length=1, description="SMS message text to classify.")


class ClassificationResponse(BaseModel):
    """Normalized response returned by the FastAPI service."""

    message: str
    verdict: int
    reasoning: str
    raw_response: str
    model: str


def build_classification_prompt(message: str) -> str:
    """Create an instruction prompt for binary SMS spam classification.

    Args:
        message: SMS text that must be classified.

    Returns:
        Prompt text instructing the model to produce strict JSON.
    """

    return f"""
You are an SMS spam classifier for a mobile operator.
Classify the SMS message as:
- 1 = spam
- 0 = not spam

Return strictly valid JSON with exactly two fields:
{{
  "reasoning": "short explanation",
  "verdict": 0
}}

Rules:
- Do not add markdown.
- Do not add code fences.
- Keep reasoning short.
- verdict must be only 0 or 1.

SMS:
{message}
""".strip()


def request_ollama(prompt: str) -> dict[str, Any]:
    """Send a non-streaming generation request to the local Ollama API.

    Args:
        prompt: Prompt text that will be forwarded to Ollama.

    Returns:
        Parsed JSON response from Ollama.

    Raises:
        HTTPException: If the Ollama server is unreachable or returns an invalid response.
    """

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0},
            },
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Ollama request failed: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Ollama returned non-JSON data.") from exc


def normalize_model_output(raw_response: str) -> tuple[int, str]:
    """Parse and validate the model JSON output.

    Args:
        raw_response: Raw text produced by the LLM.

    Returns:
        Tuple of verdict and reasoning.

    Raises:
        HTTPException: If the model output cannot be parsed or validated.
    """

    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="Model output is not valid JSON.") from exc

    verdict = payload.get("verdict")
    reasoning = str(payload.get("reasoning", "")).strip()

    if verdict not in (0, 1):
        raise HTTPException(status_code=502, detail="Model verdict must be 0 or 1.")

    if not reasoning:
        reasoning = "Reasoning was not provided by the model."

    return int(verdict), reasoning


@app.post("/classify", response_model=ClassificationResponse)
def classify_sms(request: ClassificationRequest) -> ClassificationResponse:
    """Classify one SMS message as spam or not spam.

    Args:
        request: Request body with the SMS text.

    Returns:
        Normalized classification response containing verdict and explanation.
    """

    prompt = build_classification_prompt(request.message)
    ollama_response = request_ollama(prompt)
    raw_response = str(ollama_response.get("response", "")).strip()
    verdict, reasoning = normalize_model_output(raw_response)

    return ClassificationResponse(
        message=request.message,
        verdict=verdict,
        reasoning=reasoning,
        raw_response=raw_response,
        model=OLLAMA_MODEL,
    )
