#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_test_change_tools.py
# Function : unit and command-line tests for vlsit_csr_info.py
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
