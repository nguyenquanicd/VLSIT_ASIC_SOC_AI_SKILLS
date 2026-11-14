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
    "compile_options": ["-sv", "+incdir+src"],
    "run_options": ["+UVM_TESTNAME=t_vip_apb_write_0wait"],
    "vip_versions": {},
    "seed": 1,
    "timeout_s": 60
  },
  "test": "t_vip_apb_write_0wait",
  "result": {
    "compile": "pass",
    "simulation": "pass",
    "assertions": {
      "total": 42,
      "fired": 42,
      "failed": 0
    },
    "coverage": {
      "functional": "96.4%",
      "code": "91.2%"
    },
    "mutation": {
      "injected": 12,
      "killed": 10,
      "equivalent": 1,
      "survived": 1
    }
  },
  "artifacts": [
    {"path": "compile.log", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"},
    {"path": "sim.log", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"},
    {"path": "assertions.csv", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"},
    {"path": "coverage/merged.xml", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"},
    {"path": "mutation/report.md", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"},
    {"path": "review.md", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}
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
