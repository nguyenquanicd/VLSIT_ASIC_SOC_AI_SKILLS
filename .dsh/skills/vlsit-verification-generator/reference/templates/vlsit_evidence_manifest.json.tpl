{
  "project": "example_soc",
  "level": "vip",
  "artifact": "vip_apb_master",
  "version": "1.0.0",
  "spec": {
    "path": "spec/APB.md",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "tools": {
    "simulator": "questa",
    "simulator_version": "2026.1",
    "uvm": "2020-3.2",
    "os": "Windows 11 24H2",
    "compile_options": [
      "-sv",
      "+incdir+src"
    ],
    "run_options": [
      "+UVM_TESTNAME=t_vip_apb_write_0wait"
    ],
    "vip_versions": {},
    "seed": 1,
    "timeout_s": 60,
    "no_vip_reason": ""
  },
  "test": "t_vip_apb_write_0wait",
  "result": {
    "compile": "not_run",
    "simulation": "not_run",
    "assertions": {
      "total": 0,
      "fired": 0,
      "failed": 0
    },
    "coverage": {
      "functional": "not_measured"
    },
    "mutation": {}
  },
  "artifacts": [
    {
      "path": "compile.log",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "path": "sim.log",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "path": "assertions.csv",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "path": "coverage/merged.xml",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "path": "mutation/report.md",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "path": "review.md",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "ai": {
    "used": false,
    "provenance": "",
    "artifacts": []
  },
  "review": {
    "reviewer": "dv_lead",
    "date": "2026-11-11",
    "decision": "approved"
  }
}
