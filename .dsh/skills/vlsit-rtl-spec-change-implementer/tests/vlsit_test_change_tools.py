#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_test_change_tools.py
# Function : unit and command-line tests for vlsit_csr_info.py and vlsit_change_review_check.py
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Test the scripts of the vlsit-rtl-spec-change-implementer skill.

Run: python -m unittest discover -s tests -v
No network and no third-party package are needed; every file is written in a temporary folder.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import vlsit_csr_info as csi  # noqa: E402

PY = sys.executable


def run(script, *arguments):
    result = subprocess.run([PY, str(SCRIPT_DIR / script)] + [str(item) for item in arguments],
                            capture_output=True, text=True, encoding="utf-8")
    return result.returncode, result.stdout + result.stderr


def register(name, offset, fields, **extra):
    item = {"name": name, "offset": offset, "description": "%s register. Controls one documented function." % name,
            "fields": fields}
    item.update(extra)
    return item


def field(name, bits, kind="rw", reset="0x0"):
    return {"name": name, "bits": bits, "type": kind, "reset": reset,
            "description": "%s field. Documents the behavior of this bit range for software." % name}


def version_register(minor="0x1"):
    return register("dma_version", "0x0", [
        field("major", "[31:16]", "ro", "0x1"),
        field("minor", "[15:0]", "ro", minor)])


def ctrl_register():
    return register("dma_ctrl", "0x4", [
        field("enable", "[0]"),
        field("mode", "[2:1]"),
        field("reserved", "[31:3]", "ro")])


def channel_bank():
    return register("dma_chn", "0x10", [
        field("start", "[0]"),
        field("reserved", "[31:1]", "ro")],
        repeat={"mode": "FIXED", "count": 2, "stride": "0x4"})


def trace_register(offset="0x20"):
    return register("dma_trace", offset, [
        field("channel", "[1:0]", "ro"),
        field("valid", "[2]", "ro"),
        field("reserved", "[31:3]", "ro")])


def description(registers, minor="0x1"):
    return {"module": "m_vlsit_csr_dma", "prefix": "dma", "async": 0,
            "ip_version": {"major": 1, "minor": int(minor, 16)}, "registers": registers}


SPEC_BODIES = [
    ("Purpose, scope, and product context", "The delta contract of the existing controller."),
    ("Normative references and precedence", "VLSIT_RTL_Design_Rule.md and APB4 apply."),
    ("Requirements and traceability", "| ID | Requirement | Verification |\n|---|---|---|\n"
                                      "| REQ-FUNC-101 | The IP shall keep arbitration and shall add a trace word. | Simulation |\n"
                                      "| REQ-ERR-101 | The IP shall pulse the error output. | Assertion |"),
    ("Features and configurations", "The existing configuration set is unchanged."),
    ("Architecture", "The existing blocks are preserved; one register is added."),
    ("External interfaces and ports", "The existing ports are preserved."),
    ("Clock, reset, and power", "The existing clock and reset are preserved."),
    ("Parameters and elaboration configurations", "The existing parameters keep their defaults."),
    ("Data representation and arithmetic", "The trace word holds the channel index."),
    ("Detailed functional behavior", "The state machine keeps its states and adds one output register."),
    ("Register and programming model", "The register map is defined in the CSR workbook only."),
    ("Error handling and recovery", "The existing error mapping is preserved."),
    ("Performance, power, and area", "One register is added and no pipeline stage."),
    ("RTL implementation contract", "Only rtl/m_dma_core.sv may change; the style is kept."),
    ("Verification specification", "Directed simulation covers the trace word."),
    ("DFT and testability", "The existing scan chain observes the new register."),
    ("Physical design and timing integration", "The existing constraints apply."),
    ("Security, safety, and reliability", "The trace word exposes no secret data."),
    ("Requirement-to-verification traceability", "| Requirement | Verification |\n|---|---|\n"
                                                 "| REQ-FUNC-101 | simulation |\n| REQ-ERR-101 | assertion |"),
    ("Assumptions, dependencies, and decisions", "The user confirmed the defect on 2026-11-15."),
    ("Glossary", "CSR, DMA and RTL are defined in the skill glossary."),
    ("References used to shape this template", "The VLSIT template and the old specification."),
]


def spec_text(extra=""):
    parts = ["# DMA Controller Design Specification", ""]
    for number, (title, body) in enumerate(SPEC_BODIES, start=1):
        parts += ["## %d. %s" % (number, title), "", body, ""]
    if extra:
        parts += [extra, ""]
    return "\n".join(parts)


