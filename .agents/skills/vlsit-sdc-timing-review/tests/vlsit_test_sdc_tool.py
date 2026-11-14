#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_test_sdc_tool.py
# Function : unit tests for the SDC and timing review scripts (R-006 to R-018)
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Run: python vlsit_test_sdc_tool.py   (standard library only; exit 0 when every test passes)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
SDC_PARSE = SCRIPTS / "vlsit_sdc_parse.py"
SDC_CROSS = SCRIPTS / "vlsit_crosscheck_sdc.py"
SDC_SCORE = SCRIPTS / "vlsit_scorecard.py"
SDC_REPORT = SCRIPTS / "vlsit_report_check.py"


def run(script, *args):
    result = subprocess.run([sys.executable, str(script)] + [str(a) for a in args],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.returncode, result.stdout + result.stderr


def load(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


class Parse(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.sdc = Path(self.tmp.name) / "t.sdc"
        self.out = Path(self.tmp.name) / "c.json"

    def test_expands_variables_and_parses_common_forms(self):
        self.sdc.write_text(
            "set T 10.0\n"
            "create_clock -name clk_a -period $T [get_ports i_clk_a]\n"
            "create_clock -name clk_b -period 20 [get_ports i_clk_b]\n"
            "set_clock_groups -asynchronous -group [get_clocks clk_a] -group [get_clocks clk_b]\n"
            "set_false_path -from [get_clocks clk_a] -to [get_clocks clk_b]\n"
            "set_input_delay -clock clk_a 1.0 [get_ports i_data]\n", encoding="utf-8")
        code, _text = run(SDC_PARSE, self.sdc, "--out", self.out)
        self.assertEqual(code, 0)
        data = load(self.out)
        self.assertEqual(data["counts"]["clocks"], 2)
        self.assertEqual(data["clocks"][0]["period"], "10.0")
        self.assertEqual(data["counts"]["groups"], 1)
        self.assertEqual(data["clock_groups"][0]["groups"], ["clk_a", "clk_b"])
        self.assertEqual(data["exceptions"][0]["from"], ["clk_a"])
        self.assertEqual(data["exceptions"][0]["to"], ["clk_b"])
        self.assertEqual(data["io_delays"][0]["ports"], ["i_data"])
        self.assertEqual(data["counts"]["unparsed"], 0)

    def test_unresolved_command_is_recorded_unparsed(self):
        self.sdc.write_text(
            "create_clock -name clk_a -period 10 [get_ports i_clk_a]\n"
            "set_max_delay -from $NOT_DEFINED -to [get_ports i_data]\n", encoding="utf-8")
        code, _text = run(SDC_PARSE, self.sdc, "--out", self.out)
        self.assertEqual(code, 0)
        data = load(self.out)
        self.assertEqual(data["counts"]["unparsed"], 1)
        self.assertEqual(data["unparsed"][0]["reason"], "exception endpoints not resolved")


class Crosscheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.rtl = Path(self.tmp.name) / "rtl.json"
        self.rtl.write_text(json.dumps({
            "modules": [{"name": "top", "file": "top.sv", "line": 1,
                         "ports": [{"name": "i_clk_a", "direction": "input", "width": "1", "line": 3},
                                   {"name": "i_clk_b", "direction": "input", "width": "1", "line": 4},
                                   {"name": "i_rst_n", "direction": "input", "width": "1", "line": 5},
                                   {"name": "i_data", "direction": "input", "width": "8", "line": 6},
                                   {"name": "o_data", "direction": "output", "width": "8", "line": 7}],
                         "instances": []}],
            "module_names": ["top"],
        }), encoding="utf-8")

    def _crosscheck(self, sdc_text):
        sdc = Path(self.tmp.name) / "s.sdc"
        sdc.write_text(sdc_text, encoding="utf-8")
        constraints = Path(self.tmp.name) / "c.json"
        run(SDC_PARSE, sdc, "--out", constraints)
        out = Path(self.tmp.name) / "x.json"
        code, text = run(SDC_CROSS, "--sdc", constraints, "--rtl", self.rtl, "--out", out)
        return code, load(out)

    def test_reset_via_input_delay_and_grouped_pair_are_clean(self):
        code, report = self._crosscheck(
            "create_clock -name clk_a -period 10 [get_ports i_clk_a]\n"
            "create_clock -name clk_b -period 20 [get_ports i_clk_b]\n"
            "set_clock_groups -asynchronous -group [get_clocks clk_a] -group [get_clocks clk_b]\n"
            "set_input_delay -clock clk_a 1.0 [get_ports i_data]\n"
            "set_input_delay -clock clk_a 1.0 [get_ports i_rst_n]\n")
        self.assertEqual(code, 0)
        self.assertEqual(report["counts"]["findings"], 0)

    def test_unconstrained_reset_and_pair_are_reported(self):
        code, report = self._crosscheck(
            "create_clock -name clk_a -period 10 [get_ports i_clk_a]\n"
            "create_clock -name clk_b -period 20 [get_ports i_clk_b]\n"
            "set_input_delay -clock clk_a 1.0 [get_ports i_data]\n")
        self.assertEqual(code, 1)
        kinds = {finding["kind"] for finding in report["findings"]}
        self.assertIn("reset_without_constraint", kinds)
        self.assertIn("clock_pair_without_relationship", kinds)


class Scorecard(unittest.TestCase):
    def test_sdc_areas_and_unknown_area(self):
        with tempfile.TemporaryDirectory() as folder:
            good = Path(folder) / "good.json"
            good.write_text(json.dumps({
                "ip": "x", "reviewed_sdc": "x.sdc", "date": "2026-11-14",
                "areas": [{"id": "clock_definition", "score": 4, "justification": "ok"}],
                "findings": [],
            }), encoding="utf-8")
            code, text = run(SDC_SCORE, good, "--out", str(Path(folder) / "g.md"))
            self.assertEqual(code, 0)
            self.assertIn("Verdict: Ready", text)
            bad = Path(folder) / "bad.json"
            bad.write_text(json.dumps({
                "ip": "x", "reviewed_sdc": "x.sdc", "date": "2026-11-14",
                "areas": [{"id": "market_position", "score": 4, "justification": "ok"}],
                "findings": [],
            }), encoding="utf-8")
            code, text = run(SDC_SCORE, bad)
            self.assertEqual(code, 2)
            self.assertIn("unknown area", text)


class ReportCheck(unittest.TestCase):
    def test_matrix_row_required_per_clock_and_pair(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            sdc = folder / "t.sdc"
            sdc.write_text(
                "create_clock -name clk_a -period 10 [get_ports i_clk_a]\n"
                "create_clock -name clk_b -period 20 [get_ports i_clk_b]\n", encoding="utf-8")
            constraints = folder / "c.json"
            run(SDC_PARSE, sdc, "--out", constraints)
            matrix = folder / "matrix.csv"
            matrix.write_text(
                "Clock or pair,Domain,Relationship,RTL evidence,SDC construct,Line,Status\n"
                "clk_a,A,---,port i_clk_a,create_clock,1,match\n"
                "clk_b,B,---,port i_clk_b,create_clock,2,match\n"
                "clk_a / clk_b,A / B,asynchronous,synchronizer,set_clock_groups,3,verify\n",
                encoding="utf-8")
            report = folder / "REVIEW_SDC.md"
            chapters = ["## 1. Executive summary / Tóm tắt điều hành\n**EN.** x\n**VI.** x",
                        "## 2. Scorecard / Bảng điểm\n| table |",
                        "## 3. Clock definition / Định nghĩa clock\n**EN.** x\n**VI.** x",
                        "## 4. Generated clocks / Generated clock\n**EN.** x\n**VI.** x",
                        "## 5. Clock relationships / Quan hệ giữa các clock\n**EN.** x\n**VI.** x",
                        "## 6. Timing exceptions / Ngoại lệ timing\n**EN.** x\n**VI.** x",
                        "## 7. Input and output delays / Trễ vào ra\n**EN.** x\n**VI.** x",
                        "## 8. Clock uncertainty and latency / Uncertainty\n**EN.** x\n**VI.** x",
                        "## 9. Reset structure / Cấu trúc reset\n**EN.** x\n**VI.** x",
                        "## 10. CDC structure / Cấu trúc CDC\n**EN.** x\n**VI.** x",
                        "## 11. Operating conditions and corners / Corner\n**EN.** x\n**VI.** x",
                        "## 12. Sign-off criteria / Tiêu chí sign-off\n**EN.** x\n**VI.** x",
                        "## 13. Constraint matrix / Ma trận ràng buộc\n| table |",
                        "## 14. Fix owner / Trách nhiệm sửa\n**EN.** x\n**VI.** x",
                        "## 15. Proposed SDC patch / Đề xuất sửa SDC\n**EN.** x\n**VI.** x\n```diff\n+ a\n```",
                        "## 16. Actions / Hành động\n**EN.** x\n**VI.** x",
                        "## 17. Evidence appendix / Phụ lục bằng chứng\n**EN.** x\n**VI.** x",
                        "| ID | Severity | Area | Finding (EN) | Phát hiện (VI) | Locator | Owner |",
                        "| F-001 | Major | clock_relationships | FACT x | y | section 1.1 | SDC |"]
            report.write_text("\n".join(chapters), encoding="utf-8")
            code, text = run(SDC_REPORT, report, "--constraints", constraints,
                             "--clock-matrix", matrix, "--out", str(folder / "f.json"))
            self.assertEqual(code, 0, text)
            # remove the pair row; the check must fail
            matrix.write_text(
                "Clock or pair,Domain,Relationship,RTL evidence,SDC construct,Line,Status\n"
                "clk_a,A,---,port i_clk_a,create_clock,1,match\n"
                "clk_b,B,---,port i_clk_b,create_clock,2,match\n", encoding="utf-8")
            code, text = run(SDC_REPORT, report, "--constraints", constraints,
                             "--clock-matrix", matrix, "--out", str(folder / "f.json"))
            self.assertEqual(code, 2)
            self.assertIn("clock pair clk_a / clk_b has no constraint matrix row", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
