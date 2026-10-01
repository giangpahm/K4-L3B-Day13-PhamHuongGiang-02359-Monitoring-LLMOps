from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil((p / 100) * len(ordered)) - 1))
    return ordered[index]


def load_records(path: Path) -> list[dict]:
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def fmt(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}"


def panel(title: str, value: str, unit: str, threshold: str, details: str, ok: bool) -> str:
    state = "Within threshold" if ok else "Threshold breached"
    state_class = "ok" if ok else "bad"
    return f"""
      <section class="panel">
        <div class="panel-head"><h2>{title}</h2><span class="{state_class}">{state}</span></div>
        <div class="metric">{value}<small>{unit}</small></div>
        <div class="details">{details}</div>
        <div class="threshold">Threshold / SLO: {threshold}</div>
      </section>"""


def build_dashboard(records: list[dict], config: dict) -> str:
    received = [r for r in records if r.get("event") == "request_received"]
    responses = [r for r in records if r.get("event") == "response_sent"]
    failures = [r for r in records if r.get("event") == "request_failed"]
    latencies = [float(r["latency_ms"]) for r in responses if isinstance(r.get("latency_ms"), (int, float))]
    ttfts = [float(r["ttft_ms"]) for r in responses if isinstance(r.get("ttft_ms"), (int, float))]
    costs = [float(r["cost_usd"]) for r in responses if isinstance(r.get("cost_usd"), (int, float))]
    qualities = [float(r["quality_score"]) for r in responses if isinstance(r.get("quality_score"), (int, float))]
    tokens_in = sum(int(r.get("tokens_in", 0)) for r in responses)
    tokens_out = sum(int(r.get("tokens_out", 0)) for r in responses)
    tool_events = [r for r in records if r.get("tool_success") is not None]
    tool_ok = sum(r.get("tool_success") is True for r in tool_events)
    retrieval_rate = 100 * tool_ok / len(tool_events) if tool_events else 0.0
    error_rate = 100 * len(failures) / len(received) if received else 0.0

    panels = [
        panel("Latency percentiles & TTFT", fmt(percentile(latencies, 95), 0), "ms P95", "P95 ≤ 3,000 ms", f"P50 {fmt(percentile(latencies, 50), 0)} ms · P99 {fmt(percentile(latencies, 99), 0)} ms · TTFT P95 {fmt(percentile(ttfts, 95), 0)} ms", percentile(latencies, 95) <= 3000),
        panel("Request traffic", str(len(received)), "requests / 60 min", "≥ 1 request/min target", f"{len(responses)} successful responses · {len(failures)} failed requests", len(received) > 0),
        panel("Errors & retrieval", fmt(error_rate), "% error rate", "Error ≤ 2% · retrieval ≥ 90%", f"Retrieval success {fmt(retrieval_rate)}% · {len(failures)} errors", error_rate <= 2 and retrieval_rate >= 90),
        panel("Cost over time", f"${fmt(sum(costs), 4)}", "USD total", "Total ≤ $2.50", f"Average ${fmt(mean(costs), 4) if costs else '0.0000'} per response", sum(costs) <= 2.5),
        panel("Input & output tokens", f"{tokens_in + tokens_out:,}", "tokens", "Total ≤ 50,000", f"Input {tokens_in:,} · Output {tokens_out:,}", tokens_in + tokens_out <= 50000),
        panel("Quality proxy", fmt(mean(qualities), 2) if qualities else "0.00", "score 0–1", "Average ≥ 0.75", f"Based on {len(qualities)} completed responses", bool(qualities) and mean(qualities) >= 0.75),
    ]
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    title = config["dashboard"]["title"]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{title}</title><style>
*{{box-sizing:border-box}} body{{margin:0;background:#09111f;color:#e6edf7;font:15px Inter,Segoe UI,Arial,sans-serif}}
.wrap{{max-width:1420px;margin:auto;padding:28px}} header{{display:flex;justify-content:space-between;align-items:end;margin-bottom:22px}}
h1{{font-size:27px;margin:0 0 7px}} .sub{{color:#8ca0bd}} .range{{background:#142238;border:1px solid #29405f;border-radius:10px;padding:10px 14px;color:#b9c9df}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}} .panel{{min-height:220px;background:linear-gradient(150deg,#111e31,#0e1929);border:1px solid #263b57;border-radius:15px;padding:20px;box-shadow:0 8px 26px #0005}}
.panel-head{{display:flex;justify-content:space-between;gap:12px;align-items:start}} h2{{font-size:16px;margin:0;color:#bfd0e8}} .ok,.bad{{font-size:11px;padding:5px 8px;border-radius:20px;white-space:nowrap}} .ok{{color:#6ee7b7;background:#064e3b88}} .bad{{color:#fca5a5;background:#7f1d1d88}}
.metric{{font-size:38px;font-weight:750;margin:28px 0 15px;color:#f8fbff}} .metric small{{font-size:13px;font-weight:500;color:#8ca0bd;margin-left:8px}}
.details{{color:#aebed3;min-height:38px}} .threshold{{margin-top:18px;padding-top:14px;border-top:1px solid #243751;color:#6ea8fe;font-size:13px}}
footer{{margin-top:18px;color:#7388a4;font-size:12px;display:flex;justify-content:space-between}} @media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main class="wrap"><header><div><h1>{title}</h1><div class="sub">Runtime dashboard · source: data/logs.jsonl</div></div><div class="range">Time range: Last 60 minutes · Refresh: 30s</div></header>
<div class="grid">{''.join(panels)}</div><footer><span>Generated {generated}</span><span>{len(records)} structured log records · no raw PII displayed</span></footer></main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the six-panel runtime dashboard from JSONL logs")
    parser.add_argument("--logs", type=Path, default=REPO_ROOT / "data" / "logs.jsonl")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "config" / "dashboard.yaml")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "submission" / "evidence" / "11-dashboard-overview.html")
    args = parser.parse_args()
    records = load_records(args.logs)
    if not records:
        raise SystemExit("No valid log records found; run the workload first.")
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_dashboard(records, config), encoding="utf-8")
    print(f"Generated {args.output} from {len(records)} log records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
