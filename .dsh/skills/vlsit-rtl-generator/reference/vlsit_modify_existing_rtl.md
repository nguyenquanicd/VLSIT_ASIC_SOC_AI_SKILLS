# Changing existing RTL

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-008, R-009, R-002). Read this when the request is to fix, extend or restyle RTL that already exists.

## Use the sibling skill when it is present

If the skill `vlsit-rtl-spec-change-implementer` exists in the same skills folder, follow its procedure for the plan and the approval gate, and use its snapshot and change-percentage helpers. It covers: read-only baseline, a review document with a minimal-change plan, a gate (APPROVE, REVISE or STOP) for a named plan version, minimal approved edits, then validation and the code-change percentage. This skill adds the VLSIT rule check, lint and the output rules on top.

Without that skill, use the procedure below.

## Procedure

1. **Inputs.** Ask for the RTL folder (required), the old specification (optional), and the new request or specification. Ask once for everything that is missing.
2. **Baseline, read only.** Run `vlsit_rtl_check.py check <rtl folder>` and `vlsit_lint_rtl.py` on the original so that findings that already existed are known and are not blamed on the change. Copy the original files to a snapshot folder outside the RTL tree before any edit.
3. **Understand.** List modules, ports, clocks, resets and the signals touched by the request. When something about the request or the existing behavior is unclear, ask with the question format of [vlsit_question_format.md](vlsit_question_format.md); do not guess.
4. **Plan.** Write a plan with: files to change, exact edits (before and after in a few lines), the reason for each, the behavior that changes and the behavior that must stay the same, and the checks that will run. Keep it minimal: change only what the request needs.
5. **Gate.** Ask the designer to approve the named plan. Edit nothing until the answer is yes. A changed plan needs a new approval.
6. **Implement.** Write the changed files into the output folder (R-009), keeping unchanged files out of the folder unless they are needed for the filelist. Apply only the approved edits. Existing code that violates the rule file stays as it is unless the plan said to fix it; report it instead.
7. **Verify.** Run the rule check and lint on the changed set, compare the findings with the baseline, and report new findings and fixed findings separately.
8. **Report.** List changed files, the diff size, rule IDs failed, justified and clean, and what was not run.

## Restyling to the rule file

When the request is only "bring this RTL into line with the rules", the plan lists the rule IDs to fix and the files they touch. Renames change interfaces: list every renamed port and every instance that connects to it, and get approval for the renames separately.