def review_text(status="Awaiting user sign-off", bug_status="CONFIRMED", bug_requirement="REQ-ERR-101",
                bug_date="2026-11-15", offset="0x0020", validation="not run", modules="none",
                budget="5", metrics=None, reconciliation="12 statements kept, 3 revised, 1 rerouted"):
    if metrics is None:
        metrics = ("| Metric | Value |\n|---|---|\n| Baseline RTL code lines | <n> |\n| Added code lines | <n> |\n"
                   "| Deleted code lines | <n> |\n| Change percentage | <n.n> % |\n"
                   "| Changed files | `<file>.sv` |\n| CSR delta | `<n>` added |\n"
                   "| Review check | `vlsit_change_review_check.py` RESULT: PASS |")
    return """# RTL Change Review — DMA trace channel — plan version 1

Status: {status}

## 1. Design and input summary
RTL root `rtl/`, 6 modules. Old specification `doc/DMA_HDS_v0.9.md`; rewritten specification
`VLSIT_DMA_HDS.md`. Task-start snapshot in `snapshot/`.

## 2. Specification rewrite
| Item | Value |
|---|---|
| Rewritten specification | `VLSIT_DMA_HDS.md`, version 0.2 |
| Template and sections | VLSIT template, 22 sections |
| As-is evidence | `rtl/m_dma_core.sv:88` for the FSM |
| Old-specification reconciliation | {reconciliation} |
| Reference-IP research | not used |

## 3. Requirement comparison
| ID | New requirement | Preserved behavior | Current RTL behavior (file:line) | Added behavior | Verification method |
|---|---|---|---|---|---|
| REQ-FUNC-101 | keep arbitration and add a trace word | round-robin | `rtl/m_dma_core.sv:88` | one trace word | directed simulation |
| REQ-ERR-101 | keep the error map and pulse the output | error map | `rtl/m_dma_core.sv:131` | one-cycle pulse | assertion |

## 4. Pre-existing defect report
| ID | RTL evidence | Observed behavior | Required behavior | Evidence | Status | Decision date | Requirement |
|---|---|---|---|---|---|---|---|
| BUG-001 | `rtl/m_dma_core.sv:131` | the error output stays low | one-cycle pulse | waveform `sim/dma_err.vcd` | {bug_status} | {bug_date} | {bug_requirement} |

## 5. Affected modules and files
| Module | File | Code region | Proposed change | Reason |
|---|---|---|---|---|
| m_dma_core | `rtl/m_dma_core.sv` | always_ff 88-140 | add the trace word | REQ-FUNC-101 |

## 6. Design choices (max three, ranked, one recommended)
| Strategy | Functional coverage | Change size | Compatibility | Complexity | Risk |
|---|---|---|---|---|---|
| A (recommended) | complete | 12 lines | unchanged | low | low |

## 7. Minimal-change rationale and style profile
The arbitration block is explicitly excluded.

| Convention | Current RTL evidence | Rule applied to the change |
|---|---|---|
| Module naming | `rtl/m_dma_core.sv:1` | keep the `m_` prefix |
| Reset style | `rtl/m_dma_core.sv:70` | keep the synchronous reset |
| FSM encoding | `rtl/m_dma_core.sv:88` | keep the enum |

## 8. CSR delta
| Register | Baseline state | New state | Offset | Free-range evidence | Policy | Approval |
|---|---|---|---|---|---|---|
| `dma_version` | minor 1 | minor 2 | 0x0 | — | unchanged | — |
| `dma_trace` | absent | new register | {offset} | free between 0x0014 and the map end | added-free | — |

CSR INFO file: `DMA_CSR_info.json`; delta result: `csr_delta.json`.

## 9. Proposed validation
| Check | Command | Expected evidence | Status (not run) |
|---|---|---|---|
| Compile | `iverilog -g2012 -o build/top.out rtl/m_dma_core.sv tb/tb_dma.sv` | no error | {validation} |

## 10. Approval and budget
| Item | Value |
|---|---|
| Change budget | {budget} % of the baseline RTL code lines |
| Baseline RTL code lines | 420 |
| Maximum files changed | 2 |
| New modules allowed | {modules} |
| Register policy | existing registers unchanged; new registers at free addresses |

Do you approve plan version 1? Reply APPROVE, REVISE, or STOP.

## 11. Final implementation report (added after approval)
Traceability: REQ-FUNC-101 to `rtl/m_dma_core.sv:132`; REQ-ERR-101 to `rtl/m_dma_core.sv:131`.

{metrics}
""".format(status=status, bug_status=bug_status, bug_requirement=bug_requirement, bug_date=bug_date,
           offset=offset, validation=validation, modules=modules, budget=budget, metrics=metrics,
           reconciliation=reconciliation)


IMPLEMENTED_METRICS = ("| Metric | Value |\n|---|---|\n| Baseline RTL code lines | 420 |\n| Added code lines | 8 |\n"
                       "| Deleted code lines | 2 |\n| Change percentage | 2.4 % |\n"
                       "| Changed files | `rtl/m_dma_core.sv` |\n| CSR delta | 1 added, 1 unchanged |\n"
                       "| Review check | `vlsit_change_review_check.py` RESULT: PASS |")


class ReviewCheckTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def write(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def check(self, text, spec=True, regs=True, **changes):
        review = self.write("rtl_change_review.md", text)
        arguments = [review]
        if spec:
            arguments += ["--spec", self.write("VLSIT_DMA_HDS.md", spec_text())]
        if regs:
            arguments += ["--regs", self.write("regs.json", json.dumps(description(
                [version_register("0x2"), ctrl_register(), channel_bank(), trace_register()])))]
        return run("vlsit_change_review_check.py", *arguments)

    def test_plan_passes(self):
        code, output = self.check(review_text())
        self.assertEqual(code, 0, output)
        self.assertIn("RESULT: PASS", output)

    def test_implemented_report_passes(self):
        text = review_text(status="Implemented", validation="PASS", metrics=IMPLEMENTED_METRICS)
        code, output = self.check(text)
        self.assertEqual(code, 0, output)

    def test_percentage_mismatch_is_reported(self):
        metrics = IMPLEMENTED_METRICS.replace("2.4 %", "9.9 %")
        code, output = self.check(review_text(status="Implemented", validation="PASS", metrics=metrics))
        self.assertEqual(code, 1)
        self.assertIn("does not match", output)

    def test_budget_overrun_is_reported(self):
        metrics = (IMPLEMENTED_METRICS.replace("| Added code lines | 8 |", "| Added code lines | 30 |")
                   .replace("| Deleted code lines | 2 |", "| Deleted code lines | 10 |")
                   .replace("2.4 %", "9.5 %"))
        code, output = self.check(review_text(status="Implemented", validation="PASS", metrics=metrics))
        self.assertEqual(code, 1)
        self.assertIn("exceeds the approved budget", output)

    def test_pending_defect_blocks_implementation(self):
        text = review_text(status="Implemented", validation="PASS", bug_status="PENDING",
                           bug_requirement="REQ-ERR-101", bug_date="2026-11-15",
                           metrics=IMPLEMENTED_METRICS)
        code, output = self.check(text)
        self.assertEqual(code, 1)
        self.assertIn("blocks implementation", output)

    def test_unrun_check_blocks_completion(self):
        text = review_text(status="Implemented", validation="not run", metrics=IMPLEMENTED_METRICS)
        code, output = self.check(text)
        self.assertEqual(code, 1)
        self.assertIn("still 'not run'", output)

    def test_missing_section_is_reported(self):
        text = review_text().replace("## 7. Minimal-change rationale and style profile",
                                     "### 7. Minimal-change rationale and style profile")
        code, output = self.check(text)
        self.assertEqual(code, 1)
        self.assertIn("missing section", output)

    def test_new_module_is_rejected(self):
        code, output = self.check(review_text(modules="one"))
        self.assertEqual(code, 1)
        self.assertIn("new modules allowed must be 'none'", output)

    def test_confirmed_defect_requirement_must_exist(self):
        text = review_text(bug_requirement="REQ-ERR-909")
        code, output = self.check(text)
        self.assertEqual(code, 1)
        self.assertIn("REQ-ERR-909 is missing from section 3", output)

    def test_csr_offset_must_match_description(self):
        code, output = self.check(review_text(offset="0x0024"))
        self.assertEqual(code, 1)
        self.assertIn("differs from the description offset", output)

    def test_from_scratch_wording_is_rejected(self):
        review = self.write("rtl_change_review.md", review_text())
        spec = self.write("VLSIT_DMA_HDS.md", spec_text("The RTL shall be implemented from scratch."))
        code, output = run("vlsit_change_review_check.py", review, "--spec", spec)
        self.assertEqual(code, 1)
        self.assertIn("from scratch", output)

    def test_missing_spec_section_is_reported(self):
        review = self.write("rtl_change_review.md", review_text())
        spec = self.write("VLSIT_DMA_HDS.md", spec_text().replace("## 21. Glossary", "## 21. Terms"))
        code, output = run("vlsit_change_review_check.py", review, "--spec", spec)
        self.assertEqual(code, 1)
        self.assertIn("section 21 title", output)


class CsrInfoTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def write(self, name, document):
        path = self.root / name
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def test_expand_fixed_repeat(self):
        entries = csi.expand(description([version_register(), channel_bank()])["registers"])
        names = [entry["name"] for entry in entries]
        self.assertEqual(names, ["dma_version", "dma_chn_0", "dma_chn_1"])
        self.assertEqual([entry["offset"] for entry in entries], [0, 0x10, 0x14])

    def test_info_layout_and_check(self):
        regs = self.write("regs.json", description([version_register(), ctrl_register(), channel_bank(), trace_register()]))
        info = self.root / "DMA_CSR_info.json"
        code, output = run("vlsit_csr_info.py", "info", regs, "--out", info, "--author", "Test (user)")
        self.assertEqual(code, 0, output)
        document = json.loads(info.read_text(encoding="utf-8"))
        self.assertEqual(document["Table - Configuration"][0]["Protocol"], "APB4")
        self.assertEqual(document["Table - Configuration"][0]["Register Event Sideband"], "0")
        names = [entry["Register Name"] for entry in document["Table - Register Definition"]]
        self.assertEqual(names, ["dma_version", "dma_ctrl", "dma_chn_0", "dma_chn_1", "dma_trace"])
        first = document["Table - Register Definition"][0]
        self.assertIn("Descriprtion", first)
        self.assertEqual(first["Bits"][0]["Bit Field"], "[31:16]")
        code, output = run("vlsit_csr_info.py", "check", info, "--regs", regs)
        self.assertEqual(code, 0, output)
        self.assertIn("RESULT: PASS", output)

    def test_check_detects_reset_mismatch(self):
        document = csi.build_info(description([version_register(), ctrl_register(), channel_bank(), trace_register()]),
                                  author="Test (user)")
        document["Table - Register Definition"][1]["Reset Value"] = "0x00000010"
        path = self.write("info.json", document)
        regs = self.write("regs.json", description([version_register(), ctrl_register(), channel_bank(), trace_register()]))
        code, output = run("vlsit_csr_info.py", "check", path, "--regs", regs)
        self.assertEqual(code, 1)
        self.assertIn("does not match the fields", output)

    def test_diff_accepts_free_address(self):
        baseline = self.write("base.json", description([version_register(), ctrl_register(), channel_bank()]))
        current = self.write("new.json", description([version_register("0x2"), ctrl_register(), channel_bank(),
                                                      trace_register()]))
        code, output = run("vlsit_csr_info.py", "diff", baseline, current, "--json")
        self.assertEqual(code, 0, output)
        result = json.loads(output)
        self.assertEqual(result["counts"]["added"], 1)
        self.assertEqual(result["counts"]["version"], 1)
        self.assertIn("free between", result["added"][0]["evidence"])
        self.assertEqual(result["added"][0]["offset"], "0x0020")

    def test_diff_rejects_occupied_address(self):
        baseline = self.write("base.json", description([version_register(), ctrl_register(), channel_bank()]))
        current = self.write("new.json", description([version_register("0x2"), ctrl_register(), channel_bank(),
                                                      trace_register("0x0014")]))
        code, output = run("vlsit_csr_info.py", "diff", baseline, current, "--json")
        self.assertEqual(code, 1)
        result = json.loads(output)
        self.assertEqual(result["findings"][0]["kind"], "occupied")

    def test_diff_requires_approval_for_a_change(self):
        baseline = self.write("base.json", description([version_register(), ctrl_register()]))
        changed = ctrl_register()
        changed["fields"].insert(2, field("trace_en", "[3]"))
        changed["fields"][3]["bits"] = "[31:4]"
        current = self.write("new.json", description([version_register("0x2"), changed]))
        code, output = run("vlsit_csr_info.py", "diff", baseline, current)
        self.assertEqual(code, 1)
        self.assertIn("[modified]", output)
        code, output = run("vlsit_csr_info.py", "diff", baseline, current, "--allow-modify", "dma_ctrl")
        self.assertEqual(code, 0, output)
        self.assertIn("MODIFIED  dma_ctrl", output)

    def test_parameterized_bank_reserves_its_maximum(self):
        bank = register("dma_mon", "0x30", [field("count", "[7:0]", "ro"), field("reserved", "[31:8]", "ro")],
                        repeat={"mode": "PARAMETERIZED", "count": 2, "stride": "0x4", "max": 4})
        baseline = self.write("base.json", description([version_register(), bank]))
        current = self.write("new.json", description([version_register("0x2"), bank, trace_register("0x0038")]))
        code, output = run("vlsit_csr_info.py", "diff", baseline, current, "--json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["findings"][0]["kind"], "occupied")

    def test_major_version_change_is_reported(self):
        baseline = self.write("base.json", description([version_register(), ctrl_register()]))
        current = self.write("new.json", description([version_register("0x2"), ctrl_register()]))
        current_document = json.loads(current.read_text(encoding="utf-8"))
        current_document["registers"][0]["fields"][0]["reset"] = "0x2"
        current.write_text(json.dumps(current_document), encoding="utf-8")
        code, output = run("vlsit_csr_info.py", "diff", baseline, current, "--json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["findings"][0]["kind"], "version-major")

    def test_bad_bits_are_rejected(self):
        with self.assertRaises(ValueError):
            csi.parse_bits("[3:5]")


if __name__ == "__main__":
    unittest.main()
