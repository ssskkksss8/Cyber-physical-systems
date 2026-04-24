"""Host-side inference script for the Dockerized FastAPI + Ollama SMS spam classifier."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

DEFAULT_SERVICE_URL = "http://127.0.0.1:8000/classify"
DEFAULT_TIMEOUT_SECONDS = 120
REPORTS_DIR = Path("reports")

SAMPLE_MESSAGES = [
    "WINNER! You have won a free vacation. Reply YES to claim now.",
    "Hi Alex, are we still meeting at 18:30 near the station?",
    "URGENT: Your bank account is blocked. Follow the link immediately.",
    "Please review the draft and send comments before tomorrow morning.",
    "Congratulations! You were selected for a cash prize. Call now.",
    "Mom, I bought bread and milk. I will be home in 20 minutes.",
    "Limited offer only today: get a cheap loan with no documents required.",
    "The lesson has been moved from Friday to Saturday at 10:00.",
    "Claim your bonus points before they expire. Click the link.",
    "I left the charger on your desk. Take it when you arrive.",
]


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for the host-side inference script.

    Returns:
        Parsed command line namespace.
    """

    parser = argparse.ArgumentParser(description="Run sample SMS spam inference via FastAPI service.")
    parser.add_argument(
        "--url",
        default=DEFAULT_SERVICE_URL,
        help="FastAPI classification endpoint URL.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="HTTP timeout in seconds for each request.",
    )
    return parser.parse_args()


def ensure_reports_directory() -> None:
    """Create the reports directory if it does not exist."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def classify_message(session: requests.Session, url: str, message: str, timeout: int) -> dict[str, Any]:
    """Send one SMS message to the FastAPI service for classification.

    Args:
        session: Reusable HTTP session.
        url: FastAPI endpoint URL.
        message: SMS text to classify.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response from the FastAPI service.

    Raises:
        requests.RequestException: If the HTTP request fails.
        ValueError: If the service returns invalid JSON.
    """

    response = session.post(url, json={"message": message}, timeout=timeout)
    response.raise_for_status()
    return response.json()


def run_inference(url: str, timeout: int) -> list[dict[str, Any]]:
    """Classify the predefined sample SMS messages.

    Args:
        url: FastAPI endpoint URL.
        timeout: Request timeout in seconds.

    Returns:
        List with normalized inference results.
    """

    results: list[dict[str, Any]] = []
    with requests.Session() as session:
        for index, message in enumerate(SAMPLE_MESSAGES, start=1):
            result = classify_message(session=session, url=url, message=message, timeout=timeout)
            result["id"] = index
            result["created_at"] = datetime.now(timezone.utc).isoformat()
            results.append(result)
    return results


def save_csv_report(results: list[dict[str, Any]]) -> Path:
    """Write inference results to a CSV report file.

    Args:
        results: Inference results to save.

    Returns:
        Path to the created CSV report.
    """

    output_path = REPORTS_DIR / "report.csv"
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["id", "message", "verdict", "reasoning", "model", "created_at", "raw_response"],
        )
        writer.writeheader()
        writer.writerows(results)
    return output_path


def save_json_log(results: list[dict[str, Any]]) -> Path:
    """Write inference results to a JSON log file.

    Args:
        results: Inference results to save.

    Returns:
        Path to the created JSON log file.
    """

    output_path = REPORTS_DIR / "log.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)
    return output_path


def save_markdown_report(results: list[dict[str, Any]], service_url: str) -> Path:
    """Write a human-readable Markdown report for the inference run.

    Args:
        results: Inference results to save.
        service_url: URL used for the inference run.

    Returns:
        Path to the created Markdown report.
    """

    output_path = REPORTS_DIR / "report.md"
    spam_count = sum(item["verdict"] for item in results)
    ham_count = len(results) - spam_count

    lines = [
        "# Inference report",
        "",
        f"- Service URL: `{service_url}`",
        f"- Total messages: **{len(results)}**",
        f"- Predicted spam: **{spam_count}**",
        f"- Predicted non-spam: **{ham_count}**",
        "",
        "| ID | SMS message | Verdict | Reasoning |",
        "|---:|---|---:|---|",
    ]

    for item in results:
        message = item["message"].replace("|", "\\|")
        reasoning = str(item["reasoning"]).replace("|", "\\|")
        lines.append(f"| {item['id']} | {message} | {item['verdict']} | {reasoning} |")

    with output_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    return output_path


def main() -> None:
    """Run the end-to-end host-side inference flow and generate all reports."""

    args = parse_arguments()
    ensure_reports_directory()
    results = run_inference(url=args.url, timeout=args.timeout)

    csv_path = save_csv_report(results)
    json_path = save_json_log(results)
    md_path = save_markdown_report(results, service_url=args.url)

    print("Inference completed successfully.")
    print(f"CSV report: {csv_path}")
    print(f"JSON log:   {json_path}")
    print(f"MD report:  {md_path}")


if __name__ == "__main__":
    main()
