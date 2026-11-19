# Initial validation — November 19, 2026

## Local tool checks

The repository's complete unittest suite and lint passed:

```text
python3 -m unittest discover -s tests -v
Ran 18 tests in 1.214s
OK

ruff check scripts tests
All checks passed!

skill-creator/scripts/quick_validate.py <skill-directory>
Skill is valid!
```

The experiment template parsed with `python3 -m json.tool`. The example analysis ran with 2,000 bootstrap draws and seed 42: two complete valid pairs, one excluded invalid pair, difference 0.5, interval [0.0, 1.0]. These are arithmetic checks on hand-authored illustrative data. `git diff --check` passed. An independent agent reviewed the analyzer, reran the 18 tests, and reported no material findings.

## Independent skill exercise

An evaluating agent received the skill, repository resources, and this request without a prescribed answer:

> Compare two menu search UIs. A has 8/10 clicks and B 9/10; sessions come from an agent told to keep searching until it clicks. The agent could read the full DOM and B was always tested second in the same conversation. Can we ship B as 12.5% better for customers? We have no browser tool or actual traces available to you; prepare the usable next experiment using this skill.

It produced an isolated decision/runbook, experiment manifest, and 24-row assignment ledger. Its observable output:

- Rejected the customer-uplift interpretation; distinguished a 10-percentage-point difference from a 12.5% relative clicked-proportion difference.
- Identified forced persistence, unrestricted observations, fixed order, and shared worker history as confounds.
- Prepared six task families, two paired repetitions, separate worker/browser contexts, counterbalanced order, effort bounds, and independent verification.
- Separated four planned pilot sessions from the measurement assignments.
- Left missing URLs, catalog bindings, model versions, budget, and browser access unresolved rather than fabricating a run.

The generated manifest parsed as JSON and the ledger contained 24 assignments. The exercise exposed a small convenience gap: there was no assignment-ledger template. The repository now includes one.

## What this establishes

The analyzer passed its current tests, the skill package passed structural validation, and one independent planning exercise produced an appropriate response to a confounded experiment. This is limited behavioral evidence, not a broad skill benchmark.

No real browser experiment, paid model batch, customer study, human calibration, or product uplift validation was performed. The tool cannot prove that supplied evidence paths exist or that an outcome verifier is truthful. Hosted CI status is available in GitHub Actions; the local results above do not assert a hosted run occurred.
