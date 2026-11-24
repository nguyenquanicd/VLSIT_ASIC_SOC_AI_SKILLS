#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_test_fsm_diagram.py
# Function : unit tests for the FSM diagram generator (R-068 to R-071)
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Run: python vlsit_test_fsm_diagram.py   (standard library only; exit 0 when every test passes)."""
import argparse
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import vlsit_fsm_diagram as CLI
import vlsit_fsm_layout as F  # noqa: E402
import vlsit_fsm_library_symbols as L  # noqa: E402
import vlsit_fsm_to_svg as R  # noqa: E402


class FsmSpecChecks(unittest.TestCase):
    def setUp(self):
        self.spec = copy.deepcopy(F.SAMPLE)

    def test_sample_is_valid(self):
        self.assertEqual(F.validate_spec(self.spec), [])

    def test_state_name_must_follow_the_rtl_rule(self):
        self.spec["state_pattern"] = r"^ENUM_ST_[A-Z0-9_]+$"
        self.spec["states"][0]["name"] = "idle"
        errors = F.validate_spec(self.spec)
        self.assertTrue(any("naming pattern" in e for e in errors))

    def test_duplicate_state_is_rejected(self):
        self.spec["states"].append({"name": "ENUM_ST_IDLE"})
        self.assertTrue(any("duplicate state" in e for e in F.validate_spec(self.spec)))

    def test_unknown_transition_endpoint_is_rejected(self):
        self.spec["transitions"][0]["dst"] = "ENUM_ST_NOPE"
        self.assertTrue(any("unknown destination" in e for e in F.validate_spec(self.spec)))

    def test_unreachable_state_is_rejected(self):
        self.spec["states"].append({"name": "ENUM_ST_LOST"})
        self.assertTrue(any("unreachable" in e for e in F.validate_spec(self.spec)))

    def test_empty_or_duplicate_label_is_rejected(self):
        self.spec["transitions"][0]["label"] = "  "
        self.assertTrue(any("label" in e for e in F.validate_spec(self.spec)))
        self.spec = copy.deepcopy(F.SAMPLE)
        self.spec["transitions"].append(copy.deepcopy(self.spec["transitions"][0]))
        self.assertTrue(any("duplicate transition" in e for e in F.validate_spec(self.spec)))

    def test_linear_approval_needs_a_reason(self):
        self.spec["linear_layout_approved"] = True
        self.assertTrue(any("linear_reason" in e for e in F.validate_spec(self.spec)))

    def test_state_pattern_can_be_overridden(self):
        self.spec["state_pattern"] = r"^ST_[A-Z]+$"
        self.spec["states"] = [
            {"name": "ST_A", "conditional_exit": False, "hold_conditions": []},
            {"name": "ST_B", "conditional_exit": False, "hold_conditions": []},
        ]
        self.spec["initial"] = "ST_A"
        self.spec["transitions"] = [{"src": "ST_A", "dst": "ST_B", "label": "go"}]
        self.spec["condition_aliases"] = []
        self.assertEqual(F.validate_spec(self.spec), [])


class Geometry(unittest.TestCase):
    def setUp(self):
        self.spec = copy.deepcopy(F.SAMPLE)
        self.names, self.succ, self.pred, self.rank = F.build_graph(self.spec)
        self.sizes = {name: F.state_size(name) for name in self.names}

    def test_every_state_name_fits_its_oval(self):
        for name in self.names:
            width, height = self.sizes[name]
            ok, ratio = F.state_fit(name, width, height)
            self.assertTrue(ok, "%s has fill ratio %.2f" % (name, ratio))
            self.assertGreaterEqual(width, len(name) * F.CHAR_W)
            self.assertGreaterEqual(height, F.LINE_H)

    def test_oval_sizes_are_on_the_grid(self):
        for width, height in self.sizes.values():
            self.assertEqual(width % F.GRID, 0)
            self.assertEqual(height % F.GRID, 0)

    def test_flow_ranks_start_at_the_initial_state(self):
        self.assertEqual(self.rank["ENUM_ST_IDLE"], 0)
        self.assertGreater(self.rank["ENUM_ST_WAIT"], 0)
        self.assertGreater(self.rank["ENUM_ST_DONE"], self.rank["ENUM_ST_WAIT"])

    def test_chosen_layout_is_two_dimensional_and_passes_geometry(self):
        layout, positions, _stats, min_gap, _rank_gap, margin = F.choose_layout(
            self.spec, self.names, self.sizes, self.pred, self.succ, self.rank)
        positions = F.normalise_positions(positions, self.sizes, margin)
        report = F.geometry_report(positions, self.sizes, self.spec["transitions"], min_gap, self.spec)
        self.assertFalse(report["linear"], "layout %s is a single row or column" % layout)
        self.assertGreaterEqual(report["distinct_x"], 2)
        self.assertGreaterEqual(report["distinct_y"], 2)
        self.assertTrue(report["fit_ok"])
        self.assertEqual(report["findings"], [])

    def test_crossing_detection(self):
        self.assertTrue(F.segments_cross(((0, 0), (10, 10)), ((0, 10), (10, 0))))
        self.assertFalse(F.segments_cross(((0, 0), (10, 0)), ((0, 1), (10, 1))))

    def test_point_along_a_polyline(self):
        path = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]
        self.assertEqual(F.point_along(path, 0.0), (0.0, 0.0))
        self.assertEqual(F.point_along(path, 0.5), (10.0, 0.0))
        self.assertEqual(F.point_along(path, 1.0), (10.0, 10.0))


class DrawioAndSvg(unittest.TestCase):
    def test_build_writes_valid_library_cells_and_an_svg_with_ellipses(self):
        spec = copy.deepcopy(F.SAMPLE)
        names, succ, pred, rank = F.build_graph(spec)
        sizes = {name: F.state_size(name) for name in names}
        _layout, positions, _stats, min_gap, _rank_gap, margin = F.choose_layout(
            spec, names, sizes, pred, succ, rank)
        positions = F.normalise_positions(positions, sizes, margin)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fsm.drawio"
            F.build_drawio(spec, positions, sizes, min_gap, "FSM_TEST", path.name, path)
            self.assertTrue(path.exists())
            digest, prototypes = L.load_library()
            pages = L.read_pages(path)
            checked = L.validate_pages(pages, digest, prototypes)
            self.assertEqual(checked, 1 + len(names) + len(spec["transitions"]))
            styles = [cell.get("style") or "" for cell in pages[0].find("root").findall("mxCell")]
            self.assertTrue(any("ellipse" in style for style in styles))
            svg = R.render_page(pages[0]).render()
            self.assertIn("<ellipse", svg)
            self.assertIn("ENUM_ST_IDLE", svg)
            self.assertIn("request accepted", svg)

    def make_insert_args(self, spec, stem, function):
        figure = spec.parent / "figures" / (stem + ".svg")
        figure.parent.mkdir(exist_ok=True)
        source = figure.with_suffix(".drawio")
        figure.write_text("<svg/>", encoding="utf-8")
        source.write_text("<mxfile/>", encoding="utf-8")
        source.with_suffix(".json").write_text("{}", encoding="utf-8")
        report = figure.with_name(stem + "_layout_report.txt")
        report.write_text("CROSSINGS: 0\nCONNECTOR CONFLICTS: 0 (minimum clearance 50 px)\nRESULT: PASS\n",
                          encoding="utf-8")
        return argparse.Namespace(spec=str(spec), figure=str(figure), source=str(source),
                                  function=function, caption=None, json_source=None)

    def test_insert_adds_and_replaces_the_fsm_figure(self):
        text = "# Spec\n\n### 10.1 Modes and state transitions\n\n| A | B |\n|---|---|\n| x | y |\n"
        with tempfile.TemporaryDirectory() as folder:
            spec = Path(folder) / "spec.md"
            spec.write_text(text, encoding="utf-8")
            args = self.make_insert_args(spec, "fsm", "bridge")
            self.assertEqual(CLI.action_insert(args), 0)
            result = spec.read_text(encoding="utf-8")
            self.assertIn("<!-- FSM-DIAGRAM:bridge -->", result)
            self.assertIn("![FSM state diagram of bridge](figures/fsm.svg)", result)
            self.assertLess(result.find("<!-- FSM-DIAGRAM:bridge -->"), result.find("| A | B |"))
            args = self.make_insert_args(spec, "fsm_v2", "bridge")
            self.assertEqual(CLI.action_insert(args), 0)
            result = spec.read_text(encoding="utf-8")
            self.assertEqual(result.count("<!-- FSM-DIAGRAM:bridge -->"), 1)
            self.assertIn("figures/fsm_v2.svg", result)
            self.assertNotIn("figures/fsm.svg)", result)

    def test_insert_removes_the_template_placeholder_and_numbers_figures(self):
        text = ("### 10.1 Modes and state transitions\n\n"
                "<!-- FSM-DIAGRAM:<fsm-function> -->\n"
                "![placeholder](figures/placeholder.svg)\n\n"
                "*Figure 10-1. placeholder.*\n"
                "<!-- /FSM-DIAGRAM:<fsm-function> -->\n\n"
                "| A | B |\n|---|---|\n| x | y |\n")
        with tempfile.TemporaryDirectory() as folder:
            spec = Path(folder) / "spec.md"
            spec.write_text(text, encoding="utf-8")
            for function in ("bridge", "aux"):
                args = self.make_insert_args(spec, function, function)
                self.assertEqual(CLI.action_insert(args), 0)
            result = spec.read_text(encoding="utf-8")
            self.assertNotIn("<fsm-function>", result)
            self.assertNotIn("placeholder.svg", result)
            self.assertEqual(result.count("<!-- FSM-DIAGRAM:"), 2)
            self.assertIn("Figure 10-1.", result)
            self.assertIn("Figure 10-2.", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
