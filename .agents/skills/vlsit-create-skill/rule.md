# Rules

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
These rules are mandatory every time this skill runs, and they describe what every skill it creates must satisfy. When this file, SKILL.md and a file in `reference/` differ, this file wins.

Each rule has a permanent ID that is never reused or renumbered. New house-format skills use a level-3 heading (`### R-001 Title`), a statement beginning with MUST or MUST NOT, a Why line and a Check line. Established domain-specific skills may retain their documented one-line ID namespace (for example, `- OCI-001 (MUST): ...`); do not mix the two formats in one rule file. No two rules may repeat or contradict each other. "validate" below means `scripts/vlsit_skillkit.py validate`.

## Layout

### R-001 Four parts
MUST give every skill four parts: a SKILL.md workflow file, a rule.md file, a reference/ folder and a scripts/ folder, each folder holding at least one file.
- Why: the workflow, the mandatory rules, the background knowledge and the deterministic code each have one fixed place, so every skill reads the same way. Git keeps no empty folders, so an unused folder holds a `.gitkeep`.
- Check: validate.

### R-002 No nested skill file
MUST NOT place any SKILL.md other than the top-level one inside a skill folder; templates use the `.tpl` extension.
- Why: the tools discover every SKILL.md they find and would load a nested one as a second, unintended skill.
- Check: validate.

### R-003 One source, three platform trees
MUST write each skill in `.claude/skills/<name>/` and produce exact copies in `.agents/skills/<name>/` and `.dsh/skills/<name>/` only by running `scripts/vlsit_skillkit.py mirror` after the last edit.
- Why: the three skill loaders use different discovery folders; one canonical source and scripted mirrors prevent the platform copies from drifting apart.
- Check: `scripts/vlsit_skillkit.py mirror --check` reports IN SYNC for both `.agents/skills/<name>/` and `.dsh/skills/<name>/`.

## Metadata

### R-004 Skill name
MUST name the skill with lowercase letters, digits and single hyphens, at most 64 characters, identical to its folder name and starting with `vlsit-` unless the user states another prefix.
- Why: the name is the skill's identity in both tools, and a mismatch with the folder makes it hard to find or load.
- Check: validate.

### R-005 Portable frontmatter
MUST NOT use frontmatter keys other than `name`, `description`, `compatibility`, `license` and `metadata`.
- Why: other keys are specific to one tool; one tool ignores them and hosted environments reject them with a hard error.
- Check: validate.

### R-006 Description content
MUST write the description as one line of at most 500 characters that states what the skill does and when to use it.
- Why: the assistant reads only the name and description to decide whether to load a skill, so this line decides whether the skill triggers at the right moment.
- Check: validate.

### R-007 Description syntax
MUST NOT put a colon followed by a space inside the description.
- Why: an unquoted value containing that sequence breaks the YAML header, and the skill then loads without its fields.
- Check: validate.

## Language

### R-008 Professional English
MUST write SKILL.md, rule.md, reference documents and script code and comments in professional English, keeping Vietnamese only where it is real data such as search keywords, document names or output content, with an English gloss at first use.
- Why: one working language keeps the files readable for every maintainer and for both tools.
- Check: manual - read the files and look for prose in another language.

### R-009 Tool-neutral text
MUST NOT name an AI tool product or write a tool-specific invocation of a skill in SKILL.md or rule.md.
- Why: one file must serve both tools, so it cannot depend on either tool's command syntax. Reference documents may name tools where they document format facts.
- Check: validate.

## Rules file

### R-010 Rule identity
MUST give each rule a unique, permanent ID and keep that ID unchanged for the life of the rule. New house-format skills use an `R-NNN` level-3 heading; an established domain-specific skill MAY retain its documented prefix and one-line rule form.
- Why: other files and reports cite rules by ID, so a changed or reused ID silently breaks those citations.
- Check: validate reports unique IDs and resolves rule citations for either supported format.

### R-011 Rule anatomy
MUST write each house-format rule as one checkable requirement that starts with `MUST` or `MUST NOT` and is followed by a Why line and a Check line. A domain-specific rule file MAY retain its established direct-rule form and normative keywords.
- Why: a rule with a reason can be applied to cases the author did not foresee, and a rule with a check can be verified instead of trusted.
- Check: validate checks the house-format anatomy or the domain-specific rule IDs and keywords.

### R-012 No repetition or contradiction
MUST leave rule.md with no two rules that repeat or contradict each other, resolving each case by merging or rewording the rules instead of adding an exception rule.
- Why: duplicated rules drift apart over time, and contradicting rules leave the assistant without a correct action.
- Check: validate reports no error for rule pairs, and every REVIEW pair it lists was judged by hand and reworded if the two rules really overlap or conflict. The script compares wording only, so the rule list is also read once by hand for opposite rules phrased differently.

### R-013 Precedence
MUST state in both SKILL.md and rule.md that rule.md overrides SKILL.md, and SKILL.md overrides the reference files, when they differ.
- Why: guidance in reference files is background knowledge and may be outdated or looser than the rules, so the order must be explicit.
- Check: validate.

