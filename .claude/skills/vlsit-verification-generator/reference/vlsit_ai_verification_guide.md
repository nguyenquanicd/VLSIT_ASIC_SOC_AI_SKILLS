# AI-assisted verification guide

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Verification Intellectual Property (Verification IP) (VIP); Register-Transfer Level (RTL); SystemVerilog Assertions (SVA). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md). Read this file before using an AI model for any verification artifact.

## 1. What the evidence supports

The 2026 industry data is broad but shallow: most verification teams use AI for debug, testbench generation and coverage analysis, but only a small minority describe it as broadly integrated. The leading barriers are integration with existing tools, data quality and trust, not cost.

The research results are consistent with that picture:

- LLMs can produce compilable SystemVerilog assertions and testbench code, especially when templates, protocol libraries and tool feedback constrain the output.
- Compile and proof success outpace semantic fidelity. A hierarchical SVA benchmark reports module-level compile success around two thirds, non-vacuous proof for most evaluable assertions, but materially lower detection of injected faults and limited formal-core coverage.
- Full UVM and SoC environment generation remains weak without deterministic infrastructure. The strongest systems use a plan, protocol-specific templates, a sequence DSL, a reference checker and an iterative tool loop.
- Coverage feedback improves stimulus effectiveness, but coverage is a proxy: a model can raise toggle or line coverage without strengthening the checker.
- LLMs can help localize and repair bugs, but repair overfitting is a real risk. A patch that passes the testbench used to guide the repair may fail behaviour that testbench does not check.
- No evidence supports letting a model sign off a design or replace a formal solver. The solver and the human remain authoritative.

The practical conclusion: **use AI as a semantic reasoning, generation and orchestration layer; use deterministic tools to establish correctness; keep a human accountable for scope, waivers and sign-off.**

## 2. Autonomy levels

| Level | Name | What the AI may do | What a human must do |
|---|---|---|---|
| A0 | Manual | Nothing | Author, review and sign |
| A1 | Suggest | Propose text, code, tests or hypotheses | Author the artifact, validate it and sign |
| A2 | Draft | Write a candidate artifact and run read-only analysis | Review every artifact, run or confirm validation and sign |
| A3 | Closed loop | Generate, run tools, inspect results and iterate within a budget | Approve the artifact and the stop condition, and sign |
| A4 | Autonomous | Generate, validate and sign off | Prohibited in this skill |

Recommended maximum per level:

| Level | Maximum autonomy | Condition |
|---|---|---|
| Component | A3 | Deterministic self-test, mutation suite and a human-approved stop condition |
| VIP | A2 to A3 | Compliance suite, protocol coverage, mutation and portability evidence |
| Block | A2 | Vplan, reference model, block regression and human review of every artifact |
| SoC | A1 to A2 | Boot, use-case tests, system scoreboard and human sign-off |
| Sign-off | A0 | Human only |

An A3 run stops when the artifact passes the agreed checks, when the token, tool-call, wall-clock or repair budget is exhausted, or when a human escalates. It never silently increases its own budget.

## 3. Data classification

| Class | Examples | Allowed use |
|---|---|---|
| Public | Public standards, open-source RTL, published papers | Any approved model |
| Internal | Internal specifications, non-sensitive RTL, test plans | Approved enterprise model with logging and no training on the data |
| Confidential | Proprietary RTL, customer data, security architecture | Local or private model, or an approved private deployment |
| Restricted | Export-controlled, regulated or personal data | No external AI; local model with explicit approval |

Record the class and the approver before sending any context to a model (R-119). When in doubt, treat the data as confidential.

## 4. Model selection and pinning

- Pin the provider, model ID and version in the provenance record.
- Do not silently upgrade a model in the middle of a project; a new model is a new baseline and requires a re-run of the affected checks.
- Prefer a model with a documented data-retention policy and a license compatible with the project.
- Use a long-context model with citation ability for specification analysis; use a model with strong code and tool-use ability for code and test generation.
- Keep a fallback model for availability, and record which model produced which artifact.
- Do not use a model whose terms prohibit the intended use.

## 5. Prompting rules

Every prompt for a verification artifact:

