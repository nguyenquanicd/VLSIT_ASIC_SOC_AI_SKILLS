#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_test_csr_tool.py
# Function : unit tests for the naming and description checks of vlsit_csr_tool.py (R-032 to R-034)
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Run: python vlsit_test_csr_tool.py   (standard library only; exit 0 when every test passes)."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import vlsit_csr_tool as T  # noqa: E402

GOOD = copy.deepcopy(T.SAMPLE)


def errors(doc):
    return T.check(doc, auto_reserved=True)


class NamingAndDescription(unittest.TestCase):
    def test_sample_passes(self):
        self.assertEqual(errors(GOOD), [])

    def test_missing_prefix(self):
        d = copy.deepcopy(GOOD)
        del d["prefix"]
        self.assertTrue(any("prefix must be" in e for e in errors(d)))

    def test_register_without_prefix(self):
        d = copy.deepcopy(GOOD)
        d["registers"][0]["name"] = "ctrl"
        self.assertTrue(any("must start with the design prefix" in e for e in errors(d)))

    def test_field_name_too_long(self):
        d = copy.deepcopy(GOOD)
        d["registers"][0]["fields"][0]["name"] = "a_field_name_that_is_far_too_long"
        self.assertTrue(any("limit is 20" in e for e in errors(d)))

    def test_upper_case_name(self):
        d = copy.deepcopy(GOOD)
        d["registers"][0]["fields"][0]["name"] = "En"
        self.assertTrue(any("lower-case" in e for e in errors(d)))

    def test_register_description_two_lines(self):
        d = copy.deepcopy(GOOD)
        d["registers"][0]["description"] = "Demo control register. Main meaning here.\nSecond line"
        self.assertTrue(any("register description" in e for e in errors(d)))

    def test_register_description_without_meaning(self):
        d = copy.deepcopy(GOOD)
        d["registers"][0]["description"] = "Control"
        self.assertTrue(any("register description" in e for e in errors(d)))

    def test_field_description_missing_values_block(self):
        d = copy.deepcopy(GOOD)
        f = d["registers"][0]["fields"][0]
        lines = f["description"].split("\n")
        f["description"] = "\n".join(lines[:2] + lines[-2:])
        self.assertTrue(any("blank line" in e for e in errors(d)))

    def test_value_line_needs_hex_key(self):
        d = copy.deepcopy(GOOD)
        f = d["registers"][0]["fields"][0]
        f["description"] = f["description"].replace("0x1 block enabled.", "1 block enabled.")
        self.assertTrue(any("hexadecimal" in e for e in errors(d)))

    def test_value_line_endings(self):
        d = copy.deepcopy(GOOD)
        f = d["registers"][0]["fields"][0]
        f["description"] = f["description"].replace("(reset value);", "(reset value).")
        self.assertTrue(any("must end with ';'" in e for e in errors(d)))

    def test_missing_blank_line_before_unit(self):
        d = copy.deepcopy(GOOD)
        f = d["registers"][0]["fields"][0]
        f["description"] = f["description"].replace("\n\nUnit:", "\nUnit:")
        self.assertTrue(any("blank line" in e for e in errors(d)))

    def test_field_description_wrong_usage_label(self):
        d = copy.deepcopy(GOOD)
        f = d["registers"][0]["fields"][0]
        f["description"] = f["description"].replace("Usage: ", "Use: ")
        self.assertTrue(any("'Usage: '" in e for e in errors(d)))

    def test_module_name(self):
        d = copy.deepcopy(GOOD)
        d["module"] = "m_vlsi_csr"
        self.assertTrue(any("m_vlsit_csr_<function>" in e for e in errors(d)))
        d["module"] = "M_VLSIT_CSR_X"
        self.assertTrue(any("m_vlsit_csr_<function>" in e for e in errors(d)))

    def test_duplicate_module_names(self):
        a, b = copy.deepcopy(GOOD), copy.deepcopy(GOOD)
        self.assertTrue(T.duplicate_modules([("a.json", a), ("b.json", b)]))
        b["module"] = "m_vlsit_csr_other"
        self.assertEqual(T.duplicate_modules([("a.json", a), ("b.json", b)]), [])

    def test_register_name_30_characters(self):
        d = copy.deepcopy(GOOD)
        d["registers"][0]["name"] = "demo_" + "x" * 25
        self.assertTrue(any("fewer than 30" in e for e in errors(d)))
        d["registers"][0]["name"] = "demo_" + "x" * 24
        self.assertFalse(any("fewer than 30" in e for e in errors(d)))

    def test_workbook_format(self):
        if T.load_workbook is None:
            self.skipTest("openpyxl missing")
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp) / "r.json", Path(tmp) / "r.xlsx"
            src.write_text(json.dumps(GOOD), encoding="utf-8")
            class A:
                json, template, auto_reserved, force = str(src), None, True, True
            A.out = str(out)
            self.assertEqual(T.action_fill(A), 0)
            ws = T.load_workbook(out)["CSR"]
            narrow = [ws.column_dimensions[c].width for c in "ABCDEF"]
            self.assertEqual(len(set(narrow)), 1)
            self.assertAlmostEqual(ws.column_dimensions["G"].width, 5 * narrow[0])
            self.assertFalse(ws["A15"].alignment.wrap_text)
            self.assertEqual(ws.max_row, 18)   # no styled blank row below the map: the generator reads every row
            self.assertTrue(ws["G17"].alignment.wrap_text)
            self.assertEqual(ws["G17"].alignment.vertical, "center")
            self.assertEqual(ws["A16"].font.size, 13)
            self.assertEqual(ws["G17"].font.size, 13)
            self.assertEqual(ws["G17"].value if ws["C17"].value == "reserved" else "x", T.RESERVED_DESC if ws["C17"].value == "reserved" else "x")
            colors = {str(ws.cell(r, c).fill.fgColor.rgb)[-6:] for r in range(2, 19) for c in range(1, 8) if ws.cell(r, c).fill.fill_type}
            self.assertLessEqual(colors, {"7030A0", "E6DCF2", "FFFFFF"})

    def test_interrupt_set(self):
        def reg(kind, typ, names):
            return {"name": "demo_irq_" + kind, "offset": {"raw": "0x10", "en": "0x14", "inj": "0x18", "sts": "0x1C"}[kind],
                    "description": "Interrupt %s register. Test register for the check." % kind,
                    "fields": [dict(name=n, bits="[%d]" % i, type=typ, reset="0x0", description="") for i, n in enumerate(names)]}
        d = copy.deepcopy(GOOD)
        ok = ["a", "b"]
        d["registers"] = [reg("raw", "w1c", ok), reg("en", "rw", ok), reg("inj", "rw", ok), reg("sts", "ro", ok)]
        self.assertEqual([e for e in T.interrupt_set_errors(d)], [])
        d["registers"][1] = reg("en", "rw", ["a", "c"])
        self.assertTrue(any("same fields" in e for e in T.interrupt_set_errors(d)))
        d["registers"][1] = reg("en", "rw", ok)
        d["registers"][2] = reg("inj", "rwi", ok)
        self.assertTrue(any("must be type rw" in e for e in T.interrupt_set_errors(d)))

    def test_reserved_description_is_fixed(self):
        d = copy.deepcopy(GOOD)
        d["registers"][0]["fields"][-1]["description"] = "Whatever"
        self.assertTrue(any("fixed (R-039)" in e for e in errors(d)))
        d["registers"][0]["fields"][-1]["description"] = T.RESERVED_DESC
        self.assertEqual(errors(d), [])

    def test_reserved_needs_no_description(self):
        d = copy.deepcopy(GOOD)
        self.assertEqual(errors(d), [])


if __name__ == "__main__":
    unittest.main()
