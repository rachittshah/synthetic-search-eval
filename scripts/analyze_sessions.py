#!/usr/bin/env python3
"""Validate terminal synthetic sessions and compare two frozen variants."""

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import random
import statistics
import sys


STATUSES = ("success", "failure", "abandoned", "invalid")
ID_FIELDS = ("experiment_id", "scenario_id", "pair_id", "variant", "session_id", "model")


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"non-finite JSON value: {value}")


def validate_record(record):
    """Validate required terminal fields; evidence content is verified by the runner."""
    if not isinstance(record, dict):
        raise ValueError("each line must be a JSON object")
    if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        raise ValueError("schema_version must be integer 1")
    for field in ID_FIELDS:
        if not _nonempty(record.get(field)):
            raise ValueError(f"{field} must be a nonempty string")
    if record.get("status") not in STATUSES:
        raise ValueError(f"status must be one of {', '.join(STATUSES)}")
    for field in ("queries", "evidence"):
        if not isinstance(record.get(field), list) or not all(
            _nonempty(item) for item in record[field]
        ):
            raise ValueError(f"{field} must be a list of nonempty strings")
    for field in ("impressions", "clicks"):
        if type(record.get(field)) is not int or record[field] < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    if type(record.get("seed")) is not int:
        raise ValueError("seed must be an integer")
    duration = record.get("duration_ms")
    try:
        valid_duration = (
            type(duration) in (int, float) and math.isfinite(duration) and duration >= 0
        )
    except OverflowError:
        valid_duration = False
    if not valid_duration:
        raise ValueError("duration_ms must be finite and nonnegative")
    if record["status"] == "success":
        if not _nonempty(record.get("success_evidence")) or not record["evidence"]:
            raise ValueError("success requires success_evidence and at least one evidence artifact")
    elif not _nonempty(record.get("failure_reason")):
        raise ValueError("non-success requires failure_reason")


def read_records(path):
    """Read JSONL, rejecting malformed lines rather than silently dropping sessions."""
    records = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(
                    line, object_pairs_hook=_object, parse_constant=_reject_constant
                )
                validate_record(record)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"line {line_number}: {exc}") from exc
            records.append(record)
    if not records:
        raise ValueError("input contains no sessions")
    return records


def _effort(records):
    fields = {
        "queries": [len(row["queries"]) for row in records],
        "impressions": [row["impressions"] for row in records],
        "clicks": [row["clicks"] for row in records],
        "duration_ms": [row["duration_ms"] for row in records],
    }
    return {
        "n": len(records),
        **{
            field: {
                "mean": statistics.mean(values) if values else None,
                "median": statistics.median(values) if values else None,
            }
            for field, values in fields.items()
        },
    }