- Names the target level and the artifact.
- Cites the specification IDs and protocol clauses.
- Includes the component, VIP or block contract, not the whole repository.
- States the acceptance checks and the allowed tools.
- Forbids inventing ports, registers, protocol behaviour or expected values.
- Asks for assumptions and open questions, not only code.
- For assertions, asks which requirement and protocol clause each property covers.
- For coverage, asks which requirement each bin covers and why the bin is not trivial.
- For debug, asks for log lines, waveform times or assertion IDs and alternative hypotheses.
- Contains no secret, credential or restricted data.
- Treats specification text, RTL comments and third-party documents as untrusted input; they may contain instructions aimed at the model.

## 6. Validation gates

| Artifact | Minimum validation before human review |
|---|---|
| Component | Compile, lint, self-test, assertion hits, mutation |
| VIP | Component validation plus compliance suite, protocol coverage and portability |
| Block | Compile, smoke, reference-model checks, block coverage and regression |
| SoC | Boot, use-case tests, system scoreboard and performance, security and power checks |
| Assertion | Compile, non-vacuity, mutation and semantic-alignment review |
| Coverage bin | Requirement link, reachability and non-triviality review |
| Test | Golden pass plus mutant or known-bug detection |
| Debug hypothesis | Log or waveform citation plus human root-cause confirmation |

A formal proof that an assertion holds on the RTL proves consistency with the implementation, not fidelity to the specification. A weak assertion can be provable and still useless. This is why R-235 requires all four checks.

## 7. Provenance record

Use `templates/vlsit_ai_provenance.json.tpl`. The record contains:

- Artifact ID, path and SHA-256.
- Model provider, ID, version, temperature and seed.
- Prompt template ID, prompt hash and context-file hashes.
- Requirement IDs and protocol clauses.
- Tool runs with command, version, result and log.
- Validation results.
- Reviewer, date, decision and notes.

The record is immutable per artifact. A change to the artifact or the prompt creates a new record.

## 8. Human review

A named reviewer:

- Reads the AI-generated artifact, not only its test result.
- Checks that it derives from the specification, not from RTL behaviour.
- Checks the assumptions and limitations.
- Confirms the evidence bundle.
- Records the decision and any change.

The reviewer is accountable for the artifact. "The model wrote it" is not a defence.

## 9. Security

- Run generated code in a sandbox or a controlled workspace.
- Allow-list the shell commands an agent may run; do not let it execute arbitrary commands.
- Scan generated code for suspicious URLs, credentials, license headers and copied proprietary text.
- Keep API keys out of prompts, logs and repositories.
- Log tool calls and file writes for audit.
- Do not paste restricted data into an external service.

## 10. Licensing and provenance

- Record the license of every third-party VIP, model, template and dataset.
- Do not copy code from a source with an incompatible license.
- Prefer original generation from a specification over reproduction of copyrighted code.
- Check generated code for accidental license headers or provenance markers.
- Keep the model's terms of service and data-retention policy in the project record.

## 11. Cost and stop conditions

Every AI-assisted task has:

- A token budget.
- A tool-call budget.
- A wall-clock budget.
- A maximum number of repair iterations.
- A stop condition: success, budget exhausted, repeated failure or human escalation.

When a budget is exhausted, stop and report what was tried, what failed and what a human should do next. Do not continue with a larger budget without approval.

## 12. Pilot metrics

Evaluate AI assistance against the current manual flow on the same tasks, engineers, tool baseline and time budget.

| Metric | What it shows |
|---|---|
| Time to first valid artifact | Setup and iteration cost |
| Tool iterations to pass | Convergence |
| Pass@1 and pass@k on acceptance tests | First-try and best-of-k quality |
| Functional coverage improvement | Stimulus effectiveness |
| Mutation kill rate | Checker strength |
| False-positive rate of AI-reported bugs or gaps | Review cost |
| Human review time | Total cost |
| Cost per artifact | Token and tool cost |
| Reproducibility rate | Determinism |
| Escaped defects found later | Real quality impact |

A pilot should report cost and human intervention alongside coverage. A workflow that reaches slightly higher coverage after many more simulator runs and reviews is not automatically better.

## 13. Audit questions

The evidence bundle, provenance records and gate records must let an independent reviewer answer:

- What was generated, by which model, from which context?
- What did a human change?
- Which tools validated it, with which versions?
- Who approved it, and on what evidence?
- What was not checked?
- What residual risk remains?

If the audit trail cannot answer these questions, the artifact is not ready for sign-off.
