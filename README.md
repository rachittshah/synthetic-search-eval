# Synthetic Search Eval

A coding-agent skill for evaluating search through the interface people use: type a query, inspect results, scroll, recover from a bad search, and verify whether the task was completed.

Inspired by Doug Turnbull's [Prefer synthetic traffic over LLM-as-a-judge](https://softwaredoug.com/blog/2026/11/12/agent-search-traffic). This repository combines that session-based approach with practitioner work on agent evaluation, click bias, and the limits of synthetic users.

**Use synthetic sessions to find and reproduce problems. Do not interpret them as measured customer preferences, conversion forecasts, or a replacement for human research.**

## What this skill does

- Diagnoses search failures through the actual UI, including prefixes, misspellings, vocabulary mismatch, zero-result recovery, and layout-dependent findability.
- Separates adaptive coverage exploration from frozen comparisons, preventing exploratory clicks from becoming an accidental benchmark.
- Specifies bounded browser workers, isolated state, explicit assignment IDs, viewport exposure, and independent task verification.
- Compares paired variants with honest outcome denominators and scenario-cluster uncertainty.
- Preserves failed, abandoned, invalid, and missing sessions in the accounting.
- Produces a decision report with reproduction steps, traces, limitations, and the next validation step.

This is a portable **skill plus analysis tool**, not a bundled browser service. Your coding agent supplies browser access and, optionally, worker orchestration. The repository includes prompts and contracts for those tools; it does not launch browsers, call paid models, collect customer traffic, or connect to an application by itself.

## Install and invoke

The repository root is the skill directory. Clone it into your agent's skills folder, or symlink an existing checkout. Choose one installation method; avoid overwriting an existing skill.

```sh
# Codex; this private repository requires an authorized GitHub account.
git clone https://github.com/rachittshah/synthetic-search-eval.git \
  ~/.codex/skills/synthetic-search-eval

# Alternatively, after cloning elsewhere:
# ln -s /absolute/path/synthetic-search-eval ~/.codex/skills/synthetic-search-eval
```

Other agents that support `SKILL.md` can use the same directory under their documented skill location. Agents without skill discovery can read `SKILL.md` explicitly. Browser tool configuration is environment-specific; the skill inspects available tools rather than assuming a particular MCP server or provider is installed.

Example requests:

```text
Use $synthetic-search-eval to diagnose why mobile users cannot find vegetarian
mains in our staging menu. Keep actions to search and item details. Capture a
reproducible trace and distinguish ranking, UI, and simulator failures.
```

```text
Use $synthetic-search-eval to compare the baseline and candidate search layouts.
Freeze tasks before measurement, use separate browser and worker contexts, and
report verified task completion, effort, exclusions, and uncertainty. We have
no human calibration data, so limit conclusions to synthetic task performance.
```

## Run the analysis example

Python 3.9 or newer; no third-party runtime dependencies.

```sh
python3 scripts/analyze_sessions.py \
  --input assets/example-sessions.jsonl \
  --baseline A --candidate B --bootstrap 2000 --seed 42

python3 -m unittest discover -s tests -v
```

The six example records are **hand-authored illustrations**, with intentionally fictional evidence paths. They exercise arithmetic and validation, not a browser or human study. The example has two complete valid pairs and one pair excluded for an invalid session. Its candidate-minus-baseline difference is `0.5` (50 percentage points) and its illustrative interval is `[0.0, 1.0]`; neither is a product-quality result.

For real sessions, replace the example with independently verified terminal records following [the schema](references/session-format.md). `--output new-report.json` writes a new file and refuses to overwrite an existing one. Invalid JSON, duplicate assignments, inconsistent pairs, mixed experiments, and unexpected variants fail visibly.

The analyzer verifies the record structure, not evidence contents. It cannot discover assignments absent from both variants; reconcile the assignment ledger before analysis. It reports paired synthetic task outcomes, not human causal effects. It does not infer query-to-item click tables or time-to-first-click from aggregate session counts.

## Workflow and files

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Entry point; route diagnosis, exploration, comparison, or calibration |
| [Experiment protocol](references/experiment-protocol.md) | Frozen scenarios, telemetry, exposure, isolation, retries, analysis, calibration |
| [Agent prompts](references/agent-prompts.md) | Orchestrator, browser worker, independent outcome observer |
| [Experiment template](assets/experiment-template.json) | Editable planning contract; not executable runner configuration |
| [Assignment ledger template](assets/assignments-template.csv) | Explicit paired IDs and counterbalanced order; illustrative rows |
| [Session format](references/session-format.md) | Terminal-record schema and analyzer behavior |
| [Analysis CLI](scripts/analyze_sessions.py) | Dependency-free paired outcome analysis |
| [Report template](assets/report-template.md) | Decision, denominators, evidence, limitations, follow-up |
| [Practitioner research](references/practitioner-sources.md) | Search/UI and synthetic-user sources with limits |
| [Evaluation research](references/evaluation-sources.md) | Agent evaluation sources and methodological implications |

