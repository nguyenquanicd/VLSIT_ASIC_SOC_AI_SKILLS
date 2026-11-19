#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_test_ip_tools.py
# Function : tests for vlsit_rtl_ip_scan.py, vlsit_ip_report_check.py and vlsit_ip_verify.py
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Test the analysis, report-check and verification scripts of vlsit-rtl-spec-change-implementer.

Run: python -m unittest discover -s tests -p "vlsit_test*.py" -v
No network and no third-party package are needed; every file is written in a temporary folder. Tests that need an
installed simulator are skipped when iverilog and vvp are not on PATH (reported as skipped, not passed).
"""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import vlsit_ip_report_check as rcheck  # noqa: E402
import vlsit_ip_verify as ver  # noqa: E402
import vlsit_rtl_ip_scan as scan  # noqa: E402

TOP = """
module top #(parameter int N = 3, parameter int W = 8) (
  input  logic clk, input logic rst_n,
  input  logic [W-1:0] din, input logic vld, output logic rdy,
  output logic [W-1:0] dout
);
  logic [W-1:0] mid;
  logic mid_vld;
  stage u_a (.clk(clk), .rst_n(rst_n), .din(din), .vld(vld), .rdy(rdy), .dout(mid), .vld_o(mid_vld));
  for (genvar i = 0; i < N; i++) begin : g_lane
    lane #(.W(W)) u_lane (.clk(clk), .din(mid), .dout());
  end
  stage u_b [1:0] (.clk(clk), .rst_n(rst_n), .din(mid), .vld(mid_vld), .rdy(), .dout(dout), .vld_o());
  unknown_ip u_x (.a(clk));
endmodule
"""
STAGE = """
module stage (input logic clk, input logic rst_n, input logic [7:0] din, input logic vld,
              output logic rdy, output logic [7:0] dout, output logic vld_o);
  lane #(.W(8)) u_l (.clk(clk), .din(din), .dout(dout));
  assign rdy = 1'b1;
  assign vld_o = vld;
endmodule
"""
LANE = """
module lane #(parameter int W = 4) (input logic clk, input logic [W-1:0] din, output logic [W-1:0] dout);
  always_ff @(posedge clk) dout <= din;
endmodule
"""
NON_ANSI = """
module old_style (clk, a, y);
  input clk;
  input [3:0] a;
  output reg y;
  parameter K = 2;
  localparam ADDR_CTRL = 8'h04;
  always @(posedge clk) y <= |a;
