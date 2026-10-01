from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.challenge import load_challenge


def incident_rows() -> tuple[object, list[dict]]:
    challenge = load_challenge()
    sessions = {query["session_id"] for query in challenge.queries}
    rows = [
        json.loads(line)
        for line in Path("data/logs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    responses = [
        row
        for row in rows
        if row.get("event") == "response_sent" and row.get("session_id") in sessions
    ]
    return challenge, responses


def show_metric() -> None:
    challenge, rows = incident_rows()
    latencies = sorted(row["latency_ms"] for row in rows)
    p95 = latencies[math.ceil(0.95 * len(latencies)) - 1]
    print(f"Challenge: {challenge.challenge_id}")
    print(f"Incident: {challenge.incident} | Feature: {challenge.affected_feature}")
    print(f"Window UTC: {min(row['ts'] for row in rows)} -> {max(row['ts'] for row in rows)}")
    print(f"Threshold: {challenge.latency_threshold_ms} ms")
    print(f"Affected requests: {sum(x > challenge.latency_threshold_ms for x in latencies)}/{len(latencies)}")
    print(f"Latency min/avg/P95/max: {min(latencies)} / {sum(latencies)/len(latencies):.1f} / {p95} / {max(latencies)} ms")
    print("ALERT: P95 latency exceeded the challenge threshold.")


def show_log() -> None:
    challenge, rows = incident_rows()
    worst = max(rows, key=lambda row: row["latency_ms"])
    print(f"Challenge: {challenge.challenge_id}")
    print(f"Threshold: {challenge.latency_threshold_ms} ms")
    selected = {
        key: worst.get(key)
        for key in (
            "ts",
            "event",
            "correlation_id",
            "session_id",
            "feature",
            "latency_ms",
            "ttft_ms",
            "tool_name",
            "tool_success",
        )
    }
    print(json.dumps(selected, indent=2, ensure_ascii=False))
    print(f"MATCH: latency {worst['latency_ms']} ms > threshold {challenge.latency_threshold_ms} ms")


def show_trace() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    from langfuse import get_client

    challenge, rows = incident_rows()
    worst = max(rows, key=lambda row: row["latency_ms"])
    observations = get_client().api.observations.get_many(
        session_id=worst["session_id"], limit=20
    ).data
    observations.sort(key=lambda observation: observation.start_time)
    trace_ids = {observation.trace_id for observation in observations}
    assert len(trace_ids) == 1
    trace_id = trace_ids.pop()

    print("Langfuse project: day13-k4-l3b-02359")
    print(f"Challenge: {challenge.challenge_id}")
    print(f"Correlation ID (joined via session): {worst['correlation_id']}")
    print(f"Session ID: {worst['session_id']}")
    print(f"Trace ID: {trace_id}")
    for observation in observations:
        parent = observation.parent_observation_id or "root"
        print(
            f"{observation.name:<14} {observation.type:<10} "
            f"duration={observation.latency * 1000:.0f} ms "
            f"observation={observation.id} parent={parent}"
        )
    retrieval = next(item for item in observations if item.name == "retrieval")
    print(
        f"ROOT CAUSE: retrieval span {retrieval.latency * 1000:.0f} ms "
        f"> threshold {challenge.latency_threshold_ms} ms (injected rag_slow)."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("metric", "log", "trace"))
    args = parser.parse_args()
    {"metric": show_metric, "log": show_log, "trace": show_trace}[args.kind]()


if __name__ == "__main__":
    main()
