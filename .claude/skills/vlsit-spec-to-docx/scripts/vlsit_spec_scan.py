#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_spec_scan.py
# Function : map a VLSIT Markdown specification onto the DOCX template sections and list the gaps
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Scan a specification and report what the template needs but the source lacks.

The scan never reads the RTL and never invents content. It produces the gap list
that the assistant must put to the user before content.json is written.

Usage:
    vlsit_spec_scan.py <spec.md> [--folder INPUT_FOLDER] [--out gaps.json]
"""

import argparse
import json
import os
import re
import sys

# Template section slug -> source specification sections (numbers of the VLSIT 22-section spec).
TEMPLATE_MAP = {
    "overview": [1, 4, 18],
    "ip_description": [1],
    "features": [4],
    "limitations": [18, 1],
    "standard_compliance": [2],
    "parameters": [8],
    "parameter_model_and_ownership": [8],
    "user_configurable_parameters_dependencies_and_legal_combinations": [8],
    "parameter_validation_requirements": [8],
    "validated_configuration_examples": [8],
    "block_diagram": [5, 14],
    "ip_block_diagram": [5],
    "block_behavior_and_inter_block_relationships": [5, 14],
    "functions": [10, 3],
    "overview_purpose_use_case_and_scope": [10],
    "function_diagram": [5, 10],
    "function_description": [10],
    "waveform": [10],
    "interfaces": [6],
    "control_and_status_registers": [11],
    "csr_summary": [11],
    "csr_list": [11],
    "csr_behavioral_rules": [11, 12],
    "interrupt_and_error_status_lifecycle": [12, 11],
    "software_programming": [11, 10],
    "programming_model_and_ownership": [11],
    "initialization_flow": [11, 10],
    "configuration_and_start_flow": [11, 10],
    "normal_operation_transfer_flow": [10, 11],
    "interrupt_service_flow": [11, 12],
    "dma_flow_if_supported": [11],
    "error_detection_and_recovery_flow": [12, 11],
    "shutdown_reset_and_power_transition_flow": [7, 11],
    "worked_programming_examples": [11],
    "integration_guideline": [6, 7, 13, 17],
    "address_bus_and_access_integration": [6, 7],
    "clock_reset_power_and_cdc_integration": [7],
    "interrupt_dma_memory_and_pin_integration": [6],
    "integration_hazards_and_bring_up": [7, 17],
    "performance_boundary_and_liveness_requirements": [13],
    "synthesis_design_constraints_sdc": [17],
    "clock_definitions_and_relationships": [17],
    "input_output_delays_and_electrical_constraints": [17],
    "timing_exceptions": [17],
    "synthesis_and_sta_sign_off": [13, 17],
    "design_for_test_dft": [16],
    "test_modes_and_access": [16],
    "scan_memory_test_and_embedded_instruments": [16],
    "dft_verification_and_manufacturing_procedure": [16],
    "physical_design_pd": [17, 13],
    "implementation_views_and_boundary": [17],
    "floorplan_pins_macros_and_power": [17],
    "routing_reliability_and_sign_off": [17],
    "ppa_results_by_configuration": [13],
    "verification_and_validation_dv": [15, 19, 14],
    "verification_scope_and_requirements_traceability": [15, 19],
    "testbench_architecture_and_dependencies": [15, 14],
    "test_scenarios_assertions_and_coverage": [15],
    "regression_results_and_sign_off": [15],
    "power_management_and_power_intent": [7, 13],
    "power_domain_state_and_ownership_model": [7, 13],
    "power_transition_isolation_and_retention": [7, 13],
    "power_intent_artifacts_and_verification": [7, 13],
    "security_and_robustness": [18],
    "security_boundary_and_access_control": [18],
    "integrity_ras_and_error_containment": [18],
    "security_and_robustness_verification": [18],
    "revision_history": [20],
    "acronyms_and_definitions": [21],
    "references": [22],
}

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".emf")
WAVE_EXT = (".json", ".svg", ".vcd")


def read_text(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read()


def parse_headings(text):
    """Return [(number, title, body_text)] for every level-2 section of the spec."""
    lines = text.splitlines()
    sections, current, buffer = [], None, []
    for line in lines:
        match = re.match(r"^##\s+(\d+)\.\s+(.*)$", line)
        if match:
            if current is not None:
                sections.append((current[0], current[1], "\n".join(buffer)))
            current = (int(match.group(1)), match.group(2).strip())
            buffer = []
            continue
        if re.match(r"^##\s+Document map", line) and current is None:
            current = (0, "Document map")
            buffer = []
            continue
        if current is not None:
            buffer.append(line)
    if current is not None:
        sections.append((current[0], current[1], "\n".join(buffer)))
    return sections


def looks_like_wavejson(path):
    """A WaveJSON source holds a top-level signal array; other JSON files are not waveforms."""
    try:
        with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
            head = handle.read(2048)
    except OSError:
        return False
    return '"signal"' in head.replace(" ", "")


def list_assets(folder):
    """Return the figure and waveform assets found under the input folder."""
    figures, waveforms = [], []
    if not folder or not os.path.isdir(folder):
        return figures, waveforms
    for root, _dirs, files in os.walk(folder):
        for name in sorted(files):
            lower = name.lower()
            full = os.path.join(root, name)
            rel = os.path.relpath(full, folder)
            if "waveform" in root.lower() and lower.endswith(WAVE_EXT):
                waveforms.append(rel)
            elif lower.endswith(".json") and looks_like_wavejson(full):
                waveforms.append(rel)
            elif lower.endswith(IMAGE_EXT):
                figures.append(rel)
    return figures, waveforms


def main():
    parser = argparse.ArgumentParser(description="Map a specification onto the template and list gaps.")
    parser.add_argument("spec", help="the source specification Markdown")
    parser.add_argument("--folder", help="the input folder that holds the assets")
    parser.add_argument("--out", default="gaps.json", help="gap report (default gaps.json)")
    args = parser.parse_args()

    text = read_text(args.spec)
    sections = parse_headings(text)
    by_number = {number: body for number, _title, body in sections}
    titles = {number: title for number, title, _body in sections}

    requirements = sorted(set(re.findall(r"\bREQ-[A-Z0-9]+-\d+\b", text)))
    figures, waveforms = list_assets(args.folder)

    resolved, gaps = [], []
    for slug, sources in TEMPLATE_MAP.items():
        bodies = [by_number.get(number, "") for number in sources]
        chars = sum(len(body) for body in bodies)
        has_table = any("|---" in body for body in bodies)
        found = chars > 0
        resolved.append({"slug": slug, "sources": sources, "found": found,
                         "chars": chars, "has_table": has_table})
        if not found:
            gaps.append({"kind": "no_source", "slug": slug,
                         "question": "Template section '%s' has no source section %s. Does the IP have this content, and where is it?"
                                     % (slug, sources)})

    mandatory = [
        ("sdc_numeric", "synthesis_design_constraints_sdc",
         r"\b\d+(\.\d+)?\s*(ns|MHz|GHz|ps)\b",
         "Section 9 SDC needs a clock period and I/O delays; the source states none. What are the target period and the boundary delays?"),
        ("software_flow", "software_programming",
         r"(?i)software",
         "Section 7 Software Programming has no software sequence in the source. Is there a driver flow, or is the IP software-invisible?"),
        ("worked_example", "overview_purpose_use_case_and_scope",
         r"(?i)worked example|for example|example:",
         "Section 4 asks for a worked example of each function; none was found. Can you provide concrete values?"),
        ("function_cycle_detail", "function_description",
         r"(?i)cycle",
         "Section 4 function descriptions need cycle-level behaviour; the source has no cycle description. Can you provide it or the RTL?"),
    ]
    for key, slug, pattern, question in mandatory:
        body = " ".join(by_number.get(number, "") for number in TEMPLATE_MAP.get(slug, []))
        if not re.search(pattern, body):
            gaps.append({"kind": "missing_element", "slug": slug, "element": key, "question": question})

    if not figures:
        gaps.append({"kind": "no_figure", "slug": "ip_block_diagram",
                     "question": "No figure asset was found in the input folder. Where is the block diagram, and which waveforms may be inserted?"})
    if not waveforms:
        gaps.append({"kind": "no_waveform_asset", "slug": "waveform",
                     "question": "No waveform asset was found. Which waveforms are approved for the function sections?"})

    report = {
        "source": args.spec,
        "folder": args.folder,
        "title": os.path.splitext(os.path.basename(args.spec))[0],
        "sections": [{"number": number, "title": titles[number], "chars": len(body)}
                     for number, body in by_number.items()],
        "requirements": {"count": len(requirements), "sample": requirements[:8]},
        "assets": {"figures": figures[:40], "waveforms": waveforms[:40]},
        "template_sections": resolved,
        "gaps": gaps,
        "summary": {
            "source_sections": len(sections),
            "requirements": len(requirements),
            "figures": len(figures),
            "waveforms": len(waveforms),
            "gaps": len(gaps),
        },
    }

    with open(args.out, "w", encoding="utf-8-sig") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print("SOURCE   %s (%d sections, %d requirements)"
          % (os.path.basename(args.spec), len(sections), len(requirements)))
    print("ASSETS   figures=%d waveforms=%d" % (len(figures), len(waveforms)))
    if gaps:
        print("GAPS     %d" % len(gaps))
        for gap in gaps[:20]:
            print("  [%s] %s" % (gap["kind"], gap["question"][:120]))
    else:
        print("GAPS     0")
    print("SCAN gaps=%d figures=%d waveforms=%d -> %s"
          % (len(gaps), len(figures), len(waveforms), args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
