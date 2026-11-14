# Skill format: shared facts and repository integration

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Application Programming Interface (API). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Checked on 2026-10-16 against the official pages:
[Claude Code skills](https://code.claude.com/docs/en/skills) and
[Codex skills](https://learn.chatgpt.com/docs/build-skills). Tool documentation
changes; if something here looks wrong, check the pages again before relying on it.

This file is background only. Mandatory requirements are in [rule.md](../rule.md).

## Shared skill format

A skill is a folder whose entry point is `SKILL.md`: a YAML frontmatter block, then
Markdown instructions. The assistant always sees `name` and `description`. It loads
the body of `SKILL.md` only when the skill is chosen (by the user, or because the
request matches the description), and it reads other files in the folder only when
`SKILL.md` points to them. Scripts are run, not read into context.

## Where each tool looks

| | Claude Code | Codex | DeepSeek Harness integration in this repository |
|---|---|---|---|
| Project skills | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | `.dsh/skills/<name>/SKILL.md` |
| Personal skills | `~/.claude/skills/<name>/` | `$HOME/.agents/skills/<name>/` | `~/.dsh/skills/<name>/` |
| Invocation | `/skill-name` | `$skill-name`, or `/skills` to pick | `/skill-name` |
| Other | enterprise, plugin, nested `.claude/skills/` in sub-folders | admin `/etc/codex/skills`, bundled system skills | This repository's harness also searches `.agents/skills/` at a lower project priority |

The `.dsh/` locations describe this repository's DeepSeek Harness setup and may change
with the harness runtime. Author in `.claude/skills/`; `vlsit_skillkit.py mirror`
creates the `.agents/skills/` and `.dsh/skills/` copies and checks both.

## Frontmatter

| Key | Claude Code | Codex | House rule |
|---|---|---|---|
| `name` | optional (defaults to the folder name) | required | required, equals the folder |
| `description` | recommended | required | required, one line, at most 500 characters |
| `compatibility` | accepted, up to 500 characters | not listed | optional; states runtime and network needs |
| `license`, `metadata` | accepted (Agent Skills spec) | not listed | allowed |
| anything else (`allowed-tools`, `disable-model-invocation`, `context`, ...) | tool-specific controls | goes in `agents/openai.yaml` | not allowed in SKILL.md |

Why keep to the portable keys: Claude Code ignores unknown keys without a message,
but outside Claude Code (web uploads, the Skills API) unknown keys are a hard error,
and Codex keeps its own options in `agents/openai.yaml`. Specification limits:
`name` up to 64 characters of lowercase letters, digits and hyphens; `description`
up to 1024. The house limit for `description` is stricter (500) because Claude Code
truncates the combined description text in its skill listing and many skills share
that listing.

## Invocation

| | Claude Code | Codex | DeepSeek Harness integration in this repository |
|---|---|---|---|
| Explicit | `/skill-name` | `$skill-name`, or `/skills` to pick | `/skill-name` |
| Implicit | The assistant loads a skill whose description matches the request. | The assistant loads a skill whose description matches the request. | Harness discovery follows its configured project paths; this repository keeps `.dsh/skills/` in sync. |

Skill files must not contain tool-specific invocation syntax (see R-009); the README files document invocation for users.

New house-format rules use `### R-001 Title` headings with a normative statement, a Why line and a Check line. Existing VLSIT skills with a domain-specific namespace (for example `OCI-001` or `RHD-001`) may retain their established one-line rule entries; the validator checks their ID uniqueness, normative keyword, in-skill references, and possible overlaps without imposing the house-format Why/Check structure.

## Folder names inside a skill

Only `SKILL.md` is special. Codex documentation names the optional folders
`scripts/`, `reference/` and `assets/`; Claude Code documentation shows
`reference.md` files. These assistants do not require those names, because supporting files are
found through links in `SKILL.md`. The house format uses `reference/` (singular) and
`scripts/`, plus `rule.md`.

## Size and loading

- Keep `SKILL.md` under 500 lines (Claude Code guidance); the body stays in context
  after it loads.
- Claude Code re-attaches up to 5,000 tokens of an invoked skill after context
  compaction, so the most important instructions belong near the top.
- Link supporting files directly from `SKILL.md` and say when to read each one.
  Files reached through a chain of links may be read only in part.
