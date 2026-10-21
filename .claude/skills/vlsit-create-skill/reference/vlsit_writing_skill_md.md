# Writing SKILL.md

Guidance only; the mandatory requirements are in [rule.md](../rule.md).

## The description is the trigger

The assistant sees only `name` and `description` until it picks a skill, so the
description decides whether the skill is used at the right moment. Put in it:

1. what the skill does, in one clause;
2. "Use when the user ..." followed by the situations and the words people use;
3. the near-misses, phrased as "even if they never say X", when users rarely name
   the task directly.

Write it on one line, at most 500 characters, with no colon followed by a space
(use a dash or a comma). Lead with the main use case: long descriptions are cut
in the listing.

| | Example |
|---|---|
| Weak | `Helps with documents.` |
| Strong | `Convert scanned PDFs or photos into editable Word files using Vietnamese OCR. Use when the user wants to OCR a document, asks why text in a PDF cannot be copied, or wants to edit a scanned legal document.` |

Vietnamese words can appear in the description when they are what users actually
type (document numbers, terms), with an English gloss.

## Workflow style

- **Numbered steps in the order they happen.** Step 1 reads rule.md; the last step
  verifies against the rules by ID and reports.
- **Say why**, not only what. An assistant that knows the reason handles the case
  the author did not foresee; a bare command is applied blindly.
- **Ask, do not guess.** State which input is required, and tell the assistant to ask
  one short question when it is missing. Name the exception, if there is one.
- **Give the exact command** for every scripted step, with the expected result
  (`READY`, exit code 3, and so on) and what to do for each.
- **Match the freedom to the risk.** Fragile steps (file conversion, data loss) get
  exact commands; open-ended steps (drafting, summarizing) get goals and criteria.
- **Be honest about limits.** Include a short section on what the skill cannot do or
  cannot verify, so the assistant reports it instead of hiding it.

## Keep SKILL.md small

SKILL.md holds the workflow. Move to `reference/` anything the assistant needs only
sometimes: long tables, format specifications, examples, domain background. Keep the
links one level deep and say when to read each file. Move to `scripts/` anything
mechanical.

## Layout of a good SKILL.md

```
frontmatter (name, description, optional compatibility)
# Title
what it does / does not do; reply-language line; precedence line
## Workflow        1. read rule.md ... N. verify against the rules
## Reference       table: file | read it when
## Scripts         table: script | run it when
## Output          where results go; what to report
```

File names (R-042): every file the skill uses, in `reference/`, `scripts/`, `templates/` and examples, starts with `vlsit_` (for example `reference/vlsit_writing_rules.md`). Only `SKILL.md`, `rule.md`, `README.md`, `LICENSE` and third-party files under `assets/` keep their names. Write each file name in full wherever it is mentioned.

The template in [templates/vlsit_SKILL.md.tpl](templates/vlsit_SKILL.md.tpl) has this shape.

## Keep out of SKILL.md

- product names of AI tools and their invocation syntax (`/name`, `$name`), so one
  file serves both tools;
- requirements phrased as background advice: if it is mandatory, it is a rule;
- long copies of material that already lives in `reference/`;
- time-sensitive statements without a date.