endmodule
"""


def write_tree(root, files):
    for name, text in files.items():
        (Path(root) / name).write_text(text, encoding="utf-8")


class ScanTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        write_tree(self.root, {"top.sv": TOP, "stage.sv": STAGE, "lane.sv": LANE})
        self.out = self.root / "scan.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.status = scan.main(["scan", str(self.root), "--out", str(self.out)])
        self.data = json.loads(self.out.read_text(encoding="utf-8"))

    def test_top_is_detected(self):
        self.assertEqual(self.data["top"], "top")

    def test_unresolved_instance_is_reported_with_status_one(self):
        self.assertEqual(self.status, 1)
        self.assertEqual([u["module"] for u in self.data["unresolved_instances"]], ["unknown_ip"])

    def test_generate_loop_count_uses_the_parameter(self):
        lane = [c for c in self.data["hierarchy"]["children"] if c["inst"] == "u_lane"][0]
        self.assertEqual(lane["count"], 3)

    def test_instance_array_count(self):
        stage_b = [c for c in self.data["hierarchy"]["children"] if c["inst"] == "u_b"][0]
        self.assertEqual(stage_b["count"], 2)

    def test_total_counts_multiply_along_the_path(self):
        # lane: 3 from the generate loop, plus 1 inside u_a, plus 1 inside each of the two u_b copies
        self.assertEqual(self.data["totals"]["lane"]["total"], 3 + 1 + 2)
        self.assertEqual(self.data["totals"]["stage"]["total"], 3)

    def test_ports_and_parameters(self):
        ports = {p["name"]: p for p in self.data["modules"]["top"]["ports"]}
        self.assertEqual(ports["din"]["width"], "[W-1:0]")
        self.assertEqual(ports["rdy"]["dir"], "output")
        self.assertEqual([p["name"] for p in self.data["modules"]["top"]["params"]], ["N", "W"])

    def test_tables_and_mermaid(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            scan.main(["tables", str(self.out)])
            scan.main(["mermaid", str(self.out)])
        text = buf.getvalue()
        self.assertIn("### Hierarchy (top-down)", text)
        self.assertIn("```mermaid", text)
        self.assertIn("#6a1b9a", text)
        self.assertIn("TOP block diagram: `top`", text)

    def test_mermaid_uses_only_white_black_purple(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            scan.main(["mermaid", str(self.out)])
        colors = set(c.lower() for c in __import__("re").findall(r"#[0-9a-fA-F]{6}\b", buf.getvalue()))
        self.assertLessEqual(colors, {"#ffffff", "#000000", "#6a1b9a"})

    def test_non_ansi_ports_and_csr_hints(self):
        write_tree(self.root, {"old.v": NON_ANSI})
        modules, _, _ = scan.scan_modules(str(self.root))
        ports = {p["name"]: p for p in modules["old_style"]["ports"]}
        self.assertEqual(ports["a"]["width"], "[3:0]")
        self.assertEqual(ports["y"]["dir"], "output")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            scan.main(["csr-hints", str(self.root), "--module", "old_style"])
        self.assertIn("ADDR_CTRL", buf.getvalue())

    def test_missing_directory_is_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(scan.main(["scan", str(self.root / "nope")]), 2)

    def test_evaluator_is_safe(self):
        self.assertEqual(scan.evaluate("N*2+1", {"N": 3}), 7)
        self.assertEqual(scan.evaluate("$clog2(8)", {}), 3)
        self.assertIsNone(scan.evaluate("__import__('os')", {}))
        self.assertIsNone(scan.evaluate("UNKNOWN+1", {}))


def section(n, title, body):
    return "## %s. %s\n%s\n" % (n, title, body)


def good_report(status="Awaiting user sign-off"):
    parts = ["# RTL IP Report — Demo — add wrap — plan version 1\n\nStatus: %s\n" % status,
             section(1, "Inputs and scope", "| Item | Value |\n|---|---|\n| Top | top |"),
             section(2, "Hierarchy (top-down)",
                     "| Level | Instance path | Module | Count | Basis | Source |\n|---|---|---|---|---|---|\n| 0 | top | top | 1 | top | top.sv:1 |\n| 1 | u_a | stage | 1 |  | top.sv:9 |\n| 2 | u_a.u_l | lane | 1 |  | stage.sv:3 |"),
             "## 3. Block diagrams\n### 3.1 TOP block diagram: `top`\n```mermaid\nflowchart LR\n  A-->B\n```\n"
             "#### Level 1 block diagram: `stage`\n```mermaid\nflowchart LR\n  A-->B\n```\n",
             section(4, "Functional analysis by instance",
                     "| Instance | Module | Role | Receives | Sends | Behavior | Evidence |\n|---|---|---|---|---|---|---|\n| u_a | stage | registers data | din | mid | pass-through | top.sv:9 |"),
             "## 5. Module interfaces and signals\n### 5.1 `top`\n| Port | Dir | Width | Domain | Kind | Protocol | Function | Evidence |\n|---|---|---|---|---|---|---|---|\n| din | input | 8 | clk | bus | custom | data | top.sv:3 |\n"
             "### 5.2 `stage`\n| Port | Dir | Width | Domain | Kind | Protocol | Function | Evidence |\n|---|---|---|---|---|---|---|---|\n| din | input | 8 | clk | bus | custom | data | stage.sv:2 |\n"
             "### 5.3 `lane`\n| Port | Dir | Width | Domain | Kind | Protocol | Function | Evidence |\n|---|---|---|---|---|---|---|---|\n| din | input | 8 | clk | bus | custom | data | lane.sv:2 |\n",
             section(6, "CSR map", "No software-visible registers."),
             section(7, "Software sequence (basic configuration)",
                     "| Step | Action | Register | Value | Wait | Purpose | Evidence |\n|---|---|---|---|---|---|---|\n| 1 | release reset | rst_n | 1 | none | start | top.sv:2 |"),
             "## 8. Requirement and modification analysis\n### 8.1 Requirement\nWrap the counter at 9.\n### 8.2 Mapping to the RTL\nlane.\n"
             "### 8.3 Strategies (at most three)\n| Strategy | Functional coverage | RTL change size | Software-flow impact | New module | Compat | Risk |\n|---|---|---|---|---|---|---|\n| A (recommended) | full | 1 line | none | none | kept | low |\n"
             "### 8.4 Affected files\nlane.sv\n### 8.5 Style profile\nkeep\n### 8.6 Minimal-change rationale\none line\n### 8.7 CSR delta\nNo CSR change.\n### 8.8 Software-sequence delta\nunchanged\n"
             "### 8.9 Pre-existing defects\nNone found.\n"
             "### 8.10 Test plan\n| Test | Kind | Checks | Item | Baseline | Modified | Source |\n|---|---|---|---|---|---|---|\n| t_basic | basic | count | existing | pass | pass | baseline |\n| t_wrap | feature | wrap | wrap | fail | pass | requirement |\n"
             "### 8.11 Budget and approval\n| Item | Value |\n|---|---|\n| Change budget | 5 % |\n| Baseline RTL code lines | 100 |\n| New modules | none |\n\nDo you approve plan version 1? Reply APPROVE, REVISE, or STOP.\n"]
    return "\n".join(parts)


IMPLEMENTED = """
## 9. Implementation results
### 9.1 Traceability and changed files
| Item | Module | file:line | Summary |
|---|---|---|---|
| wrap | lane | lane.sv:3 | compare with 9 |
### 9.2 Change metrics
| Metric | Value |
|---|---|
| Change percentage | 2.0 % |
| New modules | none |
### 9.3 Checks
| Check | Command | Result | Log |
|---|---|---|---|
| Lint | lint-diff | PASS | l.log |
| Tests | matrix | PASS | m.log |
### 9.4 Remaining risks and completion
none
"""


class ReportCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def check(self, text, stage=None, scan_json=None):
        path = self.dir / "rtl_ip_report.md"
        path.write_text(text, encoding="utf-8")
        rep, status, st = rcheck.check(str(path), scan_json, stage)
        return [m for lvl, m in rep.findings if lvl == "ERROR"]

    def test_good_plan_passes(self):
        self.assertEqual(self.check(good_report()), [])

    def test_missing_section_is_reported(self):
        text = good_report().replace("## 7. Software sequence (basic configuration)", "## 7x. Other")
        self.assertTrue(any("section 7" in e for e in self.check(text)))

    def test_two_recommended_or_four_strategies(self):
        text = good_report().replace("| A (recommended) | full | 1 line | none | none | kept | low |",
                                     "| A (recommended) | f | 1 | none | none | k | l |\n| B (recommended) | f | 1 | none | none | k | l |")
        self.assertTrue(any("exactly one" in e for e in self.check(text)))

    def test_feature_test_must_fail_on_baseline(self):
        text = good_report().replace("| t_wrap | feature | wrap | wrap | fail | pass |", "| t_wrap | feature | wrap | wrap | pass | pass |")
        self.assertTrue(any("feature test" in e for e in self.check(text)))

    def test_basic_and_feature_tests_are_required(self):
        text = good_report().replace("| t_basic | basic |", "| t_basic | feature |")
        self.assertTrue(any("basic" in e for e in self.check(text)))

    def test_pending_defect_blocks_implementation(self):
        text = good_report("Implemented").replace("None found.", "| ID | E | O | R | Ev | Status | Date |\n|---|---|---|---|---|---|---|\n| BUG-001 | a.sv:1 | x | y | z | PENDING | |") + IMPLEMENTED
        self.assertTrue(any("PENDING" in e for e in self.check(text)))

    def test_implemented_report_passes(self):
        self.assertEqual(self.check(good_report("Implemented") + IMPLEMENTED), [])

    def test_implemented_report_needs_percentage_and_check_results(self):
        bad = IMPLEMENTED.replace("| Change percentage | 2.0 % |", "| Change percentage | ? |").replace("| Tests | matrix | PASS | m.log |", "| Tests | matrix | done | m.log |")
        errors = self.check(good_report("Implemented") + bad)
        self.assertTrue(any("percentage" in e for e in errors))

    def test_placeholder_is_reported(self):
        self.assertTrue(any("placeholder" in e for e in self.check(good_report().replace("Wrap the counter at 9.", "<requirement text>"))))

    def test_scan_cross_check_flags_missing_module(self):
        scan_data = {"top": "top", "totals": {"stage": {}, "lane": {}, "ghost": {}},
                     "modules": {"top": {"child_modules": ["stage"]}, "stage": {"child_modules": ["lane"]},
                                 "lane": {"child_modules": []}, "ghost": {"child_modules": []}}}
        sp = self.dir / "scan.json"
        sp.write_text(json.dumps(scan_data), encoding="utf-8")
        errors = self.check(good_report(), scan_json=str(sp))
        self.assertTrue(any("ghost" in e for e in errors))

    def test_command_line_exit_codes(self):
        path = self.dir / "r.md"
        path.write_text(good_report(), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(rcheck.main([str(path)]), 0)
        path.write_text("# nothing", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(rcheck.main([str(path)]), 1)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(rcheck.main([str(self.dir / "missing.md")]), 2)


BASE_CNT = """module cnt (input logic clk, input logic rst_n, input logic en, output logic [3:0] q);
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) q <= 4'd0;
    else if (en) q <= q + 4'd1;
