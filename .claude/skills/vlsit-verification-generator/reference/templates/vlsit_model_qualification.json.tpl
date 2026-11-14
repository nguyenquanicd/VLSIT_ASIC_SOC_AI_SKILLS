{
  "model_id": "oracle",
  "build_manifest_sha256": "<actual SHA-256>",
  "review": {
    "decision": "pending",
    "approver": "<named reviewer>",
    "date": "<YYYY-MM-DD>"
  },
  "tests": [
    {
      "kind": "boundary",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "match",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_boundary.json",
        "sha256": "<actual SHA-256>"
      }
    },
    {
      "kind": "fault_detection",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "detected",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_fault_detection.json",
        "sha256": "<actual SHA-256>"
      }
    },
    {
      "kind": "known_answer",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "match",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_known_answer.json",
        "sha256": "<actual SHA-256>"
      }
    },
    {
      "kind": "negative",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "handled",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_negative.json",
        "sha256": "<actual SHA-256>"
      }
    },
    {
      "kind": "reset",
      "status": "not_run",
      "command": "<actual qualification command>",
      "exit_code": null,
      "expected": "match",
      "observed": "<actual observed outcome>",
      "evidence": {
        "path": "qualification_reset.json",
        "sha256": "<actual SHA-256>"
      }
    }
  ]
}
