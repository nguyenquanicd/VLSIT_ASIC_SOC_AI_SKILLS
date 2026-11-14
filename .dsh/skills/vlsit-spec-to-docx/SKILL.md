---
name: vlsit-spec-to-docx
description: Convert a Markdown design specification into a filled copy of the VLSIT IP Microarchitecture Specification DOCX template, asking the user for every missing fact and never inventing content. Use when the user asks to turn a spec, or the current design specification, into the DOCX template format.
compatibility: Python 3.8 or later. python-docx and lxml are required for filling; Pillow and PyMuPDF are optional; LibreOffice renders the result. Windows or Linux, offline. Dependencies are checked when needed; nothing is installed without the user's approval.
---

# Specification to DOCX template

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Synopsys Design Constraints (timing context) (SDC); Clock-Domain Crossing (CDC); Application-Specific Integrated Circuit (ASIC); Advanced Peripheral Bus (APB); System on Chip (SoC). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Turn a Markdown design specification into a filled copy of the VLSIT IP Microarchitecture
Specification DOCX template. The source specification stays the technical authority; this skill
does not invent a value, a waveform, or a constraint that the source, a reference RTL file, or a
user answer does not provide.

**Precedence:** [rule.md](rule.md) overrides this file, and this file overrides the files under
`reference/`, when they differ.

**Reply language:** reply to the user in the language the user writes; the document itself is
professional English (R-006).

## What the run produces

| Output | Content |
|---|---|
| `<source>_updated.md` | the source specification plus the answers and RTL-derived facts, each marked `[added: <source>, <date>]` (R-004) |
| `content.json` | the section-by-section content in the schema of [reference/vlsit_content_schema.md](reference/vlsit_content_schema.md) |
| `<IP>_Design_Specification.docx` | the filled template |
| drawn figure files (optional) | a `.drawio` or WaveJSON source plus its raster export, when the user asked for a missing figure to be drawn (step 9b) |
| `run_report.md` | inventory, gap list, decisions, verification results, figure provenance |

The template and two worked examples ship with the skill:
`reference/vlsit_spec_template.docx` (the format template),
`reference/vlsit_content_example.json` (a fragment showing every content block type), and
`reference/vlsit_example/` (one complete APB4-to-TL-UL run: input specification, validated content,
filled DOCX, and run report). Read the example README before the first real run.

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) in full before doing anything else. Step 11 checks the result by rule ID.

### 2. Find Python

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

```sh
sh "<skill folder>/scripts/vlsit_find_python.sh"
```

It prints the path of a working Python 3.8 or later, or `NOT FOUND` with exit code 3. If Python
is missing, stop and let the user choose between installing it themselves and approving the
installer (`-Install` / `--install`).

The `docx` and `lxml` packages are needed by the fill step only. Check them with
`<python> -c "import docx"`; when absent, ask the user before installing (`pip install python-docx`)
— the user may prefer another machine or another tool. `Pillow` is optional and is needed only
to crop a block diagram (step 9).

### 3. Take the input

Ask the user for the specification file, or for the folder that holds it, when the request does
not name one (R-001). Then inventory the folder — specification Markdown, `figures/`,
`waveforms/`, `research/`, `rtl/`, `verification/` — and read the companion files that matter
before asking anything. Write the inventory into `run_report.md`.

If the user gives only a folder with several specifications, ask which one is the subject.

### 4. Probe the template

```powershell
<python> "<skill folder>\scripts\vlsit_template_probe.py" "reference\vlsit_spec_template.docx" --out template_map.json
```

It prints the fourteen sections, the paragraphs styled `Guidance`, the table captions, and the
figure placeholders, and writes the same data as JSON. Read
[reference/vlsit_template_contract.md](reference/vlsit_template_contract.md) for what each
section must contain. Use the same probe on a user-supplied template when the user has one.

### 5. Scan the source and map it

