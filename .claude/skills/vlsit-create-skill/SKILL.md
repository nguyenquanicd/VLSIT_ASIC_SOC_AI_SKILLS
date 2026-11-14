---
name: vlsit-create-skill
description: Create a new agent skill in the house format (SKILL.md workflow, rule.md with numbered rules, reference/ and scripts/ folders) and mirror it to the repository's supported assistant skill folders. Interview the user, offer design options with advantages and disadvantages, then validate and mirror the skill. Use when the user asks to create, build, scaffold, write, standardize or fix a skill, a SKILL.md or a rule.md, or wants to turn a repeated workflow into a reusable skill.
compatibility: Python 3.8 or later using the standard library only, and works offline. Windows PowerShell 5.1 (Windows) or POSIX sh (Linux, macOS) is used only to locate or install Python. No administrator rights are needed for the skill itself.
---

# Create a skill in the house format

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
This skill builds other skills. Every skill it produces has the same four parts, so
any of them can be read, checked and maintained the same way:

| Part | Role |
|---|---|
| `SKILL.md` | The orchestrator: the workflow and what the assistant must do, step by step |
| `rule.md` | The mandatory requirements, each with a permanent ID (`R-NNN`); SKILL.md calls this file |
| `reference/` | Background documents and templates the skill reads on demand |
| `scripts/` | Python scripts for mechanical work, so the assistant spends output lines instead of reasoning |

Before building anything it interviews the user for a detailed description of the
skill, then lays out the real design choices with advantages and disadvantages and
lets the user decide.

Reply to the user in the language they use.

If instructions differ, follow them in this order: [rule.md](rule.md) first, then this
file, then the files in `reference/`. The rules in `rule.md` apply both to how this
skill works and to every skill it creates.

All work goes through `scripts/vlsit_skillkit.py` (path relative to this skill folder), run
with the Python that step 2 finds:

```powershell
<python> "<skill folder>\scripts\vlsit_skillkit.py" <action> ...
```

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely before doing anything else. The rules are
mandatory, and step 11 checks the result against them by ID.

### 2. Find Python

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

On Linux or macOS use the twin script instead (plain POSIX sh, works on every distribution):

```sh
sh "<skill folder>/scripts/vlsit_find_python.sh"
```

It prints the full path of a working Python 3.8 or later (this is `<python>`) and
exits 0, or prints `NOT FOUND` and exits 3. A plain `python --version` is not enough:
on Windows the `python` on PATH is often only a Microsoft Store shortcut, and a
python.org install is often missing from PATH; the script copes with both.

If Python is not found, stop and do not guess. Tell the user that Python 3 is needed,
and let them choose: install it themselves from python.org, or let you install it
with `vlsit_find_python.ps1 -Install` (winget; the installer may ask Windows for approval)
or `vlsit_find_python.sh --install` (the system package manager; it may ask for the
password). `vlsit_find_python.sh --options` prints the install command of each Linux
family. Run the install only after they agree, then run the locator again.

### 3. Interview the user

Before creating anything, ask the user to describe the skill in detail, in their own
words. Send one message that invites free-form answers (partial answers are fine) and
lists the topics: purpose and what it must not do; who uses it and the phrases they
would type; input; output; how the job is done by hand today; what must always or
never happen; sample files, templates and documents; environment and limits. The
wording and an example message are in
[reference/vlsit_interview_guide.md](reference/vlsit_interview_guide.md).

Then ask follow-up questions only about gaps and vague answers: at most four
questions per round and two rounds. Do not ask what the conversation or the
repository already answers, and never fill a gap with an invention. When the user
says "you decide", propose a value, mark it as an assumption and put it in the design
summary of step 5. Any follow-up that offers choices ends with an open choice where
the user can write their own idea.

If the user wants to improve an existing skill rather than create one, read it first
and ask for approval before changing it.

### 4. Offer design options

Some choices change what the skill does, costs and risks, and the right answer
depends on the user's business, not on a default. For each such decision the user
has not already settled, present at least two options, each with what it means, its
advantages and its disadvantages, and when to choose it. Mark at most one option as
recommended and give the reason, and end every set with an open choice such as
"Other - write your own idea", so that the user can enter a different opinion. The
user decides.

[reference/vlsit_design_options.md](reference/vlsit_design_options.md) holds the catalog (scope,
where the work is done, confirmation before risky steps, trigger breadth, reference
material, output location, script structure, outside packages, rule strictness,
testing depth), when to raise each decision, the format of the message and how to
treat the user's own idea. Raise only the decisions that fit this skill, usually two
to five, in one message. Record each answer; "you decide" means the recommended
option and is recorded as such.

### 5. Confirm the design

Summarize the agreed design in one message: name, draft description, the rules (one
line each), the workflow steps, the scripts and what each does, the reference files,
the environment needs, the options chosen with the user's own ideas in their words,
and every assumption. Ask for approval or changes. Do not create the skill folder
until the user approves.

### 6. Scaffold

```powershell
<python> "<skill folder>\scripts\vlsit_skillkit.py" new --name vlsit-<topic> --description "<what it does. Use when ...>" --with-script
```

