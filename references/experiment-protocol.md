# Experiment protocol

This is the repository's operational synthesis. Read it for controlled comparisons and instrumentation; a single diagnostic reproduction needs only the relevant parts.

## Contract and assignment

Write a manifest before collecting measurement traffic. Include the hypothesis, primary outcome, minimum worthwhile difference, guardrails, scenario provenance, success oracle, variant URLs, observation channel, viewport, app/corpus revisions, model and prompt versions, effort limits, cost limits, and output directory. Freeze the held-out cases before changing the product. Do not choose a winner by repeatedly peeking at results; use a fixed batch or a prespecified sequential method.

Create an assignment ledger before dispatch. Each row identifies experiment, scenario, pair, variant, session, model, seed, order, and terminal-record location. One pair contains exactly one assigned session per variant. Replications get new pair and session IDs. Multiple models are separate strata and never opposite halves of one pair. Record order independently from the seed; a seed alone does not reconstruct unlogged random choices.

Keep an equal replication count per scenario when targeting an equally weighted scenario average. The included analyzer weights complete pairs equally and resamples scenario clusters; unequal repetitions therefore change the estimand. Report model-specific results or separate experiments when model mix matters.

The ledger is the source of truth for assignments. Reconcile it with collected terminal records. The analyzer can flag incomplete pairs present in its input, but cannot discover an entirely absent pair or a session that was never recorded. Record explicit invalid terminal outcomes for instrument failures where the assigned session is known; disclose missing data rather than silently imputing success/failure.

## Scenario construction

Use a matrix, not a pile of paraphrases. Useful axes include task intent, vocabulary, product availability, number of constraints, result density, viewport, and recovery path. Sample according to the stated purpose: coverage-oriented stress testing is not a population-weighted experiment. Preserve the source, confidence, and rationale for each task. Treat a domain expert's plausible task as expert input, not observed demand.

Keep hidden oracle information away from the browser worker. The worker may know the patron's constraints; it must not know the expected winning item or ranking. A separate observer verifies constraints against trusted catalog/app state. For subjective tasks, use a documented rubric and human adjudication or a separately calibrated grader, report uncertainty, and avoid giving the grader the variant label. Never resolve a grader disagreement by defaulting to the worker's success claim.

Negative controls must have explicit expected behavior: for an impossible request, correctly discovering unavailability may be success if that is the stated task. If the task requires obtaining an unavailable item, completion is impossible and a reported purchase is a false positive. Fix the oracle before running.

## Browser fidelity

Use a fresh context per assigned session, consistent viewport, locale, authentication fixture, and data snapshot. Do not let a worker inspect another variant first and carry its learned item names into the next session. Use separate worker context/history for each variant, not just separate browser cookies. Counterbalance variant order to reduce timing effects. Mock external dependencies only when the limitation is recorded.

For typeahead, type in plausible increments, wait for the interface's observable settled state, and retain query/request IDs. Never use arbitrary sleeps as proof results settled. Distinguish prefix changes (`b`, `bu`, `bur`) from deliberate reformulations (`burger`, `vegetarian sandwich`). A fast full-string fill may be suitable for retrieval diagnosis but cannot test prefix interaction.

The observation contract names screenshot, viewport-filtered accessibility, unrestricted DOM, or direct API access. Only the first two can support a visual-findability claim, and they still differ from human attention. Never count a hidden snapshot node as seen. Capturing the whole DOM for post-run diagnosis is permissible if it does not leak into worker choices.

## Event and artifact contract

Use existing application telemetry when possible. Mark all events `traffic_type=synthetic` and exclude them from customer analytics and ranking training unless that use is explicitly intended. Keep training/exploration and evaluation datasets separate.

Store an append-only event stream with these common keys:

```text
event_id, experiment_id, scenario_id, pair_id, session_id, variant,
traffic_type, timestamp_utc, elapsed_ms, event_type
```

Useful event types and payloads:

