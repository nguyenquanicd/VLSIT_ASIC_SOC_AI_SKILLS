# Validation and report contract

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Clock-Domain Crossing (CDC); Reset-Domain Crossing (RDC). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

## Rule evidence matrix

Read the complete bundled rule before using its matrix. scripts/vlsit_create_rule_matrix.py creates rule_compliance.json from that exact document and records SHA-256. The helper includes numbered rules/prohibitions and supporting table, list, and naming instructions. Auxiliary AUX identifiers belong to the helper, not the original rule.

The matrix is a starting inventory, not a compliance checker. Expand compound requirements into subchecks using the full original text, including nested bullets. Verify all sections 0–12, the naming and abbreviation tables, declaration tables, Section 8.1 file ordering, protocol table, P1–P29, and every tapeout-readiness item. Newly changed rule versions require renewed coverage review, not blind trust in the extractor.

For each entry and subcheck, record module/configuration scope, source evidence, target evidence, actual tool/log evidence when relevant, findings in scientific English, rationale, and reviewer where required by the rule. Global PASS requires coverage of every generated design module/configuration; a check on one module cannot stand for the entire tree.

Matrix schema version 2 uses notes at document level and evidence and reason for each entry. Write all assessment text in scientific English. Expand subchecks with their own scope, status, and evidence when a rule contains multiple requirements.

Use the following status values:

| Status | Meaning |
|---|---|
| PASS | Demonstrated compliant in the recorded scope. |
| FAIL | Violation or demonstrated mismatch. |
| NOT_RUN | Check not executed or evidence unavailable. |
| UNSUPPORTED | Selected tool cannot perform the check. |
| N/A | Requirement genuinely inapplicable with a written reason. |

Do not remove failed rows, invent waivers for MUST/MUST NOT, or mark missing CDC/DFT/STA analysis as N/A just because a tool is absent. A SHOULD deviation must satisfy the exception policy of the original rule and be recorded in the module header or review notes.

## Validation procedure

1. **Baseline:** Analyze/elaborate VHDL with its actual standard, library bindings, selected architecture, generic values, and source order. Preserve source hashes and baseline failures. Fixing baseline code is outside translation unless explicitly approved.
2. **Target elaboration and lint:** Elaborate the emitted SV independently for the same approved configurations. Check widths, implicit nets, drivers, completeness/latches, unsigned arithmetic, prohibited constructs, names, headers/comments, and source-set separation. Inspect compiler semantics and AST-based lint where available; a text scan is only supplementary.
3. **Differential simulation:** Apply identical recorded stimuli to independently compiled source and target, through an explicit port/configuration adapter. Compare at agreed stable sampling points without hiding a cycle of mismatch. Cover reset assertion/release, enables, handshakes, backpressure, arithmetic corners, register side effects, interrupts, memory collisions, and generic boundaries relevant to the design. Preserve seeds, input vectors, output traces, and failures.
4. **Formal equivalence:** Use a frontend/flow supporting the actual VHDL and SV constructs. Record state/name/port mappings, assumptions, initial-state/reset model, black-box contracts, configurations, proof method, depth, and partition results. A bounded check is not an unbounded proof. A proof of a converted intermediate against the candidate does not independently verify that intermediate's translation semantics.
5. **Synthesis and inference:** Synthesize candidate SV with the selected frontend/target, exact version, top, filelist, options, generics/parameters, constraints, and libraries. Inspect inferred registers/memories, reset mapping, combinational loops/latches, unresolved cells, and unexpected optimization. Record resource differences without treating equal cell counts as proof. Generic synthesis without a target library does not demonstrate target-library reset mapping or ASIC tapeout readiness.
6. **Integration requirements:** Check applicable CDC/RDC, DFT/test control, clock gating wrappers, memory wrappers, constraints, power intent, and RTL-to-netlist equivalence planning per the full rule. VHDL-to-SV equivalence and SV-to-netlist equivalence are different checks. Preserve actual constraints/logs; do not claim timing sign-off from synthesis.

Tool commands must be derived from the discovered tools and their installed versions. On Windows, record whether tools run natively, through an existing WSL environment, or in another user-approved environment. Do not assume a particular simulator, frontend, or commercial license exists. A missing required tool blocks that validation result while other approved work can continue.

Useful upstream references

- [GHDL synthesis](https://ghdl.github.io/ghdl/using/Synthesis.html): Verilog netlist export and VHDL frontend capabilities; support must be checked for the installed build.
- [YosysHQ EQY](https://yosyshq.readthedocs.io/projects/eqy/en/latest/): equivalence checking after suitable frontend elaboration; proof scope and X semantics matter.

## Plan and gates

conversion_plan.md contains substantive findings in scientific English:

- Input/source inventory and hashes; selected units/configurations and completeness denominator.
- Behavioral baseline, interface/register/latency contracts, dependency decisions, and equivalence scope.
- Source-to-target structure/type/name/generic mappings and justified source evidence.
- Rule conflicts with exact IDs or source sections, unresolved questions, proposed compliant resolutions, and changes classified as translation or redesign.
- Up to three meaningful alternative approaches when warranted; compare semantic preservation, compliance, integration effort, tool support, and validation strength.
- Output location, tool environment, validation commands/configurations, required versus optional checks, unavailable tools, approval version/status.

Gate 1 prompt:

- Do you approve conversion plan version N, its source/configuration scope, mapping decisions, explicitly listed redesigns, output location, and validation plan? Reply APPROVE, REVISE, or STOP.

Formal verification is attempted when available and suitable. The plan must say whether a formal PASS is required for acceptance. If that choice is unresolved, keep formal acceptance pending; source conversion and other approved checks may proceed with explicit limitations. Never claim complete equivalence merely because formal was optional.

## Deliverable content

Use relative paths inside reusable manifests/filelists and resolve user-provided roots at runtime. Record tool names, versions, commands, configurations, and reproducible environment details. Preserve raw validation logs in the run output; reports can display portable paths while retaining enough evidence to reproduce the run.

conversion_manifest.json records source hashes, rule hash, selected standards/tools, file/unit classifications, architectures, dependencies, source-to-target module/port/bit/state/generic mappings, supported configurations, emitted file hashes, and approved behavioral differences.

conversion_report.md records in scientific English:

1. What was converted, absorbed, excluded, blocked, or redesigned, with reasons.
2. Conversion completeness as converted design units / all in-scope design units, raw counts, and supported/tested configuration counts. Treat package absorption separately from module conversion; never inflate the numerator with copied dependencies or silently shrink the denominator.
3. Rule coverage with per-rule/subcheck results, semantic rationale, and links to RTL/log evidence.
4. Actual checks/configurations and outcomes, including failures, missing tools, and counterexamples.
5. Separate equivalence evidence, synthesis evidence, integration/tapeout readiness, and remaining risks.
6. Whether behavior is unchanged in the recorded scope or includes separately approved redesign.
7. Gate 1 plan/version approval and Gate 2 acceptance status.

Acceptance requires explicit Gate 2 acceptance plus passing required planned checks and applicable mandatory rules. Otherwise deliver as GENERATED_UNVERIFIED, DELIVERED_WITH_LIMITS, or BLOCKED, with separate per-check statuses. Do not mark the entire flow PASS when any required result remains missing. A verified subset may be described only as that subset.
