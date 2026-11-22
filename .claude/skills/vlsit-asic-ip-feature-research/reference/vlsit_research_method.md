# Research and prevalence method

## Freeze the protocol

Before extraction, write the question, scope, intended applications, product generation, date range, languages, databases/catalogs, exact search strings, inclusion/exclusion criteria and source categories. With the user-first mode (R-026) freeze the inclusion and exclusion criteria before assessing the user documents, then record the gap (missing product families, papers and thin topics) and freeze the search queries only when the supplementary search is approved; with the no-search mode write that no search was performed. Keep product documentation, scholarly papers, standards, patents, application notes and market claims in separate evidence classes. Record each candidate and why it was included or excluded.

## Build the feature taxonomy

Normalize synonymous feature names into a taxonomy while preserving source wording. Give each feature a concise definition and distinguish required behavior, optional modes, performance claims, implementation choices, interfaces and software affordances. Never combine features that have different user outcomes or integration costs just to increase a count.

## Extract evidence

For every feature-source pair capture:

- source identifier and exact page, section, table, figure or patent claim;
- source's own terminology and the normalized feature name;
- explicit presence, explicit absence, not reported, or ambiguous;
- feature behavior and operating conditions;
- product family or paper identifier;
- evidence quality and independence;
- counterevidence, contradiction, assumption and confidence.

Only explicit source evidence supports a presence count. Treat silence as not reported, not absent. A vague feature mention that cannot be mapped to the defined behavior is ambiguous and excluded from the numerator.

## Occurrence rates

Report the two rates independently and label them **documented product-corpus occurrence** and **paper-corpus research occurrence**.

For each feature:

`product occurrence = distinct assessable product families explicitly documenting the feature / distinct product families with documents sufficient to assess it`

`paper occurrence = distinct eligible full-text papers substantively discussing the feature / distinct eligible full-text papers analyzed`

Show the raw values (`n/N`) and percentage, the number not reported or ambiguous, exclusions, selected product and publication generations, and the search date. A study may use `not enough evidence` instead of a misleading percentage when denominators are too small or source quality is poor.

These rates describe only the selected corpus. They are not global market share, installed-base penetration, sales, market demand or probability of implementation. Separate evidence of commercial availability from scholarly attention and from the researcher's assessment of application usefulness. Do not average the two rates.

## Synthesis and disagreement

Compare sources feature by feature. Prefer direct primary evidence for product behavior, but do not treat vendor claims as independent validation. For conflicting claims, show both positions, revisions and conditions; explain whether the difference is caused by configuration, generation, terminology or a true inconsistency. Do not silently select the preferred result.

State confidence with defined reasons: strength and number of independent sources, directness of evidence, consistency, currency and unresolved gaps. Confidence is not a statistical confidence interval unless a valid sampling model was defined and justified.

## System and application linkage

Trace the feature from user need to block/function, protocol/data path, system dependencies, software contract and observable outcome. For an external connection, distinguish logical protocol from electrical interface and physical pad. State documented line coding, voltage, signaling, clocking, reset, connector/package, external peer and board requirements where available; mark missing specifications as questions. Avoid assuming an interface-name match proves electrical compatibility.

Evaluate relevant power, performance and area, bandwidth, latency, resource utilization, memory, clock/reset, security, safety, testability, driver/application programming interface, configuration, backward compatibility, process, package and pin-count effects. Use measured evidence when available; label estimates and assumptions.