| Event | Payload |
| --- | --- |
| assigned / started | model, prompt hash, browser version, viewport, corpus revision |
| query_changed | query_id, raw query, change kind (prefix/reformulation), prior query ID |
| results_rendered | query_id, request_id, ordered item IDs, result count |
| item_visible | query_id, request_id, item ID, displayed rank, visible fraction, duration |
| click | item ID, query_id, request_id, matching exposure event ID |
| outcome | oracle decision, evidence paths, reason, budget counters |
| harness_error | error class, operation, retry/attempt identity |

Declare an exposure rule before running (for example, at least 50% of the item visible for 500 ms). That threshold is a convention, not validated human attention. Deduplicate by session/query-result instance/item unless explicitly measuring repeated exposure. Use viewport intersection and elapsed time; instrument virtualized lists after actual rendering. Keep stale responses tied to their request IDs so an old result set cannot be attributed to a newer query.

Store screenshots/traces/logs under the explicit session ID immediately. Deduplicate event ingestion by event ID and use parameterized inserts if adding a database. Redact credentials, customer identifiers, and sensitive query text before sharing artifacts. Never log auth headers or cookies. Summaries reference artifacts; they do not replace them.

For per-query top-clicked-item reports, aggregate query frequency separately from click counts, then join by query ID/string according to a declared normalization policy. Order by query frequency descending, query string, then click count descending and stable item ID. Preserve zero-click queries. Do not call those counts relevance labels.

## Failure, retries, and budgets

Specify limits for time, actions, reformulations, scroll depth, tokens, and total experiment spend. The orchestrator enforces limits when tooling permits; a prompt alone is not reliable enforcement. Abort the batch if telemetry is corrupt, error rates exceed a prespecified threshold, or resource limits are reached. Never keep spawning workers to recover a preferred outcome.

Product no-results and bad results are valid task outcomes. A browser crash, missing observation, broken oracle, or unlinked telemetry is an invalid measurement. An agent that voluntarily gives up yields abandonment. Time-budget exhaustion can be failure or abandonment under the prespecified rule; use it consistently. Successful means independently verified completion within the budget.

Keep every attempted run in raw artifacts. A retry gets a new attempt identity; do not append two terminal records for the same session or pair/variant. Decide the replacement policy in advance and expose its attrition counts. Correcting a broken harness starts a new measurement batch, rather than silently merging corrected runs with earlier outcomes.

## Analysis and decisions

Use the [terminal format](session-format.md) and analyzer for transparent descriptive summaries. It does not ingest the assignment ledger, events, costs, oracle state, or model calibration data. Reconcile and verify those separately. Never describe the illustrative fixture as a completed browser experiment.

Primary outcome: verified task success among valid terminal sessions, accompanied by counts of all assigned, missing, invalid, failed, and abandoned sessions. Inspect per-variant attrition before comparing success. Report effort for all valid sessions and successes separately; conditioning on success can make a weaker variant appear efficient. Compare zero-click success explicitly when the task supports it.

For the paired delta use only complete valid pairs. Report both session counts and unique scenarios. The helper's percentile bootstrap resamples whole scenario clusters, preserving within-scenario repetitions. It cannot establish generalization beyond sampled tasks, causal human uplift, adequate power, or model independence. One scenario has no estimable between-scenario uncertainty; a handful warrants caution. Degenerate intervals may simply mean every observed pair had the same outcome.

Inspect discordant pairs and failed controls. Classify findings as retrieval, presentation, interaction, content/data, simulator, or instrumentation. Preserve contradictions. Report the smallest targeted change and rerun a held-out regression set; do not tune both the simulator and the product on the same measurement cases.

## Calibration

On authorized human traces, compare query lengths, prefixes, reformulation counts, scroll depths, abandonment, selected-item diversity, and task success. Ask a domain reviewer to assess scenario plausibility and trace fidelity without variant labels. Use multiple models as a sensitivity analysis, not a proxy for demographics. Document where the simulator is too persistent, too knowledgeable, or blind to visual friction. If calibration is absent, restrict conclusions to synthetic-task diagnosis.
