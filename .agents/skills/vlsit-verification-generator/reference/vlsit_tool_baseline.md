# Tool baseline guide

Guidance only; the mandatory requirements are in [rule.md](../rule.md). Read this file when recording the tools that a project uses.

## 1. Why a tool baseline

A verification result is only comparable when the tool stack is known. The same test can pass on one simulator version and fail on another, and a coverage number means little without the coverage tool and its options. The tool baseline is the record that makes a result reproducible.

## 2. What to record

| Tool class | What to record | Example |
|---|---|---|
| Simulator | Name, exact version, compile and run options | `questa 2026.1`, `-sv`, `+UVM_TESTNAME=...` |
| UVM library | Distribution and version | `Accellera UVM 2020-3.2` |
| Lint | Name and version | `verilator 5.036`, `slang 7.0` |
| Coverage | Tool, format and merge options | `urg`, UCIS XML |
| Formal | Tool and version | `jaspergold 2026.1`, `sby`, `vcformal` |
| Waveform | Format and viewer | VCD, FSDB, WLF |
| Python | Version used by the skill scripts | `3.12.10` |
| Operating system | Name and version | `Windows 11 24H2`, `Ubuntu 24.04` |

Record the exact version string that the tool prints, not a marketing name.

## 3. `tools.yaml`

Use `templates/vlsit_tools.yaml.tpl` as the starting point. A project file looks like:

```yaml
project: example_soc
updated: 2026-11-11
tools:
  simulator:
    name: questa
    version: "2026.1"
    compile_command: "vlog -sv -f filelist.f"
    run_command: "vsim -c -do run.do"
    coverage_command: "vcover merge -out merged.ucdb"
  uvm:
    name: accellera
    version: "2020-3.2"
  lint:
    name: verilator
    version: "5.036"
    command: "verilator --lint-only -Wall"
  formal:
    name: jaspergold
    version: "2026.1"
    command: "jg -batch"
  coverage:
    format: ucis
    merge_command: "vcover merge -out merged.ucdb"
  python:
    version: "3.12.10"
  os:
    name: "Windows 11"
    version: "24H2"
```

The Phase 1 regression and coverage scripts use this file through a small adapter: the script calls the command named here instead of hard-coding a vendor command. A missing tool is reported as `not run`; the skill does not install it without the user's agreement.

## 4. Discovery

The skill does not search the disk for proprietary tools. It reports what the project records and what is visible in `PATH` when a Phase 1 script asks. A safe discovery command list is:

```sh
command -v vcs xrun vsim verilator iverilog
command -v slang verilator
command -v urg vcover verilator_coverage
command -v jaspergold sby vcformal
```

On Windows PowerShell, use `Get-Command` with the same names. A tool found in `PATH` is not automatically approved for the project; the project owner confirms the version and the license.

## 5. Version pinning

- Pin the simulator, UVM library and VIP versions in every run manifest.
- Pin the Python version used by the skill scripts when a result depends on the script.
- Record the version of every third-party VIP and model.
- A version change is a change event: re-run the affected checks and create a new evidence bundle (R-116).

## 6. Missing tools

When a required tool is missing:

1. Report which check could not run and why.
2. Do not substitute a different tool without the user's agreement, because the result would not be comparable.
3. Do not install a tool without the user's agreement.
4. Record the gap in the final report as `not run`, never as `passed`.

## 7. Tool baseline review checklist

- Every tool has an exact version.
- The compile and run options are recorded.
- The UVM library and VIP versions are pinned.
- The coverage format and merge command are recorded.
- The formal tool and version are recorded when formal checks are required.
- The Python and OS versions are recorded.
- A version change has a re-run record.
