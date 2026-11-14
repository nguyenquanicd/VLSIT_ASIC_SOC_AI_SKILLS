# Lint tools and installation

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-013, R-014, R-015). Read this when you run lint, read its output, or have to tell the designer how to get a tool.

## Tools the script uses

`vlsit_lint_rtl.py tools` lists what it finds. It looks in PATH and then in an OSS CAD Suite folder (`OSS_CAD_SUITE`, `C:\Tools\oss-cad-suite`, `~/oss-cad-suite`, `/opt/oss-cad-suite`).

| Tool | Role | What the script runs |
|---|---|---|
| verilator | full lint, first choice | `verilator --lint-only -Wall --top-module <top> <files>` |
| slang | full lint, second choice | `slang --top <top> -Wextra <files>` |
| yosys | elaboration only (not lint) | `read_verilog -sv ...; hierarchy -check -top <top>` |
| iverilog | elaboration only (not lint) | `iverilog -g2012 -t null -s <top> <files>` |

An elaboration-only run proves that the hierarchy builds. It is not lint, and the report must not call it lint.

On Windows the suite build of Verilator needs `VERILATOR_ROOT`; the script sets it. The `verilator` wrapper there is a Perl script, so the script runs `verilator_bin.exe` directly.

## Reading the output

Verilator exits with 1 even for warnings, so read the counts the script prints, not the exit code of the tool. The log file (`lint_<tool>.log`) holds the full output and the exact command.

Warnings that are often intentional in VLSIT RTL, to be fixed or justified one by one (R-013):

| Message | Typical cause | Usual decision |
|---|---|---|
| slang `useless-cast` on `$bits(x)'(...)` | the ARI-02 cast when the expression already has the width | justify: the rule requires the destination-width cast |
| Verilator `PINCONNECTEMPTY` | an unused output left as `()` | justify, or connect to a named `w_unused_*` signal |
| Verilator `UNUSEDSIGNAL`, `UNUSEDPARAM` | a port kept for the interface | justify with the specification section |
| Verilator `WIDTHEXPAND`, `WIDTHTRUNC` | a real width mistake | fix: never justify a width warning |
| Verilator `LATCH`, `MULTIDRIVEN`, `UNOPTFLAT` | a latch, two drivers, a combinational loop | fix: they break P7, P8, P23 |

## When no tool is found

The script prints the options for the operating system and exits with 3. Give the designer the options, with the trade-off of each, and wait for a choice. Do not install anything before a yes.

| Option | Needs | Advantage | Disadvantage |
|---|---|---|---|
| OSS CAD Suite | download of about 600 MB, no admin rights | all tools in one place, newest versions | large download |
| Package manager (Linux: apt, dnf, pacman, apk; macOS: brew) | root, except brew | small, updates with the system | older Verilator on some distributions |
| MSYS2 (Windows) | MSYS2 installed | smaller than the suite | extra shell to learn |
| WSL (Windows) | WSL with a Linux distribution | real Linux packages | a second environment |
| Conda (`conda-forge`) | Miniconda | no root | needs conda |
| Source build | compiler, time | full control | slowest |

While no tool exists: run the rule check, deliver the files, and write "lint not run" in the report together with the command the designer can run later.