## SKILL.md and reference

### R-014 Rules come first
MUST make the first workflow step of SKILL.md read rule.md in full.
- Why: a rule that was never read cannot be followed, and reading it first shapes every later step.
- Check: validate checks that SKILL.md refers to rule.md; manual - the first workflow step is the reading step.

### R-015 Rules close the work
MUST end the SKILL.md workflow with a step that checks the result by rule ID and reports the outcome.
- Why: checking by ID makes the verification complete and lets the user see exactly which rules were checked.
- Check: validate; manual - the last workflow step names the rule IDs.

### R-016 Short SKILL.md
MUST keep SKILL.md under 500 lines by moving detail into reference/ files.
- Why: SKILL.md stays in the assistant's context after it loads, so every extra line is paid for on every turn.
- Check: validate.

### R-017 Linked files
MUST link every file under reference/ and scripts/ from SKILL.md, or from a reference document that SKILL.md links, saying when to read or run it.
- Why: the assistant discovers supporting files only through such links, and a file nobody points to is never used.
- Check: validate.

### R-018 Requirements live in rule.md
MUST state every mandatory requirement as a rule in rule.md and use reference/ files only for guidance and background.
- Why: the precedence order then needs no judgment, because anything mandatory is in the file that wins.
- Check: manual - search reference/ for requirements that rule.md does not contain.

### R-019 Reply language
MUST have SKILL.md tell the assistant to reply in the language the user uses.
- Why: the skills are written in English but their users may write in any language.
- Check: validate.

## Scripts

### R-020 Mechanical steps in scripts
MUST implement each deterministic step, such as scaffolding, parsing, validating, converting or copying files, as a script in scripts/ that SKILL.md calls, instead of describing the step for the assistant to repeat by hand.
- Why: a script gives the same result every time and costs a few output lines instead of many tokens of reasoning.
- Check: manual - no step in SKILL.md asks the assistant to do by hand what a script could do.

### R-021 Python first
MUST write scripts in Python 3, and use another runtime only when the user asks for it or when Python cannot do the task.
- Why: Python is readable, runs on every platform, and its standard library covers files, text, JSON, hashing, archives and HTTP, so scripts stay short.
- Check: validate warns about script files that are not Python; manual - the reason is recorded when another runtime is used.

### R-022 Standard library only
MUST NOT import a third-party package in a script unless the standard library cannot do the job and the user has approved that package.
- Why: every package is something the user must install and keep working, while the standard library comes with Python itself.
- Check: validate lists every import that is not in the standard library.

### R-023 Python must exist first
MUST find a working Python 3 before running any script, with `vlsit_find_python.ps1` on Windows or `vlsit_find_python.sh` on Linux and macOS, and, when there is none, ask the user to install it or to approve an installation by the assistant instead of continuing without it.
- Why: the user may not know that Python is missing, and on Windows the python command on PATH is often only a Microsoft Store shortcut, so a plain version check is not reliable.
- Check: validate checks that both locators ship with the skill and that SKILL.md runs them; manual - nothing was installed before the user agreed.

### R-024 UTF-8 text files
MUST open every text file in a script with an explicit UTF-8 encoding.
- Why: Python on Windows defaults to the local code page, which corrupts Vietnamese text without any error.
- Check: validate.

### R-040 One script, both operating systems
MUST ship every non-Python script for both operating systems, a `.ps1` file for Windows and a `.sh` file for Linux and macOS with the same name, options, output and exit codes, showing in SKILL.md how to run each.
- Why: a skill is used on Windows workstations and on Linux servers alike, and a script that exists for one system only makes the skill fail on the other.
- Check: validate reports every `.ps1` without a `.sh` twin, and every `.sh` without a `.ps1` twin; manual - run both twins on a sample and compare the output.

### R-041 Portable shell scripts
MUST write each `.sh` script in POSIX sh, starting with `#!/bin/sh`, with LF line endings and without bash-only constructs.
- Why: Linux distributions use different default shells (dash, ash, bash, zsh), and only POSIX sh behaves the same in all of them.
- Check: validate checks the first line and the line endings and warns about bash-only constructs; manual - run the script under dash.

### R-042 File names
MUST name every file of the skill with the prefix `vlsit_`, for example `vlsit_find_python.sh` or `vlsit_writing_rules.md`, and write the same name wherever SKILL.md or another file mentions it. Script names use lowercase letters, digits and underscores only. Only these keep their names: `SKILL.md` (the tools find a skill by it), `rule.md`, `README.md`, `LICENSE`, third-party files kept verbatim under `assets/`, and the `.sv` files under `rtl_example/`, which are named after their module as the RTL rules require.
- Why: skill files are copied to the machines of many users, and the prefix shows where a file comes from and keeps it from clashing with other tools.
- Check: validate.