Run it from the repository root, or pass `--root <skills folder>`. It creates
`.claude/skills/<name>/` with templated `SKILL.md`, `rule.md`, `reference/` and
`scripts/`; with `--with-script` it also creates a starter Python script named
`vlsit_<topic>.py` with the standard header, and copies of the locators
`vlsit_find_python.ps1` and `vlsit_find_python.sh`. The header carries the author and
GitHub link; pass `--author` and `--github` to change the defaults. It refuses to touch a folder that already exists. Every blank to
fill is marked with a placeholder, and `validate` fails until all of them are gone.

### 7. Write the rules

Fill `rule.md` first, because the workflow is written to satisfy it. Turn each
mandatory requirement from the design into one rule with a statement, a Why line and
a Check line. Read [reference/vlsit_writing_rules.md](reference/vlsit_writing_rules.md) when you
are unsure how to word a rule or how to settle a duplicate or conflict.

### 8. Write the workflow, reference files and scripts

Apply R-044: define domain abbreviations on first use and add a scoped English glossary; use bilingual explanations in README/guideline files. Spell out Bus Functional Model (BFM), distinguish it from Verification IP (VIP), and do not confuse VIP with Verilog Procedural Interface (VPI). Preserve API and identifier spellings.

- **SKILL.md**: read [reference/vlsit_writing_skill_md.md](reference/vlsit_writing_skill_md.md)
  for the description, the step style and what to keep out of the file. Keep the
  first step "read rule.md", the "Find Python" step when there are scripts, and the
  last step "verify against the rules".
- **reference/**: put background and templates here, one topic per file, and link
   each from SKILL.md with a "read it when" note. Platform-specific skill behavior
  formats are in [reference/vlsit_skill_format.md](reference/vlsit_skill_format.md).
- **scripts/**: write every mechanical step as a Python script that uses only the
  standard library. Name every script file with the prefix `vlsit_`, start it with
  the header (`Function`, `Author`, `GitHub`), and give any non-Python script a twin
  for the other operating system (`.ps1` with `.sh`). Read [reference/vlsit_writing_scripts.md](reference/vlsit_writing_scripts.md)
  for the interface pattern, the Windows pitfalls and how to test a script.

### 9. Validate

```powershell
<python> "<skill folder>\scripts\vlsit_skillkit.py" validate ".claude\skills\<name>"
```

It prints one line per problem and a `RESULT` line. Fix every `ERROR` and run it
again until the result is `PASS`. Read each `WARN`. Judge each `REVIEW` pair by hand:
if two rules really overlap or conflict, merge or reword them, never add an
exception rule.

The script compares the wording of rules, so it cannot see two rules that say
opposite things in different words. After the script passes, read the rule list once
more yourself, looking for exactly that.

### 10. Mirror and document

Mirror to both secondary skill folders, then confirm them:

```powershell
<python> "<skill folder>\scripts\vlsit_skillkit.py" mirror ".claude\skills\<name>"
<python> "<skill folder>\scripts\vlsit_skillkit.py" mirror ".claude\skills\<name>" --check
```

If the repository has a README that lists skills, add the new skill to its table and
layout, in every language the README uses.

### 11. Test, verify against the rules, report

1. Run each script of the new skill on a sample input and look at the output and the
   exit code. Say plainly in the report what you could not test, for example
   behavior that needs the other tool or a network.
2. Check the result against every rule ID in [rule.md](rule.md): the rules whose Check
   line names `validate` are covered by step 9; go through the manual ones by hand,
   including the interview and option rules (R-035 to R-039).
3. Report to the user: the path of the new skill and both secondary mirrors, the final
   `validate` line and the number of rules, the design choices that were made, what
   was tested and what was not, and how the skill is used (the assistant picks it by
   its description; the README explains how to invoke it by name).

## Reference

Read a file only when the step needs it.

| File | Read it when |
|---|---|
| [reference/vlsit_interview_guide.md](reference/vlsit_interview_guide.md) | Step 3: wording of the opening message, follow-up questions and the design summary of step 5 |
| [reference/vlsit_design_options.md](reference/vlsit_design_options.md) | Step 4: the catalog of design decisions, the message format and the handling of the user's own idea |
| [reference/vlsit_skill_format.md](reference/vlsit_skill_format.md) | You need facts about folders, frontmatter, discovery or invocation in either tool |
| [reference/vlsit_writing_skill_md.md](reference/vlsit_writing_skill_md.md) | Writing the description and workflow of SKILL.md |
| [reference/vlsit_writing_rules.md](reference/vlsit_writing_rules.md) | Writing rules, or settling a duplicate or conflict |
| [reference/vlsit_writing_scripts.md](reference/vlsit_writing_scripts.md) | Writing or testing a script, or helping the user install Python |
| [reference/templates/vlsit_SKILL.md.tpl](reference/templates/vlsit_SKILL.md.tpl), [vlsit_rule.md.tpl](reference/templates/vlsit_rule.md.tpl), [vlsit_script.py.tpl](reference/templates/vlsit_script.py.tpl) | Used by `new`; read them only to change the house template |

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1` (Windows) and `scripts/vlsit_find_python.sh` (Linux, macOS) | Step 2, and again after Python was installed; add `-Install` or `--install` only after the user agreed |
| `scripts/vlsit_skillkit.py new` | Step 6: create the skill folder from the templates |
| `scripts/vlsit_skillkit.py validate` | Step 9, and after any later edit of a skill |
| `scripts/vlsit_skillkit.py mirror` | Step 10: copy the skill to both secondary folders; add `--check` to compare only |
