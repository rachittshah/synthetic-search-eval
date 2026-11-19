"""Contract and regression tests for the public analyzer CLI and analysis path."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_sessions.py"
SPEC = importlib.util.spec_from_file_location("analyze_sessions", SCRIPT)
analyzer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analyzer)


def session(variant="A", pair="p1", scenario="s1", status="success", **changes):
    record = {
        "schema_version": 1,
        "experiment_id": "test-experiment",
        "scenario_id": scenario,
        "pair_id": pair,
        "variant": variant,
        "session_id": f"{pair}-{variant}",
        "model": "fixed-model-version",
        "status": status,
        "queries": ["burger"],
        "impressions": 4,
        "clicks": 1,
        "duration_ms": 1500,
        "seed": 37,
        "evidence": ["test-only-artifact.json"],
    }
    if status == "success":
        record["success_evidence"] = "Test fixture verifier confirms all task constraints."
    else:
        record["failure_reason"] = "Test fixture terminal reason."
    record.update(changes)
    return record


class AnalysisTests(unittest.TestCase):
    def test_success_is_not_inferred_from_clicks(self):
        rows = [session(clicks=0), session("B", status="failure", clicks=9)]
        result = analyzer.analyze(rows)
        self.assertEqual(result["paired"]["success_rate_difference"], -1)

    def test_invalid_excluded_abandonment_included(self):
        rows = [session(), session(pair="p2", status="invalid"), session(pair="p3", status="abandoned", queries=["a", "b", "c"])]
        variant = analyzer.analyze(rows)["variants"]["A"]
        self.assertEqual(variant["total_sessions"], 3)
        self.assertEqual(variant["valid_sessions"], 2)
        self.assertEqual(variant["success_rate"], 0.5)
        self.assertEqual(variant["effort_all_valid"]["queries"]["mean"], 2)
        self.assertEqual(variant["effort_successful"]["queries"]["mean"], 1)

    def test_missing_invalid_pairs_are_explicit(self):
        rows = [session(), session(pair="p2"), session("B", pair="p2", status="invalid")]
        result = analyzer.analyze(rows)
        self.assertEqual(result["paired"]["complete_valid_pairs"], 0)
        self.assertIsNone(result["paired"]["success_rate_difference"])
        self.assertEqual(result["paired"]["excluded_pairs"], [
            {"pair_id": "p1", "missing_variants": ["B"], "invalid_variants": []},
            {"pair_id": "p2", "missing_variants": [], "invalid_variants": ["B"]},
        ])

    def test_empty_variant_has_null_rates_and_effort(self):
        variant = analyzer.analyze([session()])["variants"]["B"]
        self.assertIsNone(variant["success_rate"])
        self.assertIsNone(variant["effort_all_valid"]["clicks"]["mean"])

    def test_one_scenario_has_no_interval_even_with_many_replicates(self):
        rows = [session(v, pair=f"p{i}") for i in range(30) for v in ("A", "B")]
        self.assertIsNone(analyzer.analyze(rows)["paired"]["confidence_interval_95"])

    def test_bootstrap_deterministic_and_clustered(self):
        rows = []
        for i in range(3):
            for j in range(i + 1):
                rows.extend([session("A", pair=f"p{i}-{j}", scenario=f"s{i}", status="failure"), session("B", pair=f"p{i}-{j}", scenario=f"s{i}", status="success" if i == 0 else "failure")])
        result = analyzer.analyze(rows, seed=7, bootstrap=200)
        self.assertEqual(result, analyzer.analyze(list(reversed(rows)), seed=7, bootstrap=200))
        self.assertEqual(result["paired"]["scenario_clusters"], 3)
        self.assertEqual(result["paired"]["success_rate_difference"], 1 / 6)
        self.assertEqual(result["paired"]["confidence_interval_95"], [0, 1])

    def test_reject_duplicate_sessions_and_assignments(self):
        for other in [session(), session(session_id="different-attempt")]:
            with self.subTest(other=other["session_id"]), self.assertRaisesRegex(ValueError, "duplicate"):
                analyzer.analyze([session(), other])

    def test_reject_pair_confounds(self):
        for field, value in [("scenario_id", "other"), ("model", "different-model"), ("seed", 123)]:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, f"mismatched {field}"):
                analyzer.analyze([session(), session("B", **{field: value})])

    def test_reject_mixed_experiments_and_extra_variants(self):
        with self.assertRaisesRegex(ValueError, "mixed experiment"):
            analyzer.analyze([session(), session("B", experiment_id="other")])
        with self.assertRaisesRegex(ValueError, "unexpected variant"):
            analyzer.analyze([session("C")])

    def test_empty_input_and_bad_parameters(self):
        with self.assertRaisesRegex(ValueError, "no sessions"):
            analyzer.analyze([])
        for kwargs in [{"baseline": "A", "candidate": "A"}, {"bootstrap": 0}, {"bootstrap": True}, {"seed": False}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                analyzer.analyze([session()], **kwargs)

    def test_schema_rejects_invalid_values(self):
        changes = [
            {"schema_version": True}, {"status": "running"}, {"queries": "burger"},
            {"queries": [""]}, {"evidence": []}, {"impressions": -1},
            {"impressions": True}, {"clicks": 1.5}, {"duration_ms": float("nan")},
            {"duration_ms": float("inf")}, {"duration_ms": -1}, {"duration_ms": True},
            {"seed": 1.5}, {"success_evidence": ""}, {"scenario_id": " "},
        ]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                analyzer.validate_record(session(**change))
        with self.assertRaisesRegex(ValueError, "failure_reason"):
            analyzer.validate_record(session(status="failure", failure_reason=""))

    def test_valid_failure_may_have_no_actions_or_evidence(self):
        record = session(status="invalid", queries=[], impressions=0, clicks=0, duration_ms=0, evidence=[])
        analyzer.validate_record(record)


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "sessions.jsonl"
        self.input.write_text(json.dumps(session()) + "\n" + json.dumps(session("B")) + "\n", encoding="utf-8")

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--input", str(self.input), *args], capture_output=True, text=True, check=False)

    def test_cli_stdout(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["paired"]["complete_valid_pairs"], 1)

    def test_output_cannot_clobber_existing_file(self):
        output = self.root / "report.json"
        first = self.run_cli("--output", str(output))
        self.assertEqual(first.returncode, 0, first.stderr)
        original = output.read_bytes()
        second = self.run_cli("--output", str(output))
        self.assertEqual(second.returncode, 2)
        self.assertEqual(output.read_bytes(), original)

    def test_malformed_input_has_line_number(self):
        self.input.write_text(self.input.read_text() + "{broken\n", encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("line 3", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_empty_input(self):
        self.input.write_text("\n", encoding="utf-8")
        self.assertIn("no sessions", self.run_cli().stderr)

    def test_duplicate_json_keys_and_nan_rejected(self):
        for content in ['{"schema_version": 1, "schema_version": 1}', '{"duration_ms": NaN}']:
            with self.subTest(content=content):
                self.input.write_text(content, encoding="utf-8")
                result = self.run_cli()
                self.assertEqual(result.returncode, 2)
                self.assertIn("line 1", result.stderr)

    def test_missing_input_is_human_readable_error(self):
        self.input.unlink()
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
