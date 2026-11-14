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
