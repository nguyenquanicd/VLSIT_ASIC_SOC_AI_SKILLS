{
  "artifact_id": "vc_apb_master_driver",
  "artifact_path": "verification/01_component/vc_apb_master_driver/vc_apb_master_driver.sv",
  "artifact_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "model": {
    "provider": "example",
    "id": "example-coder",
    "version": "2026-10",
    "temperature": 0.2,
    "seed": 1
  },
  "prompt": {
    "template_id": "component_driver_v1",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "context_files": [
      {
        "path": "spec/APB.md",
        "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
      }
    ],
    "spec_ids": ["REQ-APB-001", "REQ-APB-002"],
    "protocol_clauses": ["APB 4.1", "APB 4.2"]
  },
  "tool_runs": [
    {
      "command": "compile",
      "version": "questa-2026.1",
      "result": "pass",
      "log": "compile.log"
    },
    {
      "command": "simulate",
      "version": "questa-2026.1",
      "result": "pass",
      "log": "sim.log"
    }
  ],
  "validation": {
    "compile": "pass",
    "simulation": "pass",
    "assertions": {
      "total": 12,
      "fired": 12,
      "failed": 0
    },
    "mutation": {
      "injected": 6,
      "killed": 5,
      "equivalent": 1,
      "survived": 0
    },
    "coverage": {
      "functional": "92.0%"
    }
  },
  "review": {
    "reviewer": "dv_lead",
    "date": "2026-11-11",
    "decision": "approved_with_changes",
    "notes": "Renamed two signals and added a reset check."
  }
}