### R-043 Script header
MUST begin every `.py`, `.ps1` and `.sh` script with a header of comment lines that states what the script does (`Function:`), its author (`Author:`) and its GitHub link (`GitHub: https://github.com/...`).
- Why: a script is often read or reused without its skill folder, and the header tells the reader its purpose and where to report or find updates.
- Check: validate looks for the three fields in the first lines of each script; manual - the Function line describes what the script really does.

### R-025 ASCII-only PowerShell
MUST keep every .ps1 file ASCII-only.
- Why: Windows PowerShell 5.1 reads a file without a byte-order mark in the local code page and corrupts other characters.
- Check: validate.

### R-026 Short output and exit codes
MUST make each script print a short result and return exit code 0 on success and non-zero on failure.
- Why: the assistant reads the output, so a long dump costs tokens and a missing exit code hides failures.
- Check: manual - run each script on a sample input and look at the output and the exit code.

### R-027 No silent overwrite
MUST NOT let a script overwrite or delete an existing file unless the caller passes an explicit switch such as `--force`.
- Why: an existing file may hold the user's hand edits, which are lost without a trace.
- Check: manual - run the script twice on the same output and confirm that it stops the second time.

### R-028 Declared needs
MUST state in SKILL.md, or in its compatibility field, the runtime, network access and installation that each script needs.
- Why: the user can then see before the first run what the skill will use and whether it fits the machine.
- Check: validate warns when scripts exist and compatibility is missing.

## Interview and design

### R-035 Interview first
MUST start every skill-creation task by asking the user to describe the skill in detail, following the interview guide, before running the scaffold.
- Why: a detailed description gives the real purpose, triggers, inputs and requirements, and learning them before building is far cheaper than rebuilding afterwards.
- Check: manual - the request for the description was sent in chat before any file of the new skill was created.

### R-036 Options with analysis
MUST present at least two options for each design decision the user has not already settled, and give every option its meaning, its advantages and its disadvantages.
- Why: the user knows the business context and can weigh trade-offs only when the alternatives are visible, which a bare question or a single proposal hides.
- Check: manual - each option set in the chat shows meaning, advantages and disadvantages for every option.

### R-037 The user chooses
MUST leave the choice among options to the user, marking at most one option per decision as recommended and giving the reason.
- Why: a recommendation helps a user who is unsure, but applying it unasked would replace the user's judgment with the assistant's.
- Check: manual - each chosen option traces to the user's answer; "you decide" is recorded as the choice of the recommended option.

### R-038 Approved design
MUST summarize the agreed design to the user and receive their approval before running the scaffold.
- Why: the summary exposes a misunderstanding while one message fixes it, instead of after the skill was built.
- Check: manual - an approval message follows the design summary and comes before the scaffold command.

### R-039 Open choice in every option set
MUST end every set of choices offered to the user, in the interview or in the design step, with an open choice where the user can write their own idea.
- Why: the assistant's list can never cover every need, and a closed list forces the user to pick something that does not fit.
- Check: manual - every set of choices shown in the chat ends with an open choice, and the user's own wording is recorded as given.

## Process

### R-029 Ask for what is missing
MUST ask the user for any missing purpose, trigger situation, input, output or constraint of the skill instead of inventing it.
- Why: an invented detail becomes a silent defect in a skill that will be reused many times.
- Check: manual - every requirement in the new skill traces to the user's words or to an answer.

### R-030 Existing skills
MUST NOT overwrite or delete an existing skill folder without the user's explicit approval for that folder.
- Why: the folder may hold work that is not stored anywhere else.
- Check: `scripts/vlsit_skillkit.py new` stops when the folder exists; manual - approval was given in chat before any change to an existing skill.

### R-031 No leftover placeholders
MUST NOT leave scaffold placeholders in SKILL.md, rule.md or a script.
- Why: a leftover placeholder is an instruction the assistant cannot follow.
- Check: validate.

### R-032 Validated before done
MUST run validate on the finished skill and reach zero errors before reporting the skill as complete.
- Why: the report is the user's only evidence that the skill follows the house format.
- Check: the last validate run shows RESULT: PASS.

### R-033 Repository README
MUST add the new skill to the README skills table and layout, in every language the README is written in, when the repository has a README that lists skills.
- Why: the README is where users find the skills, and a missing entry makes a skill invisible.
- Check: manual - search the README for the skill name.

### R-034 Honest report
MUST report only the checks that were actually run and list what remains untested.
- Why: the user decides whether to trust the new skill from this report.
- Check: manual - every claim in the report points to a command output.

### R-044 Defined terminology
MUST expand domain abbreviations at first use in generated prose and provide a scoped glossary when several shortened terms are used. Explain context-dependent terms from the specification instead of guessing. Preserve code identifiers and do not invent expansions for brands or tool names; keep README explanations bilingual where this repository requires it.
- Why: a reader can confuse a bus model, verification package and simulator interface when BFM, VIP, VPI and DPI are left undefined.
- Check: manual - read the first occurrence and glossary, verify ambiguous meanings, and confirm identifiers are unchanged.
