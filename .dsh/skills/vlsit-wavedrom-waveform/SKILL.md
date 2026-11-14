---
name: vlsit-wavedrom-waveform
description: Draw timing waveforms with the bundled offline WaveDrom from a short request, a VCD file (whole file or a time window) or a screenshot of a waveform, producing WaveJSON and a self-contained HTML viewer. Use when the user asks to draw, redraw, convert or check a waveform, timing diagram or VCD.
compatibility: Python 3.8 or later using the standard library only. Windows PowerShell 5.1 is used only to locate or install Python. Works offline; WaveDrom 3.7.0 (MIT licence) is bundled in assets/wavedrom and needs no Node.js. The HTML viewer needs any modern web browser.
---

# WaveDrom waveform

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Value Change Dump (VCD). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Turns a short request, a VCD file or a waveform image into WaveJSON and a self-contained HTML page that draws it with the bundled WaveDrom, so the user can open the result at once, offline. It asks the user about anything missing or unclear, with options and explanations, and it does not draw analog or free-form graphics.

Reply to the user in the language they use.

If instructions differ, follow them in this order: [rule.md](rule.md) first, then this file, then the files in `reference/`.

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely before doing anything else. Every rule in it is mandatory.

### 2. Find Python and check the bundle

Every script in `scripts/` is Python 3 and uses only the standard library. Locate a working Python before running any of them:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

On Linux or macOS run the twin script:

```sh
sh "<skill folder>/scripts/vlsit_find_python.sh"
```

It prints the full path of a working Python 3 (called `<python>` below) and exits 0, or prints `NOT FOUND` and exits 3. Do not continue without Python and do not guess a path. Tell the user that Python 3 is needed and let them choose: install it themselves from python.org, or let you install it with `vlsit_find_python.ps1 -Install` (uses winget). Run the install only after they agree, then run the locator again.

Then verify the bundled WaveDrom: `<python> "<skill folder>\scripts\vlsit_wavedrom_waveform.py" check` must print READY (exit 3 means a file is missing or changed; report it and stop).

### 3. Identify the source

Decide which input the user gave: a VCD file, a waveform image (screenshot or photo), or only a request in words. Ask for the file when the user mentions one that is not attached.

### 4. Turn the source into WaveJSON

- **Words only**: read [reference/vlsit_question_bank.md](reference/vlsit_question_bank.md), write a draft WaveJSON from the request using [reference/vlsit_wavejson_cheatsheet.md](reference/vlsit_wavejson_cheatsheet.md), show the draft with up to four questions with options (rule R-005) about what is missing, and revise after the answers.
- **VCD**: read [reference/vlsit_vcd_to_wavejson.md](reference/vlsit_vcd_to_wavejson.md). Run `vcd-info`, show the result, ask the user to choose the whole file, a time window or a signal list (rule R-006), then run `vcd-to-wavejson`.
- **Image**: read [reference/vlsit_image_to_wavejson.md](reference/vlsit_image_to_wavejson.md). Transcribe the image into the table, ask about every unreadable or ambiguous item, and get the user's confirmation of the table before writing the WaveJSON (rules R-004, R-007).

State anything WaveDrom cannot express and the nearest drawable form (rule R-008).

### 5. Check and build

```powershell
<python> "<skill folder>\scripts\vlsit_wavedrom_waveform.py" lint "<file>.json"
<python> "<skill folder>\scripts\vlsit_wavedrom_waveform.py" html "<file>.json" --title "<title>"
```

Fix every lint error and run it again; the HTML is built beside the JSON unless `--out` is given, and an existing file is not overwritten without `--force` (rule R-002).

### 6. Show the result and iterate

Tell the user the full paths of the `.json` and `.html` files and to open the HTML in a browser; the page has buttons to save SVG and PNG and to copy the WaveJSON. For an image source, compare the drawing with the original and list the differences (rule R-007). Apply the user's corrections by editing the JSON and rebuilding with `--force` on files this run created.

### 7. Verify against the rules

Check the result against every rule ID in [rule.md](rule.md): R-003 and R-009 by the script outputs, the others by inspection of the conversation and the files. Report which rules were verified and how, and say plainly what could not be verified.

## Reference

Read a file only when the step needs it.

| File | Read it when |
|---|---|
| [reference/vlsit_question_bank.md](reference/vlsit_question_bank.md) | Step 4, to word questions with options and to build a draft from a short request |
| [reference/vlsit_wavejson_cheatsheet.md](reference/vlsit_wavejson_cheatsheet.md) | Step 4, when writing or editing WaveJSON |
| [reference/vlsit_vcd_to_wavejson.md](reference/vlsit_vcd_to_wavejson.md) | Step 4 with a VCD file |
| [reference/vlsit_image_to_wavejson.md](reference/vlsit_image_to_wavejson.md) | Step 4 with a waveform image |

## Scripts

Run each script as `<python> "<skill folder>\scripts\<script>.py" <action>`.

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1` (Windows), `scripts/vlsit_find_python.sh` (Linux, macOS) | Before the first Python script, and again after Python was installed |
| `scripts/vlsit_wavedrom_waveform.py check` | Step 2: verify the bundled WaveDrom against `assets/vlsit_CHECKSUMS.txt` |
| `scripts/vlsit_wavedrom_waveform.py vcd-info` | Step 4 with a VCD file: list signals and time range |
| `scripts/vlsit_wavedrom_waveform.py vcd-to-wavejson` | Step 4 with a VCD file, after the user chose the scope |
| `scripts/vlsit_wavedrom_waveform.py lint` | Step 5: check the structure of the WaveJSON |
| `scripts/vlsit_wavedrom_waveform.py html` | Step 5: build the offline viewer |

## Assets

`assets/wavedrom/` holds the WaveDrom 3.7.0 library files (`wavedrom.unpkg.min.js`, `skins/default.js`, `LICENSE`, MIT licence, from the npm package `wavedrom`) and `assets/vlsit_CHECKSUMS.txt` lists their SHA-256 values. Do not edit these files.

## Output

The `.json` and `.html` files are saved beside the input file, or in the folder the user names; ask when there is no input file. Report the two full paths, the lint result, the rules verified, and the open items.
