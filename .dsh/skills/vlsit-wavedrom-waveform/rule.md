# Rules

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Value Change Dump (VCD). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
These rules are mandatory every time this skill runs. When this file, SKILL.md and a file in `reference/` differ, this file wins.

Each rule is one checkable requirement. It has a permanent ID (R-NNN) that is never reused or renumbered, a statement that starts with MUST or MUST NOT, a Why line and a Check line. No two rules may repeat or contradict each other.

## General

### R-001 Report only verified results
MUST report a result as checked, tested or installed only when a command or an inspection in the current run confirmed it, and list everything that was not confirmed.
- Why: the user acts on the report, and an unverified claim costs more than an honest "not checked".
- Check: manual - every claim in the final report points to a command output or to a file that was read.

### R-002 Protect existing files
MUST ask the user before overwriting or deleting a file that this skill did not create in the current run.
- Why: the user may have edited the file by hand, and a silent overwrite destroys that work.
- Check: manual - no existing file changed without a recorded yes from the user.

## Drawing

### R-003 Bundled WaveDrom only
MUST draw waveforms only with the WaveDrom files in `assets/wavedrom/`, after `scripts/vlsit_wavedrom_waveform.py check` reports READY, with no WaveDrom or other script loaded from the network and no other drawing tool substituted.
- Why: the viewer then works offline and always renders the version whose checksum was recorded, so the user sees the same result on every machine.
- Check: `scripts/vlsit_wavedrom_waveform.py check`; the generated HTML contains no `src="http` reference.

### R-004 Ask instead of guessing
MUST ask the user whenever a signal name, group, order, value, timing, edge or annotation is missing, unreadable or ambiguous, and fill none of them with an assumption.
- Why: a waveform that looks plausible but differs from the real behavior is worse than a question, because the user will trust it.
- Check: manual - every unreadable or missing item in the transcription is either answered by the user or marked as unresolved in the report.

### R-005 Questions carry options
MUST give every question to the user at least two concrete options, each with a specific explanation of what it does and what it costs, end the set with an open choice where the user writes their own answer, put at most four questions in one message, and add a draft waveform or draft WaveJSON next to the questions when the request is short.
- Why: the user decides faster from visible alternatives and a concrete draft than from an open question, and the open choice covers needs the list missed.
- Check: manual - each question in the chat shows options with explanations and an open choice.

### R-006 VCD scope is the user's choice
MUST show the signal list and time range from `vcd-info` and ask the user to choose the whole file, a time window, or a list of signals or groups before converting a VCD file, leaving the choice of signals and window to the user.
- Why: a VCD file often holds hundreds of signals and a long run, and only the user knows which part explains the behavior.
- Check: manual - the user's choice appears in the chat before the `vcd-to-wavejson` command.

### R-007 Image fidelity and confirmation
MUST transcribe a waveform image into a table of groups, signal names in drawn order, per-cycle values, timing and edges, annotations and the time axis, obtain the user's confirmation of that table before the final drawing, and reproduce every one of those aspects that WaveDrom can express.
- Why: the user asked for an exact redraw, and a confirmed transcription separates reading errors from drawing errors.
- Check: manual - the table and the user's confirmation precede the final HTML; the report lists each difference from the original.

### R-008 Declared limits
MUST tell the user before drawing when the requested content cannot be expressed in WaveDrom (for example analog values, free-form shapes, or fractional cycles that need a different period) and propose the nearest drawable form instead of dropping the content silently.
- Why: a silent omission makes the redraw look complete while it is not.
- Check: manual - every unsupported item in the request appears in the chat with a proposed alternative.

## Output

### R-009 Strict WaveJSON checked before delivery
MUST write the WaveJSON as strict JSON and run `scripts/vlsit_wavedrom_waveform.py lint` on it with zero errors before building or delivering the HTML.
- Why: strict JSON loads in every tool and the check catches the errors that make WaveDrom draw nothing, such as a wave starting with `.` or edges naming missing nodes.
- Check: `scripts/vlsit_wavedrom_waveform.py lint FILE` prints PASS.

### R-010 Deliver both files
MUST deliver the `.json` file and the offline `.html` viewer built by `scripts/vlsit_wavedrom_waveform.py html`, state their full paths, and tell the user to open the HTML file in a browser.
- Why: the JSON is the editable source and the HTML lets the user inspect the result at once without installing anything.
- Check: `scripts/vlsit_wavedrom_waveform.py html` prints OK and the report names both paths.

### R-011 Ask before installing or using the network
MUST ask the user and wait for a yes before installing software, downloading a file or using the network.
- Why: these actions change the machine or send data out, and the user did not request them by asking for a waveform.
- Check: manual - no install or network command ran without a recorded yes.
