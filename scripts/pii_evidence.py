from __future__ import annotations

import json
import logging
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path


LOG_PATH = Path(".tmp/pii-evidence-final.jsonl")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["LOG_PATH"] = str(LOG_PATH)
os.environ.pop("LANGFUSE_PUBLIC_KEY", None)
os.environ.pop("LANGFUSE_SECRET_KEY", None)
logging.disable(logging.CRITICAL)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def main() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.unlink(missing_ok=True)
    samples = (
        ("req-10000001", "Contact user@example.test"),
        ("req-10000002", "Call 0912345678"),
        ("req-10000003", "CCCD 001234567890"),
        ("req-10000004", "Card 4111 1111 1111 1111"),
    )

    client = TestClient(app)
    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        for correlation_id, message in samples:
            response = client.post(
                "/chat",
                headers={"x-request-id": correlation_id},
                json={
                    "user_id": "evidence-user",
                    "session_id": "evidence-session",
                    "feature": "qa",
                    "message": message,
                },
            )
            response.raise_for_status()

    rows = [json.loads(line) for line in LOG_PATH.read_text(encoding="utf-8").splitlines()]
    evidence = [
        {
            "event": row["event"],
            "correlation_id": row["correlation_id"],
            "payload": row["payload"],
        }
        for row in rows
        if row.get("event") == "request_received"
    ]
    rendered = json.dumps(evidence, indent=2, ensure_ascii=False)
    markers = (
        "[REDACTED_EMAIL]",
        "[REDACTED_PHONE_VN]",
        "[REDACTED_CCCD]",
        "[REDACTED_CREDIT_CARD]",
    )
    assert len(evidence) == 4
    assert all(marker in rendered for marker in markers)
    assert all("[REDACTED_" not in row["correlation_id"] for row in evidence)

    for row in evidence:
        print(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    print("PASS: 4/4 synthetic PII types redacted; correlation IDs preserved.")


if __name__ == "__main__":
    main()