Start with the existing app and telemetry. Define success and a task budget, run a small instrumentation pilot, then collect a frozen batch. Keep worker observations limited to the declared channel. A full accessibility tree or DOM can expose items that a person has not scrolled to; a screenshot-based run and an API-based run measure different things.

Keep exploration separate from comparison. Asking an agent to click a random Nth-relevant item can uncover more paths, but changes its selection policy. Likewise, switching models offers a sensitivity check, not a representative sample of customers. Preserve conventional relevance judgments when they help isolate retrieval defects.

## Research and attribution

The following **12 distinct practitioner articles** informed this skill. Attribution is to their actual bylines, including team bylines where no individual author is named. These writers did not review or endorse the repository. Source arguments, individual case studies, and this implementation's design choices are distinguished in the linked research notes.

| People / credited author | Writing | Contribution to this skill |
| --- | --- | --- |
| **Doug Turnbull** | [Prefer synthetic traffic over LLM-as-a-judge](https://softwaredoug.com/blog/2026/11/12/agent-search-traffic) — Nov 12, 2026 | Starting point: evaluate search sessions through the UI |
| **Doug Turnbull** | [I fixed Alamo Drafthouse's Search](https://softwaredoug.com/blog/2026/11/09/fixing-alamo-drafthouse-search) — Nov 9, 2026 | Menu-search example, prefix and vocabulary coverage |
| **Stefan Rössler** | [We Ran an Experiment with Synthetic Users: Here’s What We Found](https://www.userbrain.com/blog/synthetic-users-experiment/) — Apr 28, 2026 | Human-versus-synthetic usability comparison |
| **Maria Rosala and Kate Moran** | [Synthetic Users: If, When, and How to Use AI-Generated “Research”](https://www.nngroup.com/articles/synthetic-users/) — Jun 21, 2024 | Boundaries on synthetic research claims |
| **Rachel Banawa** | [Synthetic Users vs. Human Respondents: Same Conclusion, Less Variation](https://www.nngroup.com/articles/synthetic-users-vs-human-respondents/) — Oct 16, 2026 | Coverage and reduced response variation |
| **Jeff Sauro, Will Schiavone, and Jim Lewis** | [Using ChatGPT in Tree Testing: Experimental Results](https://measuringu.com/chatgpt4-tree-test/) — Apr 2, 2024 | Simulator competence can conceal human navigation difficulty |
| **Jo Kristian Bergum** | [Improving retrieval with LLM-as-a-judge](https://blog.vespa.ai/improving-retrieval-with-llm-as-a-judge/) — Jul 3, 2024 | Calibrated relevance diagnostics and zero-click satisfaction |
| **Neel Mishra** | [Clicks Are Feedback, Not Relevance Labels](https://neelmishra.github.io/blog/ml/search-and-retrieval/evaluation/online-experiments-and-click-bias.html) — Sep 2026 | Exposure, selection bias, and correct denominators |
| **Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, and Jiri De Jonghe** | [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) — Jan 9, 2026 | Independent outcomes, repeated trials, stable environments |
| **Hamel Husain and Shreya Shankar** | [AI Evals: Everything You Need to Know](https://hamel.dev/blog/posts/evals-faq/) — Sep 18, 2026 | Scenario dimensions, trace review, and real-data calibration |
| **The LangChain Team** | [Evaluating Deep Agents: Our Learnings](https://www.langchain.com/blog/evaluating-deep-agents-our-learnings) — Dec 3, 2025 | Final-state assertions and bounded simulations |
| **Sarah Gibbons and Kate Moran** | [AI Agents as Users](https://www.nngroup.com/articles/ai-agents-as-users/) — Apr 10, 2026 | Different observation and interaction channels |

Sources were checked on November 19, 2026. This is a selected practitioner reading list, not an exhaustive literature review. MeasuringU's publisher-authored indexed text was accessible; a direct page request returned 403. The notes disclose that access limit and avoid claiming that older survey/tree studies validate modern browser agents.

The schema, paired analysis tool, artifact conventions, frozen-comparison workflow, and prompt templates are this repository's synthesis. No full third-party article is copied. Third-party writings remain under their respective owners' rights; the repository's original code and documentation are MIT licensed.

## Development and validation

```sh
python3 -m unittest discover -s tests -v
ruff check scripts tests
git diff --check
```

Ruff is optional development tooling; if needed, install it in your development environment with `uv pip install ruff`. CI runs the tests on Python 3.9, 3.12, and 3.13 and runs lint separately. Local checks are not evidence that hosted CI has run.

Tests cover malformed input, duplicate IDs and assignments, pair confounds, denominators, missing variants, deterministic clustered resampling, zero-click success, and output protection. Real-browser collection, model-specific adherence, and human predictive validity require a target application and retained traces; they are not established by these tests.

See [validation notes](docs/validation.md) for the initial local checks and independent skill exercise.