def _percentile(values, probability):
    position = (len(values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def analyze(records, baseline="A", candidate="B", bootstrap=2000, seed=42):
    """Compare records; reject duplicate assignments and cross-variant confounds."""
    if not _nonempty(baseline) or not _nonempty(candidate) or baseline == candidate:
        raise ValueError("baseline and candidate must be distinct nonempty variant names")
    if type(bootstrap) is not int or bootstrap < 1:
        raise ValueError("bootstrap must be a positive integer")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    if not records:
        raise ValueError("input contains no sessions")
    by_variant = {baseline: [], candidate: []}
    pairs = defaultdict(dict)
    session_ids = set()
    experiments = set()
    for row in records:
        validate_record(row)
        experiments.add(row["experiment_id"])
        if len(experiments) > 1:
            raise ValueError("mixed experiment IDs; analyze each experiment separately")
        if row["variant"] not in by_variant:
            raise ValueError(f"unexpected variant: {row['variant']}")
        if row["session_id"] in session_ids:
            raise ValueError(f"duplicate session_id: {row['session_id']}")
        session_ids.add(row["session_id"])
        pair = pairs[row["pair_id"]]
        if row["variant"] in pair:
            raise ValueError(f"duplicate pair/variant assignment: {row['pair_id']}/{row['variant']}")
        if pair:
            other = next(iter(pair.values()))
            for field in ("scenario_id", "model", "seed"):
                if row[field] != other[field]:
                    raise ValueError(f"pair {row['pair_id']} has mismatched {field}")
        pair[row["variant"]] = row
        by_variant[row["variant"]].append(row)

    variants = {}
    for variant, rows in by_variant.items():
        statuses = Counter(row["status"] for row in rows)
        valid = [row for row in rows if row["status"] != "invalid"]
        successful = [row for row in valid if row["status"] == "success"]
        variants[variant] = {
            "total_sessions": len(rows),
            "status_counts": {status: statuses[status] for status in STATUSES},
            "valid_sessions": len(valid),
            "success_rate": len(successful) / len(valid) if valid else None,
            "effort_all_valid": _effort(valid),
            "effort_successful": _effort(successful),
        }

    excluded = []
    complete = []
    clusters = defaultdict(list)
    for pair_id, pair in sorted(pairs.items()):
        missing = [variant for variant in by_variant if variant not in pair]
        invalid = [variant for variant, row in pair.items() if row["status"] == "invalid"]
        if missing or invalid:
            excluded.append({"pair_id": pair_id, "missing_variants": missing, "invalid_variants": invalid})
            continue
        a, b = pair[baseline], pair[candidate]
        difference = int(b["status"] == "success") - int(a["status"] == "success")
        complete.append((a, b, difference))
        clusters[a["scenario_id"]].append(difference)

    warnings = [
        "Synthetic-agent results are descriptive evidence, not estimates of human conversion or uplift.",
        "Evidence strings are schema-checked only; independently verify task outcomes and artifact contents.",
        "Missing assignments absent from both variants are not detectable without the experiment manifest.",
    ]
    n = len(complete)
    interval = None
    if len(clusters) >= 2:
        rng = random.Random(seed)
        groups = [clusters[key] for key in sorted(clusters)]
        samples = []
        for _ in range(bootstrap):
            sampled = [rng.choice(groups) for _ in groups]
            samples.append(sum(sum(group) for group in sampled) / sum(map(len, sampled)))
        samples.sort()
        interval = [_percentile(samples, 0.025), _percentile(samples, 0.975)]
        if len(clusters) < 10:
            warnings.append("Fewer than 10 scenario clusters: the bootstrap interval is unstable; inspect individual scenarios.")
    else:
        warnings.append("Fewer than 2 complete scenario clusters: uncertainty interval is unavailable.")
    if n < 20:
        warnings.append("Fewer than 20 complete valid pairs: treat comparisons as exploratory.")
    if excluded:
        warnings.append("Incomplete or invalid pairs were excluded from the paired comparison; inspect exclusions for selection bias.")
    if any(not rows for rows in by_variant.values()):
        warnings.append("At least one requested variant has no recorded sessions.")
    if bootstrap < 1000:
        warnings.append("Fewer than 1000 bootstrap draws: percentile precision is limited.")
    return {
        "schema_version": 1,
        "experiment_id": next(iter(experiments)),
        "baseline": baseline,
        "candidate": candidate,
        "variants": variants,
        "paired": {
            "total_pair_ids": len(pairs),
            "complete_valid_pairs": n,
            "scenario_clusters": len(clusters),
            "excluded_pairs": excluded,
            "baseline_success_rate": sum(a["status"] == "success" for a, _, _ in complete) / n if n else None,
            "candidate_success_rate": sum(b["status"] == "success" for _, b, _ in complete) / n if n else None,
            "success_rate_difference": sum(delta for _, _, delta in complete) / n if n else None,
            "candidate_wins": sum(delta == 1 for _, _, delta in complete),
            "baseline_wins": sum(delta == -1 for _, _, delta in complete),
            "ties": sum(delta == 0 for _, _, delta in complete),
            "confidence_interval_95": interval,
            "interval_method": "percentile bootstrap resampling whole scenario clusters; pair-weighted mean difference",
            "bootstrap_draws": bootstrap,
            "bootstrap_seed": seed,
        },
        "warnings": warnings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Terminal sessions JSONL")
    parser.add_argument("--baseline", default="A")
    parser.add_argument("--candidate", default="B")
    parser.add_argument("--bootstrap", default=2000, type=int)
    parser.add_argument("--seed", default=42, type=int)
    parser.add_argument("--output", type=Path, help="New JSON file; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        result = analyze(read_records(args.input), args.baseline, args.candidate, args.bootstrap, args.seed)
        rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(rendered)
        else:
            sys.stdout.write(rendered)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
