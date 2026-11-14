{
  "checker_id": "chk_data",
  "build_manifest_sha256": "<actual SHA-256>",
  "review": {
    "decision": "pending",
    "approver": "<named reviewer>",
    "date": "<YYYY-MM-DD>"
  },
  "tests": [
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
    }
  ]
}
