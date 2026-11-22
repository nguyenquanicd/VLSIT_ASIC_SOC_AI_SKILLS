# ASIC IP feature research report template

Use this outline for the English report. Remove sections that do not apply only after stating why. Every material conclusion must link to the source register and a precise evidence locator.

## 1. Executive summary

State target, question, status (`READY` or `INCOMPLETE`), top findings, confidence and limits. Do not label a corpus rate as market share.

## 2. Scope and method

Record the source mode (user documents first, search for everything, or user documents only), the number of documents supplied by the user and the number found by search, target and application context, product generation, search date (or that no search was performed), exact queries, catalogs/databases, inclusion and exclusion criteria, languages, date limits and deduplication method.

## 3. Evidence inventory and quality

Summarize the number of qualifying product-family documents and peer-reviewed full-text papers, with exclusions and shortfalls. Link every entry to `vlsit_source_manifest.csv`.

## 4. Feature/function taxonomy

| Feature ID | Normalized feature | Source terminology | Function/user outcome | Evidence status | Confidence |
|---|---|---|---|---|---|

## 5. Corpus occurrence, not market share

| Feature | Product families with explicit evidence / assessable families | Product corpus rate | Papers discussing / eligible papers | Paper corpus rate | Not reported/ambiguous | Limits |
|---|---:|---:|---:|---:|---:|---|

Include raw `n/N`, denominator definition, excluded records and sampling limits. Keep commercial availability, scholarly attention and application value separate.

## 6. System architecture and microarchitecture

Describe system block responsibilities and microarchitectural organization such as controller/datapath roles, pipeline stages, buffering, arbitration, ordering, state machines, transaction sequences, error handling, configuration and software flow when documented. Relate each to application needs and cite the source. Include a draw.io block diagram and, where useful, a state-machine or timing/waveform figure. Distinguish documented connections from inferred or unknown ones.

## 7. Integration and physical interface requirements

| Feature/interface | Local block | External peer | Protocol/logical contract | Pad/physical-layer-interface/electrical evidence | Clock/reset/power | Package/board/process | Open integration questions |
|---|---|---|---|---|---|---|---|

Do not infer electrical compatibility from a logical bus name. State unknown pad, voltage, termination, timing or package requirements plainly.

## 8. Configuration, registers and software usability

Describe configuration modes, status/error reporting, driver/application programming interface needs, initialization sequences, discoverability, diagnostics, backwards compatibility and user-visible failure handling where supported by evidence.

## 9. Licensing, patent and dependency review

Separate document rights, implementation license, standard/specification terms, patent evidence and third-party dependencies. Include jurisdiction, source, lookup date, status, uncertainty and legal-review limitation.

## 10. Opportunities for new or improved features

| Proposal | Unmet need and evidence | User/software benefit | Architecture and integration change | Power, performance and area (PPA), security and compatibility risks | Licensing uncertainty | Validation experiment | Confidence |
|---|---|---|---|---|---|---|---|

Treat novelty as a research hypothesis, not an originality or patent-clearance finding.

## 11. Trade-offs and recommendation

Compare no more than three strong options when multiple designs are viable. Explain benefit, cost, evidence, risk, assumptions and decision criteria.

## 12. Risks, gaps and next research steps

List unresolved source conflicts, missing product evidence, inaccessible papers, unreviewed jurisdictions, requirements needing vendor confirmation and experiments needed to validate recommendations.

## 13. Abbreviations and references

Expand terms at first use and include a scoped glossary. Provide citations with stable links and precise locators. Do not embed restricted source documents into the report.

## Figures

Use draw.io for editable architecture/block diagrams. Use waveform or finite-state-machine figures only when they clarify a sourced operational sequence or state relationship. Add a short caption, source citation and legend for certainty/inference. Prefer readable labels and avoid implying undocumented signal-level detail.