endmodule
"""
MOD_CNT = BASE_CNT.replace("q <= q + 4'd1;", "q <= (q == 4'd9) ? 4'd0 : q + 4'd1;")
TB_BASIC = """module tb_basic;
  logic clk=0, rst_n=0, en=0; logic [3:0] q;
  cnt u(.*);
  always #5 clk = ~clk;
  initial begin
    #12 rst_n = 1; en = 1;
    repeat (3) @(posedge clk); #1;
    if (q == 4'd3) $display("TB_RESULT: PASS count3"); else $display("TB_RESULT: FAIL count3");
    $finish;
  end
endmodule
"""
TB_WRAP = TB_BASIC.replace("tb_basic", "tb_wrap").replace("repeat (3)", "repeat (10)").replace("q == 4'd3", "q == 4'd0").replace("count3", "wrap9")


@unittest.skipUnless(shutil.which("iverilog") and shutil.which("vvp"), "iverilog and vvp are not installed")
class VerifyMatrixTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        r = Path(self.tmp.name)
        for d in ("base", "mod", "tests"):
            (r / d).mkdir()
        (r / "base" / "cnt.sv").write_text(BASE_CNT, encoding="utf-8")
        (r / "mod" / "cnt.sv").write_text(MOD_CNT, encoding="utf-8")
        (r / "tests" / "tb_basic.sv").write_text(TB_BASIC, encoding="utf-8")
        (r / "tests" / "tb_wrap.sv").write_text(TB_WRAP, encoding="utf-8")
        self.root = r

    def make_tests_json(self, kind_wrap="feature"):
        p = self.root / "tests" / "tests.json"
        p.write_text(json.dumps([{"name": "basic_count", "kind": "basic", "tb": "tb_basic.sv", "tb_top": "tb_basic"},
                                 {"name": "feature_wrap", "kind": kind_wrap, "tb": "tb_wrap.sv", "tb_top": "tb_wrap"}]), encoding="utf-8")
        return p

    def run_matrix(self, tests):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = ver.main(["matrix", "--baseline", str(self.root / "base"), "--modified", str(self.root / "mod"),
                           "--tests", str(tests), "--out-dir", str(self.root / "out"), "--tool", "iverilog"])
        return rc, buf.getvalue()

    def test_expectations_met(self):
        rc, out = self.run_matrix(self.make_tests_json())
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULT: PASS", out)

    def test_feature_test_that_passes_on_baseline_is_a_finding(self):
        rc, out = self.run_matrix(self.make_tests_json(kind_wrap="basic"))
        self.assertEqual(rc, 1, out)
        self.assertIn("NO", out)

    def test_compile_error_is_a_failure(self):
        (self.root / "mod" / "cnt.sv").write_text("module cnt(; endmodule", encoding="utf-8")
        rc, out = self.run_matrix(self.make_tests_json())
        self.assertEqual(rc, 1, out)
        self.assertIn("compile error", out)


class VerifyUnitTest(unittest.TestCase):
    def test_result_parser(self):
        self.assertEqual(ver.parse_result("TB_RESULT: PASS a\n", 0)[0], "pass")
        self.assertEqual(ver.parse_result("TB_RESULT: PASS a\nTB_RESULT: FAIL b\n", 0)[0], "fail")
        self.assertEqual(ver.parse_result("nothing\n", 0)[0], "fail")
        self.assertEqual(ver.parse_result("TB_RESULT: PASS a\n", 1)[0], "fail")

    def test_diagnostic_normalization_ignores_paths_and_lines(self):
        a = ver.normalize_diag("%Warning-UNUSED: /x/y/a.sv:12:3: Signal is not used: 'q'")
        b = ver.normalize_diag("%Warning-UNUSED: C:\\w\\b.sv:99:1: Signal is not used: 'q'")
        self.assertEqual(a, b)

    def test_missing_tool_is_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.sv").write_text("module a; endmodule\n", encoding="utf-8")
            orig = ver.tool_paths
            ver.tool_paths = lambda tool_dir: {k: None for k in ("verilator", "slang", "iverilog", "vvp", "yosys")}
            try:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = ver.main(["lint", "--rtl-dir", tmp, "--top", "a"])
            finally:
                ver.tool_paths = orig
            self.assertEqual(rc, 3)
            self.assertIn("NOT RUN", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
