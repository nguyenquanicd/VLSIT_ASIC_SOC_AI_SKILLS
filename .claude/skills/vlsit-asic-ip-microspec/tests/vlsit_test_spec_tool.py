#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_test_spec_tool.py
# Function : unit tests for the content checks of vlsit_spec_tool.py check (R-005, R-013, R-015, R-031)
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Run: python vlsit_test_spec_tool.py   (standard library only; exit 0 when every test passes)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import vlsit_spec_tool as T  # noqa: E402


class ContentChecks(unittest.TestCase):
    def test_english_flags_vietnamese(self):
        e = []
        T.check_english("a line\nXin chào, đây là tiếng Việt\n```\nkhông tính trong code\n```\n", e)
        self.assertEqual(len(e), 1)
        self.assertIn("[2]", e[0])

    def test_english_passes_english(self):
        e = []
        T.check_english("Only English text here.\n", e)
        self.assertEqual(e, [])

    def test_empty_subsection(self):
        e = []
        T.check_empty_subsections("## 5. Architecture\n### 5.3 Data path\n\n### 5.4 Control\nText.\n", e)
        self.assertEqual(len(e), 1)
        self.assertIn("5.3", e[0])

    def test_template_text_left(self):
        line = next(l.strip() for l in T.strip_code(T.read(T.TEMPLATE)).split("## 4.")[1].splitlines()
                    if len(l.strip()) > 50 and l.strip()[0] not in "|#<!>" and "<" not in l)
        e = []
        T.check_template_text("## 4. Features\n%s\n## 5. Architecture\nOwn text.\n" % line, e)
        self.assertEqual(len(e), 1)

    def test_template_text_not_flagged_in_section_14(self):
        e = []
        T.check_template_text("## 14. RTL implementation contract\n"
                              "The VLSIT RTL Design Rules v2 in VLSIT_RTL_Design_Rule.md (same folder as this template) i\n", e)
        self.assertEqual(e, [])

    def test_verification_ids(self):
        sec = {15: "| TEST-001 | REQ-FUNC-001 | a | b |\n| SVA-001 / COV-001 | x |\n",
               19: "| REQ-FUNC-001 | a | TEST-001 | b |\n| REQ-FUNC-002 | a | TEST-009 | b |\n"
                   "| REQ-FUNC-003 | a | - | b |\n| REQ-FUNC-004 | a | Inspection | b |\n"}
        e = []
        T.check_verification_ids(sec, e)
        self.assertEqual(len(e), 2)
        self.assertTrue(any("TEST-009" in x for x in e))
        self.assertTrue(any("REQ-FUNC-003" in x for x in e))

    def test_verification_id_of_another_ip_is_ignored(self):
        e = []
        T.check_verification_ids({15: "| TEST-001 | x |\n", 19: "", 12: "see AXI-SVA-02 of the bridge"}, e)
        self.assertEqual(e, [])

    def test_csr_sections_need_workbook(self):
        text = "### 11.1 CSR source\nx\n### 11.3 Connection\n\n### 11.4 APB\ny\n"
        with tempfile.TemporaryDirectory() as d:
            e = []
            T.check_csr_sections(text, d, e)
            self.assertEqual(e, [])
            (Path(d) / "IP_CSR.xlsx").write_bytes(b"")
            T.check_csr_sections(text, d, e)
            self.assertEqual(len(e), 1)
            self.assertIn("11.3", e[0])


if __name__ == "__main__":
    unittest.main()
