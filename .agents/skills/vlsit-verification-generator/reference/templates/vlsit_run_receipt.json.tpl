{
  "schema_version": 2,
  "producer_id": "producer",
  "run": {
    "id": "run",
    "test": "t_combined",
    "configuration": "cfg",
    "seed": 7,
    "tool": "<tool and exact version>",
    "command": "<actual command>",
    "baseline": {
      "specification": "<actual SHA-256>",
      "rtl_manifest": "<actual SHA-256>"
    },
    "configuration_sha256": "<actual SHA-256>",
    "contract_sha256": "<actual SHA-256>",
    "build": {
      "top": "dut",
      "files": [
        {
          "path": "dut.sv",
          "sha256": "<actual SHA-256>",
          "role": "rtl"
        },
        {
          "path": "tb.sv",
          "sha256": "<actual SHA-256>",
          "role": "verification"
        },
        {
          "path": "model.py",
          "sha256": "<actual SHA-256>",
          "role": "model"
        },
        {
          "path": "filelist.f",
          "sha256": "<actual SHA-256>",
          "role": "filelist"
        },
        {
          "path": "producer.py",
          "sha256": "<actual SHA-256>",
          "role": "verification"
        }
      ],
      "parameters": {},
      "defines": {},
      "options": [
        "selftest"
      ]
    },
    "compile": "not_run",
    "result": "not_run",
    "exit_code": null,
    "obligations": [
      "OB-001",
      "OB-002",
      "OB-003",
      "OB-004",
      "OB-005",
      "OB-006",
      "OB-007"
    ],
    "checks": {
      "chk_data": {
        "status": "not_run",
        "comparisons": 0,
        "mismatches": 0,
        "pending": 0,
        "expected": 0,
        "observed": 0,
        "cancelled": 0
      }
    },
    "bins": [],
    "assertions": [
      {
        "id": "a_stable",
        "status": "not_run",
        "attempts": 0,
        "completed": 0,
        "antecedent_hits": 0,
        "failures": 0,
        "pending": 0,
        "disabled": 0,
        "cancelled": 0
      }
    ],
    "metric_hits": {
      "functional": [],
      "assertion": [],
      "code": [],
      "mutation": []
    }
  },
  "raw_artifacts": [
    {
      "path": "compile.log",
      "sha256": "<actual SHA-256>",
      "role": "compile_log"
    },
    {
      "path": "sim.log",
      "sha256": "<actual SHA-256>",
      "role": "simulation_log"
    }
  ]
}
