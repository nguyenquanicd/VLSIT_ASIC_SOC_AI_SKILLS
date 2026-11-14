{
  "producer_id": "producer",
  "implementation_sha256": "<actual SHA-256>",
  "review": {
    "decision": "pending",
    "approver": "<named reviewer>",
    "date": "<YYYY-MM-DD>"
  },
  "tests": [
    {
      "kind": "invalid_counter",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "rejected",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_invalid_counter.json",
        "sha256": "<actual SHA-256>"
      }
    },
    {
      "kind": "missing_bin",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "rejected",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_missing_bin.json",
        "sha256": "<actual SHA-256>"
      }
    },
    {
      "kind": "raw_failure",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "rejected",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_raw_failure.json",
        "sha256": "<actual SHA-256>"
      }
    },
    {
      "kind": "vacuity",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "rejected",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_vacuity.json",
        "sha256": "<actual SHA-256>"
      }
    },
    {
      "kind": "wrong_baseline",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "rejected",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_wrong_baseline.json",
        "sha256": "<actual SHA-256>"
      }
    },
    {
      "kind": "wrong_configuration",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "rejected",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_wrong_configuration.json",
        "sha256": "<actual SHA-256>"
      }
    }
  ]
}
