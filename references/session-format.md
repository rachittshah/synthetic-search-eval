# Terminal session format and analyzer

Use this contract when exporting completed runs for `scripts/analyze_sessions.py`. It is a summary format, not a replacement for the timestamped event log, browser trace, screenshots, frozen scenario manifest, and independent verifier results.

## Run

Python 3.9+; standard library only. From the skill/repository root:

```sh
python3 scripts/analyze_sessions.py --input assets/example-sessions.jsonl --baseline A --candidate B
python3 scripts/analyze_sessions.py --input runs/sessions.jsonl --baseline control --candidate treatment --bootstrap 2000 --seed 42 --output runs/report.json
python3 -m unittest discover -s tests -v
```

The bundled example is entirely hand-authored. Its artifact paths deliberately do not identify real traces, and its outcomes are not evidence that a browser or model was tested. The analyzer checks schema and arithmetic; it does not certify the truth of an outcome or open evidence files.

`--input` is required. Defaults: `--baseline A`, `--candidate B`, `--bootstrap 2000`, `--seed 42`. Output is JSON on stdout unless `--output` is supplied. Existing output files are never overwritten. Validation and file errors return exit code 2 with a concise stderr message. Only the two named variants are accepted.

## One JSON object per terminal session

| Field | Required value / meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `experiment_id` | Nonempty explicit ID of the frozen experiment; one per input file |
| `scenario_id` | Nonempty ID of the underlying user task, shared across its replicas and variants |
| `pair_id` | Nonempty ID of one matched scenario/model/seed assignment, shared across variants |
| `variant` | Exact baseline or candidate name |
| `session_id` | Globally unique within the input; never use a "latest session" lookup |
| `model` | Explicit model/version identifier; identical within each pair |
| `seed` | Integer scenario/randomization seed; identical within each pair; does not imply deterministic model execution |
| `status` | `success`, `failure`, `abandoned`, or `invalid` |
| `queries` | List of nonempty submitted/query-state strings, in order; empty is allowed |
| `impressions` | Nonnegative integer of measured viewport exposures under the frozen exposure definition |
| `clicks` | Nonnegative integer recorded clicks, including unhelpful clicks |
| `duration_ms` | Finite, nonnegative numeric wall-clock duration; not a human effort estimate |
| `evidence` | List of nonempty artifact paths; may be empty except for success |
| `success_evidence` | Required nonempty verifier explanation for `success`, tied to the task's acceptance conditions |
| `failure_reason` | Required nonempty reason for every other status |

Extra fields are permitted and ignored. Boolean values are not valid numeric fields. Blank lines are skipped, but malformed JSON, duplicate object keys, non-finite numbers, missing required fields, and an empty input are rejected. Strings are preserved exactly; normalize identifiers before export if needed.

Use `success` only when the independent task check passes. A click by itself is not success; a correct no-match outcome may succeed with zero clicks if that is the predeclared task. `failure` is a valid attempt that did not satisfy the task. `abandoned` is a valid attempt that reached its predefined patience/action budget. `invalid` means infrastructure or protocol failure prevents interpreting the attempt as product evidence. Do not reclassify frustrating UI behavior as infrastructure failure.

Impressions count actual observed viewport exposures, not every search response row or every DOM node. Define exposure threshold, dwell duration, and repeated-exposure deduplication in the experiment before collection. Query counting likewise needs a frozen convention for typeahead: record the query states that received/rendered results, not merely arbitrary keystrokes. Total session counts do not allow reconstruction of impressions-before-first-click; derive those from the event log separately.

## Identity, retries, and exclusions

Duplicate `session_id` values or a second record for the same `(pair_id, variant)` are errors, even if the repeated record is identical. A pair must match `scenario_id`, `model`, and `seed`; the analyzer rejects mismatches. Keep prompt version, viewport, budgets, application data, tools, and other conditions fixed in the manifest and verify them before export; this minimal summary does not mechanically check those conditions.

Preserve every attempt in raw logs. Choose a predeclared retry policy before exporting one terminal record per assignment. Do not silently replace a valid failure with a successful retry. Infrastructure retries need explicit attempt IDs and an audit trail; their exclusion is a methodological decision, not something this analyzer infers. Reconcile expected assignments against the frozen manifest before analysis: assignments missing from both variants cannot be discovered from session records alone.

## Output and interpretation

`variants[NAME]` reports total sessions, all four status counts, valid sessions, success rate, and effort summaries for `effort_all_valid` and `effort_successful`. Both effort objects include sample size and mean/median for queries, impressions, clicks, and duration. `invalid` sessions are excluded from valid denominators; failures and abandonment remain. Empty denominators produce JSON `null`, never zero.

`paired` reports all observed pair IDs, complete valid pairs, unique scenario clusters, explicit excluded pairs with missing/invalid variants, matched success rates, candidate and baseline wins, ties, and `success_rate_difference` (candidate minus baseline, in probability units). A difference of `0.1` is ten percentage points on this synthetic sample, not ten percent relative improvement. Per-variant descriptive rates can differ from paired rates when assignments are missing or invalid.

The 95% interval is a percentile bootstrap: draw whole scenario clusters with replacement, retain all their matched replicas, and recompute the pair-weighted mean difference. Replicas of the same scenario are therefore not treated as independent scenario samples. The point estimate weights scenarios according to their observed replica counts; balance replication or explicitly report that weighting. The seed controls bootstrap randomness only. The interval is absent with fewer than two complete scenario clusters. Warnings flag fewer than ten clusters, fewer than twenty pairs, exclusions, missing variants, or fewer than 1,000 bootstrap draws. These counts are practical caution flags, not validated power thresholds.

The interval describes sampling variation under this experiment's scenario-cluster assumptions. It does not measure simulator fidelity, human population uncertainty, model drift, or systematic prompt bias. A degenerate interval is possible when all observed effects agree; that is not proof of certainty. Do not optimize repeatedly on the same held-out scenarios or declare a release based solely on a favorable interval.

Raw query-to-document click tables, time to first useful result, constraint violations, model-stratified comparisons, and human calibration require the richer event/manifest data. This CLI deliberately makes no inference for those quantities from unavailable fields.
