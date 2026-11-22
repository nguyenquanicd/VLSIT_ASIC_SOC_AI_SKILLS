# Rules

These rules are mandatory. If this file, `SKILL.md` and a reference file differ, this file wins; `SKILL.md` wins over reference guidance. Each rule is one checkable requirement with a permanent identifier, a Why line and a Check line. No rule may contradict or duplicate another.

## Research scope and evidence

### R-001 Define the research scope
MUST identify the target intellectual-property block or system-on-chip, feature/function question, application context and product scope before drawing conclusions; ask about missing material facts.
- Why: feature meaning and integration requirements depend on the target and its application.
- Check: manual - the report states the target, question, scope, assumptions and unresolved inputs.

### R-002 Minimum product documents
MUST base a complete product-feature study on ten or more locally retained manufacturer datasheets or databooks, each mapped to a different product-family key.
- Why: repeated revisions or documents for one product family do not provide ten independent product examples.
- Check: `scripts/vlsit_asic_ip_feature_research.py check <directory>` confirms ten or more distinct datasheet family keys with files and valid hashes; manual - inspect source type, relevance and family identity.

### R-003 Minimum scholarly papers
MUST include ten or more relevant, full-text, peer-reviewed scientific papers as the scholarly evidence corpus for a complete study.
- Why: abstracts and duplicated conference/journal versions do not support detailed feature analysis or the requested paper evidence threshold.
- Check: `scripts/vlsit_asic_ip_feature_research.py check <directory>` confirms ten or more unique full-text peer-reviewed paper records with files and valid hashes; manual - verify venue, review status, relevance and duplicate grouping.

### R-004 Honest incomplete status
MUST label a study `INCOMPLETE` whenever either source threshold or any required evidence gate is unmet; a complete status requires both thresholds and all evidence gates.
- Why: a partial search must not be mistaken for a complete evidence base.
- Check: script status and report counts agree; manual - compare claims with the qualifying manifest rows.

### R-005 Search provenance
MUST record search date, exact queries, search/catalog sources, date and language limits, inclusion/exclusion criteria and source access basis, or the statement that no search was performed because the corpus is user-supplied (R-026).
- Why: another researcher needs to understand selection bias and reproduce or extend the search.
- Check: manual - all protocol fields appear in the report or its linked research log.

### R-006 Source diversity and deduplication
MUST deduplicate revisions, mirrors, translations and preprint/publication versions so each product family or paper contributes at most once to its corresponding rate.
- Why: copies of the same evidence inflate counts and create false prevalence.
- Check: script checks family keys, identifiers and file hashes; manual - review duplicate groups and source-family assignments.

### R-007 Source quality
MUST qualify each counted source using documented authority and relevance criteria rather than citation count or search rank alone.
- Why: popularity in a search engine does not establish technical quality or peer review.
- Check: manual - the source register records publisher/venue, date/revision, review status where applicable, relevance and qualification rationale.

### R-008 Claim traceability
MUST link every material technical, adoption, license or patent claim to a specific source and page, section, figure, claim number or dated database record.
- Why: traceable claims can be checked when sources disagree or change.
- Check: manual - sample each report section and confirm every material claim has a resolvable citation locator.

### R-009 Separate fact, inference and unknown
MUST distinguish documented facts, reasoned inferences, assumptions, disputed claims and unknowns, including significant contradictory evidence.
- Why: a plausible architectural interpretation is not the same as a manufacturer statement.
- Check: manual - review claims, confidence labels and counterevidence for each major feature.

## Feature, prevalence and system analysis

### R-010 Separate prevalence rates
MUST calculate product-document occurrence and scholarly-paper occurrence separately, with raw numerators, denominators, exclusions, missing information and selection limits.
- Why: product documentation and research attention measure different populations and cannot be meaningfully blended into one percentage.
- Check: manual - reproduce each reported numerator/denominator from unique qualifying source records and confirm the rate is labeled as corpus occurrence, not market share.

### R-011 Assess only what sources can reveal
MUST exclude unassessable product families from a feature denominator and report their omitted count when documents do not provide enough evidence to determine feature presence.
- Why: missing documentation is not evidence that a feature is absent.
- Check: manual - denominator and not-assessable counts reconcile with the manifest and extraction table.

### R-012 Explain function and application
MUST explain each important feature's function, user/system need, operating context, relevant block/microarchitecture organization and relationships to neighboring blocks, with evidence for each relationship.
- Why: a list of feature names does not explain architecture or application value.
- Check: manual - each prioritized feature has function, context, relationship and citations.

### R-013 Analyze external I/O paths
MUST identify documented off-chip pad or physical-interface requirements, external peers, relevant electrical/protocol assumptions and integration dependencies; mark undocumented properties unknown.
- Why: a logical interface name does not establish a pad cell, voltage, signaling mode or compatible external device.
- Check: manual - every off-chip interface row is sourced or explicitly marked unknown with follow-up requirements.

