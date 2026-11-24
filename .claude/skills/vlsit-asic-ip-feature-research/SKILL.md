---
name: vlsit-asic-ip-feature-research
description: Research Application-Specific Integrated Circuit (ASIC) intellectual-property (IP) and System-on-Chip (SoC) features, architecture, integration, prevalence, licensing and patent evidence. Use when the user wants a source-grounded feature study or improvement opportunities.
compatibility: Python 3.8 or later using the standard library only. Research requires internet access. Downloads must use openly accessible sources or files the user is authorized to provide; the downloader does not use credentials or bypass access controls.
---

# ASIC IP feature research

This skill performs evidence-led research into functions, features, architecture and microarchitecture of an Application-Specific Integrated Circuit (ASIC) intellectual-property (IP) block or system-on-chip (SoC). It does not design or modify register-transfer-level (RTL) code, provide legal advice, or claim market-wide prevalence from a limited document sample.

Reply in the language the user uses unless the user requests otherwise. Research reports and figures created by this skill are always in English. Expand every domain abbreviation at first use and explain it; maintain the local glossary for terms used repeatedly. Rules in [rule.md](rule.md) override this workflow, and this workflow overrides reference guidance.

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely before doing anything else. Treat each rule as mandatory.

### 2. Find Python

Before any script, locate Python 3.8 or later using `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux/macOS. If it reports `NOT FOUND`, follow rule R-023 and do not proceed with scripts until Python is available.

### 3. Define the research question and workspace

Identify the target IP or SoC, the feature/function or architecture question, intended applications and users, relevant product/market scope, technology or interface constraints, and desired depth. Ask concise questions for material gaps; do not silently choose an ambiguous expansion such as Neural Processing Unit versus Network Processing Unit. The user must supply an absolute or workspace-relative research output directory. Ask for it if absent. Preserve existing files and keep all acquired materials inside the chosen research directory.

### 4. Choose the source mode and freeze the protocol

Ask how the sources are obtained (R-026), in the question format of the house rules: options with their advantages and disadvantages, a recommendation and an open choice.

| Option | What happens | Advantage | Disadvantage |
|---|---|---|---|
| A. My documents first, search only for the gap (recommended) | You give a folder or list of documents; the skill registers and qualifies them, reports what is still missing, and only then proposes a supplementary search | Uses what you already have and are authorized to use; the search is limited to the shortfall | You must collect the documents first |
| B. Search for everything | The skill finds all candidates and asks approval per batch | No preparation by you | Misses documents you hold; more candidates to review |
| C. My documents only, no search | The skill analyses only what you provide | No network use; full control of the corpus | Likely `INCOMPLETE` if the thresholds are not met |

Read [reference/vlsit_source_qualification.md](reference/vlsit_source_qualification.md) and [reference/vlsit_research_method.md](reference/vlsit_research_method.md). Record the research question, inclusion/exclusion criteria, search engines/catalogs, exact queries, search date, time range, language, product families, and how sources will be deduplicated before counting. In option A, freeze the criteria before assessing the user documents and freeze the queries only when the supplementary search is proposed; in option C record that no search was performed. Search primary sources for product documents and reputable peer-reviewed venues for papers. Keep other source types as context only; they do not satisfy the minimum counts.

### 5. Register user documents, then find and approve what is missing

**5a. User documents first (options A and C).** Ask for the folder or the list of documents. Run `inventory` on the folder (read-only: path, size, SHA-256, whether already registered), classify each file as a datasheet/databook or a paper, and ask the user for the missing facts of each (product-family key, publisher or venue, year, peer-review status, licence notice). Register each document with `register --access-basis user-authorized` (the user confirms they are authorized to use it), qualify it by the criteria below, and run `check` to get the counts. Report the achieved and missing counts, the product families and topics that are still thin, and the documents that do not qualify with the reason.

**5b. Supplementary search (option A, or B from the start).** When a threshold or a topic is short, say exactly what is missing and propose the search (queries, catalogs, number of candidates to find) as a separate question: search, or stay with the user documents and label the study `INCOMPLETE`. Search only after the user answers yes. Candidates the user already supplied are not proposed again.

**5c. Candidate rules (all options).** Find at least ten distinct, eligible datasheets/databooks covering distinct product families and at least ten distinct, relevant, full-text peer-reviewed scientific papers. Check publisher, venue, review status, relevance, revision/date, full-text availability, legal access basis and duplicate relationships. Do not count abstracts, search snippets, vendor marketing pages, duplicate editions, or an inaccessible paper as a full-text paper.

Before downloading a batch (user-supplied files need no download), show a compact candidate list with title, publisher/venue, date, direct source link, access basis, estimated file size when known, license/copyright notice and intended local filename. Ask the user to approve that batch. Never sign in, evade a paywall, defeat a download restriction, or infer that public visibility grants redistribution rights. Then use `vlsit_asic_ip_feature_research.py` to initialize the evidence directory and record approved downloads or user-provided files. Read [reference/vlsit_license_and_patent_review.md](reference/vlsit_license_and_patent_review.md) for the distinctions and evidence required.

If either minimum cannot be met, continue only if useful, label the work `INCOMPLETE`, show the achieved and missing counts, and do not present its prevalence or recommendation as meeting the agreed evidence threshold. Do not manufacture sources or lower the threshold silently.

### 6. Extract claims and evaluate feature prevalence

Read [reference/vlsit_report_template.md](reference/vlsit_report_template.md). Build a feature/function taxonomy and a traceable evidence matrix. For each claim record source identifier, exact page/section, brief paraphrase, source type/date, confidence and any counterevidence. Reconcile contradictions explicitly; separate documented fact, inference, assumption and unknown.

Calculate two separate corpus occurrence rates: (a) distinct eligible product families that explicitly document a feature divided by product families whose sources provide enough information to assess it, and (b) distinct eligible papers that substantively discuss the feature divided by eligible papers analyzed. Report raw numerator and denominator, exclusions, missing information, corpus selection bias and the search date. Describe these only as rates in the researched corpus, never as market share or universal popularity. Keep product availability, research attention and application relevance as separate judgments.

### 7. Analyze system relationships and integration

Map each feature to its application role, neighboring blocks, data/control flow, protocol and software interaction. At block and microarchitecture levels, extract documented controller/datapath roles, pipeline stages, buffering, arbitration, ordering, state machines, transaction sequencing, error handling and configuration dependencies when sources describe them. State the source evidence and direction of each relationship. For any off-chip input/output (I/O) pad path, identify the documented pad or physical-layer interface (PHY) role, electrical signaling or standard, external peer/device, package or board dependency, voltage/clock/reset assumptions, and integration requirements. If a document omits a property, mark it unknown and list what must be confirmed; do not infer a pad cell, electrical rating or external chip from a logical interface name alone.

Evaluate integration dependencies and trade-offs such as power, performance and area (PPA), clock/reset, bandwidth/latency, memory, security, safety, test, software driver/Application Programming Interface (API), configuration, backward compatibility, package pins and manufacturing process. Explain which product lines or applications show the feature, with evidence and the limits of the sample.

### 8. Review licensing and patent evidence

For each feature and source, distinguish document copyright, implementation or RTL license, standards/specification access terms, patent statements and third-party dependencies. Search relevant patent databases and primary legal or standards sources for identified features. Record exact source, applicant/owner, jurisdictions, publication or grant number, status as shown by the source, claim/topic relevance, and lookup date. Label unresolved status and search coverage. Never call a feature unpatented, royalty-free, freely implementable or legally cleared solely because no matching record was found; do not give legal advice.

### 9. Propose improvements and illustrations

Propose new or enhanced features only when linked to a specific user/software/system need and evidence that current features leave it unresolved or costly. For every proposal state the unmet need, evidence and confidence, expected user benefit, architecture/software impact, integration and PPA costs, compatibility and security risks, licensing/patent uncertainty, alternatives, and an actionable validation experiment. Mark novelty as a hypothesis pending broader prior-art and legal review.

Create a draw.io file and concise visual illustrations when they materially clarify architecture, interfaces, operation, timing or state behavior. Label every block and connection from evidence; distinguish confirmed interfaces from inferred/unknown ones. Read [reference/vlsit_report_template.md](reference/vlsit_report_template.md) for diagram expectations. Visuals support the report and must not replace its citations or evidence tables.

### 10. Write and audit the report bundle

Write the English Markdown report, source manifest, locally retained eligible sources, and required figure files into the user-supplied research directory. Use the report template and glossary. Never overwrite a prior artifact without explicit approval. Record source hashes and original links; retain access notices and do not republish restricted material. Run:

```powershell
<python> "<skill folder>\scripts\vlsit_asic_ip_feature_research.py" check "<research directory>"
```

Use `/` in the path on Linux/macOS. A complete evidence gate exits 0 and reports `READY`; unmet thresholds exit 4 and report `INCOMPLETE`; malformed or missing evidence exits 1. A `READY` result checks manifest counts, unique product-family/source identifiers, local file presence and hashes; it does not validate research quality or truth of claims. Correct all mechanical issues, then manually audit citations, feature counts, licenses, patent dates, diagram evidence and every percentage.

### 11. Verify against the rules

Check the report and bundle against every rule ID in [rule.md](rule.md). Distinguish script checks from manual judgments. Report the source mode, the status (`READY` or `INCOMPLETE`), actual qualifying source counts, how many came from the user and how many from the search, saved artifact paths, search date, key limits, and anything not verified. Never claim a legal clearance or market-wide prevalence.

## Reference

Read a file when its workflow step calls for it.

| File | Read it when |
|---|---|
| [reference/vlsit_glossary.md](reference/vlsit_glossary.md) | Defining domain terminology, acronyms or ambiguous terms in the report |
| [reference/vlsit_source_qualification.md](reference/vlsit_source_qualification.md) | Searching, selecting, deduplicating or scoring product documents and scholarly papers |
| [reference/vlsit_research_method.md](reference/vlsit_research_method.md) | Freezing the search protocol, calculating corpus occurrence rates or reconciling evidence |
| [reference/vlsit_source_manifest_schema.md](reference/vlsit_source_manifest_schema.md) | Initializing the bundle and recording direct downloads or authorized user files |
| [reference/vlsit_license_and_patent_review.md](reference/vlsit_license_and_patent_review.md) | Reviewing document rights, implementation licenses, standards terms or patent evidence |
| [reference/vlsit_report_template.md](reference/vlsit_report_template.md) | Drafting the report, comparison tables, integration analysis or figures |
| [reference/vlsit_self_test.md](reference/vlsit_self_test.md) | Checking the mechanical evidence gate and its known limits |

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1` and `scripts/vlsit_find_python.sh` | Locating Python before a script run |
| `scripts/vlsit_asic_ip_feature_research.py init <directory>` | Creating a new evidence directory and empty source manifest; stops if either already exists |
| `scripts/vlsit_asic_ip_feature_research.py download <directory> ...` | Saving one approved, directly accessible file and registering its metadata/hash |
| `scripts/vlsit_asic_ip_feature_research.py inventory <folder> [--bundle <directory>]` | Step 5a: listing the documents the user supplied (path, size, SHA-256, already registered or not); read-only |
| `scripts/vlsit_asic_ip_feature_research.py register <directory> ...` | Copying one user-provided, authorized file into the evidence directory and registering it |
| `scripts/vlsit_asic_ip_feature_research.py check <directory>` | Checking minimum evidence counts (and how many datasheet families and papers are still missing), deduplication keys, file presence and SHA-256 hashes |

Command syntax and required metadata flags are documented in [reference/vlsit_source_manifest_schema.md](reference/vlsit_source_manifest_schema.md). Download and register commands require `--approved`, representing the user's approval of the proposed batch.

## Output

The user supplies the output directory. The bundle contains an English Markdown research report, `vlsit_source_manifest.csv`, a `vlsit_sources/` folder for approved local copies, and draw.io/visual files when useful. Existing content is preserved; the final response links the report and states evidence-gate status, qualifying counts, search date and limits.

## FSM draw.io example

Use the [Moore transfer controller](reference/examples/vlsit_fsm_moore_transfer.drawio) as a visual example when state behavior helps explain a feature. Derive any research figure from the cited sources and label any unknown behavior.