```powershell
<python> "<skill folder>\scripts\vlsit_spec_scan.py" "<source.md>" --out gaps.json --folder "<input folder>"
```

It extracts the heading tree, the requirement IDs, the tables, and the assets, maps each source
section onto the fourteen template sections, and writes `gaps.json` plus a short report: which
template section has no source, which one has source but no figure, and which mandatory element
(SDC, software flow, waveform, worked example) is absent.

Read [reference/vlsit_spec_mapping.md](reference/vlsit_spec_mapping.md) when a mapping is
ambiguous — one source section may feed two template sections, and the reverse.

### 6. Ask the gaps, or ask for RTL

Ask the user about every gap in at most four questions per round and two rounds, with concrete
questions ("Section 9 SDC lists a 400 MHz target; is the period 2.5 ns, and which I/O delay
applies to `PADDR`?"). When the gap is behavioural and the user has RTL, ask for the RTL files
and read them (R-003); never modify them.

Record every answer and every RTL-derived fact in `<source-name>_updated.md` (R-004), then
re-scan the updated file. Do not proceed while a required section is unresolved.

### 7. Write the content

Author `content.json` against [reference/vlsit_content_schema.md](reference/vlsit_content_schema.md),
using [reference/vlsit_writing_guide.md](reference/vlsit_writing_guide.md) for the required
elements of each section and the house prose style. Start from
`reference/vlsit_content_example.json` to see the file format.

Then validate it:

```powershell
<python> "<skill folder>\scripts\vlsit_content_check.py" content.json --source "<source>_updated.md" --template template_map.json
```

Fix every `ERROR` and read every `WARN`. A section that is genuinely not applicable is written
as `{"status": "na", "reason": "<why>", "confirmed_by_user": true}` (R-005).

### 8. Show the plan and get approval

Present one compact table — template section, source of the content, figure, open items — and
ask for approval before the document is written. The document is a controlled artefact, so an
unapproved structural mistake would be copied into every later revision.

### 9. Prepare the figures, or draw a missing one

**9a — an existing asset.** Run:

```powershell
<python> "<skill folder>\scripts\vlsit_figure_prepare.py" "<figure image>" --out "<figures out folder>" --crop-mode auto
```

It copies the asset, or crops the drawing out of an image that also carries the draw.io
description tables and legend (R-012), and prints the crop box. Show the result to the user and
get approval before it is inserted. When the crop is uncertain, ask the user to export a
diagram-only image instead of guessing.

**9b — no asset exists.** Ask whether the user wants the figure drawn (R-018) and stop until the
answer arrives. When the answer is yes, read
[reference/vlsit_figure_methods.md](reference/vlsit_figure_methods.md) and follow it: a block or
function diagram uses the VLSIT draw.io library and its spec-JSON generator from the sibling
hierarchy-diagram skill (R-020), a timing figure uses WaveJSON for the bundled WaveDrom (R-021),
each drawing is validated with its native checker and shown for approval (R-022), and only a raster
image is inserted into the document (R-023). A public reference figure may be used only under
R-024. When the answer is no, record the section that stays without a figure.

### 10. Fill, then verify

```powershell
<python> "<skill folder>\scripts\vlsit_docx_fill.py" --template "reference\vlsit_spec_template.docx" --content content.json --out "<IP>_Design_Specification.docx"
<python> "<skill folder>\scripts\vlsit_docx_check.py" "<IP>_Design_Specification.docx" --template-map template_map.json
<python> "<skill folder>\scripts\vlsit_docx_render.py" "<IP>_Design_Specification.docx" --out "<pages folder>"
```

`vlsit_docx_fill.py` refuses to overwrite an existing file without `--force` (R-014). Fix content
in `content.json` and re-run; never edit the DOCX.

`vlsit_docx_render.py` needs LibreOffice; when it is not installed it exits with a clear message.
Then ask the user whether to install LibreOffice or to accept structure-only verification, and
say so in the report (R-015). Inspect the rendered pages for table overflow, clipped figures and
broken page breaks.

### 11. Verify against the rules and report

Check every rule ID of [rule.md](rule.md): R-013 and R-015 through the script results above, the
rest by reading the output and the run report. Then report, in the user's language: the input
used, the gaps and how each was answered, the files written, the `RESULT` lines of the three
checks, which pages were inspected, and what remains untested.

## Scripts

| Script | Read or run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `scripts/vlsit_find_python.sh` | Step 2, and after a Python install |
| [`scripts/vlsit_template_probe.py`](scripts/vlsit_template_probe.py) | Step 4: list the sections, guidance paragraphs, table captions and figure placeholders of a template |
| [`scripts/vlsit_spec_scan.py`](scripts/vlsit_spec_scan.py) | Step 5: map the source specification to the template and list the gaps |
| [`scripts/vlsit_content_check.py`](scripts/vlsit_content_check.py) | Step 7 and after any edit of `content.json` |
| [`scripts/vlsit_figure_prepare.py`](scripts/vlsit_figure_prepare.py) | Step 9: copy or crop a figure and report the crop box |
| [`scripts/vlsit_docx_fill.py`](scripts/vlsit_docx_fill.py) | Step 10: fill the template from `content.json` |
| [`scripts/vlsit_docx_check.py`](scripts/vlsit_docx_check.py) | Step 10: verify the produced document structurally |
| [`scripts/vlsit_docx_render.py`](scripts/vlsit_docx_render.py) | Step 10: render the document to PDF and page images |

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_template_contract.md](reference/vlsit_template_contract.md) | Step 4 and step 8: what each of the fourteen sections must contain |
| [reference/vlsit_spec_mapping.md](reference/vlsit_spec_mapping.md) | Step 5: mapping the VLSIT specification sections onto the template |
| [reference/vlsit_content_schema.md](reference/vlsit_content_schema.md) | Step 7: the format of `content.json` |
| [reference/vlsit_writing_guide.md](reference/vlsit_writing_guide.md) | Step 7: required elements and prose style per section |
| [reference/vlsit_figure_methods.md](reference/vlsit_figure_methods.md) | Step 9b: how to draw a missing block diagram or waveform, validate it, and get a raster the document can hold |
| [reference/vlsit_spec_template.docx](reference/vlsit_spec_template.docx) | The format template itself; copy it, never edit it in place |
| [reference/vlsit_content_example.json](reference/vlsit_content_example.json) | A worked `content.json` fragment showing every block type |
| [reference/vlsit_example/vlsit_example_readme.md](reference/vlsit_example/vlsit_example_readme.md) | Read before the first real run: example contents, limits, and reproduction steps |
| [reference/vlsit_example/vlsit_example_spec.md](reference/vlsit_example/vlsit_example_spec.md) | Input of the worked example |
| [reference/vlsit_example/vlsit_example_content.json](reference/vlsit_example/vlsit_example_content.json) | Validated structured content of the worked example |
| [reference/vlsit_example/vlsit_example_output.docx](reference/vlsit_example/vlsit_example_output.docx) | Filled DOCX output of the worked example |
| [reference/vlsit_example/vlsit_example_run_report.md](reference/vlsit_example/vlsit_example_run_report.md) | Run report of the worked example |

## Environment

Python 3.8 or later. `python-docx` and `lxml` are required for filling the template. `Pillow` is
optional for figure cropping; `PyMuPDF` is optional for page images; LibreOffice renders the
result for layout review. Check each dependency only when its feature is needed, and ask before
installing anything. No network access is needed at run time.

Drawing a missing figure (step 9b) uses the sibling skills `vlsit-rtl-hierarchy-diagram` (library,
spec-JSON generator, validators) and `vlsit-wavedrom-waveform` (bundled WaveDrom, lint, viewer),
installed beside this skill. When they are absent, tell the user and ask whether to install them or
to leave the section without a figure.