### R-014 Evaluate integration trade-offs
MUST assess relevant power, performance and area, clock/reset, bandwidth/latency, memory, security, safety, test, software, backward compatibility, package and process dependencies, marking irrelevant items with a reason.
- Why: an isolated feature may impose substantial SoC-level cost or constraints.
- Check: manual - the integration matrix covers each applicable category and cites evidence or states an open question.

### R-015 Support improvement proposals
MUST connect every proposed new or enhanced feature to an evidenced unresolved need, expected benefit, alternatives, costs, compatibility/security risks, uncertainty and a validation experiment.
- Why: a feature idea without a need and trade-off is not an actionable design recommendation.
- Check: manual - each proposal contains all required fields and supporting citations.

## Rights, visualizations and deliverables

### R-016 Respect access and copyright
MUST use only directly accessible open sources or files the user is authorized to provide, with batch approval and no bypass of authentication, paywalls or technical access restrictions.
- Why: research access does not grant permission to evade controls or redistribute protected material.
- Check: manual - approval precedes downloads and every retained file has a recorded access basis and source notice.

### R-017 Limit legal conclusions
MUST distinguish document copyright, implementation license, standards terms, patent evidence and third-party dependencies, and avoid legal-clearance claims without qualified legal review.
- Why: a source's publication or an unsuccessful search does not establish implementation rights or patent clearance.
- Check: manual - rights findings identify evidence, jurisdiction, search date and uncertainty, with a legal-advice limitation.

### R-018 Do not redistribute restricted materials
MUST keep downloaded source documents in the user's designated research workspace and restrict redistribution to cases explicitly permitted by applicable rights.
- Why: internal research retention and public redistribution are different uses.
- Check: manual - deliverable links remain within the chosen workspace and no restricted source is embedded in a public report.

### R-019 Evidence-grounded visuals
MUST create draw.io diagrams or other figures only when useful to explain architecture, function, interfaces, timing or states, with supported, inferred and unknown relationships labeled distinctly.
- Why: diagrams should clarify the evidence without implying undocumented connectivity.
- Check: manual - inspect each figure against its source citations and the report's uncertainty labels.

### R-020 English research artifacts
MUST write the research report, diagrams and skill materials in English, while keeping each skill README and the repository-wide README bilingual in English and Vietnamese.
- Why: a consistent technical artifact supports reuse while bilingual README files serve this repository's users.
- Check: manual - inspect deliverable and README language.

### R-021 Define abbreviations
MUST expand and explain each domain abbreviation at first use in prose, preserve exact identifiers and provide a local glossary for recurring or ambiguous terms.
- Why: an acronym can have several meanings across semiconductor, software and networking contexts.
- Check: manual - inspect first occurrence, glossary and identifiers for correct contextual meaning.

### R-022 Preserve output and provenance
MUST write only to the user-supplied research directory, record source uniform resource locators (URLs) and Secure Hash Algorithm 256-bit (SHA-256) digests, and preserve existing outputs unless the user explicitly approves replacement.
- Why: provenance enables integrity checks and user-owned research files must remain safe.
- Check: script confirms hashes and refuses to replace files; manual - verify paths, links and prior-file handling.

### R-023 Date patent and standards findings
MUST state the lookup date, jurisdiction and database/standards source for time-sensitive patent and standards findings, and identify any unchecked jurisdictions or revisions.
- Why: legal status and standards editions can change over time and vary by region.
- Check: manual - each time-sensitive finding includes its date, coverage and source.

### R-024 Mechanical evidence validation
MUST run the bundle checker after registering sources and distinguish its mechanical checks from expert judgments about quality, relevance, correctness and rights.
- Why: a valid manifest and checksum do not prove that research conclusions are true.
- Check: recorded command output and a manual audit of claims, source quality, rights, calculations and diagrams.

### R-025 Report limitations and confidence
MUST report search blind spots, source conflicts, confidence, missing evidence and the limited generalizability of the corpus.
- Why: a useful study makes its uncertainty visible rather than turning it into false precision.
- Check: manual - the report includes an evidence-limits section and confidence is supported by stated criteria.

## Source acquisition mode

### R-026 User documents first
MUST ask the user, with options, explanations and an open choice, how the sources are obtained (the user supplies reference documents first, the skill searches for everything, or the user's documents only with no search),; user-supplied documents are then registered and qualified before any search, a supplementary search is proposed only for the measured shortfall, and it runs only after the user approves it.
- Why: the user often holds the documents that matter for the question, and a search that ignores them repeats work, adds sources the user did not choose and may fetch material the user already has under a better licence.
- Check: manual - the report states the chosen mode; with the user-first mode the manifest shows the user-authorized records registered before any downloaded record, the shortfall (counts and missing families or topics) is stated before the search proposal, and no search or download precedes the approval of the proposal; with the no-search mode the report is `INCOMPLETE` unless the user documents alone meet both thresholds.
