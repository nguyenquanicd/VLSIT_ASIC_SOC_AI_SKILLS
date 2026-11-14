{
  "schema_version": 2,
  "baseline": {
    "specification": {
      "path": "spec.md",
      "sha256": "<actual SHA-256>"
    },
    "rtl_manifest": {
      "path": "rtl_manifest.json",
      "sha256": "<actual SHA-256>"
    }
  },
  "configurations": [
    "cfg"
  ],
  "scope_matrix": {
    "path": "scope_matrix.json",
    "sha256": "<actual SHA-256>"
  },
  "obligations": [
    {
      "id": "OB-001",
      "req_id": "REQ-1",
      "configuration": "cfg",
      "dimension": "backpressure",
      "checks": [
        "chk_data"
      ],
      "bins": [
        "cg_backpressure"
      ],
      "assertions": [
        {
          "id": "a_stable",
          "kind": "implication"
        }
      ]
    },
    {
      "id": "OB-002",
      "req_id": "REQ-1",
      "configuration": "cfg",
      "dimension": "boundary",
      "checks": [
        "chk_data"
      ],
      "bins": [
        "cg_boundary"
      ],
      "assertions": [
        {
          "id": "a_stable",
          "kind": "implication"
        }
      ]
    },
    {
      "id": "OB-003",
      "req_id": "REQ-1",
      "configuration": "cfg",
      "dimension": "concurrency",
      "checks": [
        "chk_data"
      ],
      "bins": [
        "cg_concurrency"
      ],
      "assertions": [
        {
          "id": "a_stable",
          "kind": "implication"
        }
      ]
    },
    {
      "id": "OB-004",
      "req_id": "REQ-1",
      "configuration": "cfg",
      "dimension": "error",
      "checks": [
        "chk_data"
      ],
      "bins": [
        "cg_error"
      ],
      "assertions": [
        {
          "id": "a_stable",
          "kind": "implication"
        }
      ]
    },
    {
      "id": "OB-005",
      "req_id": "REQ-1",
      "configuration": "cfg",
      "dimension": "normal",
      "checks": [
        "chk_data"
      ],
      "bins": [
        "cg_normal"
      ],
      "assertions": [
        {
          "id": "a_stable",
          "kind": "implication"
        }
      ]
    },
    {
      "id": "OB-006",
      "req_id": "REQ-1",
      "configuration": "cfg",
      "dimension": "recovery",
      "checks": [
        "chk_data"
      ],
      "bins": [
        "cg_recovery"
      ],
      "assertions": [
        {
          "id": "a_stable",
          "kind": "implication"
        }
      ]
    },
    {
      "id": "OB-007",
      "req_id": "REQ-1",
      "configuration": "cfg",
      "dimension": "reset",
      "checks": [
        "chk_data"
      ],
      "bins": [
        "cg_reset"
      ],
      "assertions": [
        {
          "id": "a_stable",
          "kind": "implication"
        }
      ]
    }
  ],
  "checkers": [
    {
      "id": "chk_data",
      "kind": "scoreboard",
      "minimum_comparisons": 1,
      "model_id": "oracle",
      "qualification": {
        "path": "checker_qualification.json",
        "sha256": "<actual SHA-256>"
      }
    }
  ],
  "models": [
    {
      "id": "oracle",
      "contract": {
        "path": "model_contract.json",
        "sha256": "<actual SHA-256>"
      }
    }
  ],
  "producers": [
    {
      "id": "producer",
      "implementation": {
        "path": "producer.py",
        "sha256": "<actual SHA-256>"
      },
      "qualification": {
        "path": "producer_qualification.json",
        "sha256": "<actual SHA-256>"
      }
    }
  ],
  "metric_policy": [
    {
      "configuration": "cfg",
      "family": "functional",
      "applicable": true
    },
    {
      "configuration": "cfg",
      "family": "code",
      "applicable": true
    },
    {
      "configuration": "cfg",
      "family": "assertion",
      "applicable": true
    },
    {
      "configuration": "cfg",
      "family": "mutation",
      "applicable": true
    }
  ],
  "metrics": [
    {
      "id": "functional",
      "configuration": "cfg",
      "family": "functional",
      "scope": "<approved metric scope and source catalog>",
      "total": 7,
      "bin_ids": [
        "cg_backpressure",
        "cg_boundary",
        "cg_concurrency",
        "cg_error",
        "cg_normal",
        "cg_recovery",
        "cg_reset"
      ],
      "target_percent": 100
    },
    {
      "id": "assertion",
      "configuration": "cfg",
      "family": "assertion",
      "scope": "<approved metric scope and source catalog>",
      "total": 1,
      "bin_ids": [
        "a_stable"
      ],
      "target_percent": 100
    },
    {
      "id": "code",
      "configuration": "cfg",
      "family": "code",
      "scope": "<approved metric scope and source catalog>",
      "total": 1,
      "bin_ids": [
        "line_1"
      ],
      "target_percent": 100
    },
    {
      "id": "mutation",
      "configuration": "cfg",
      "family": "mutation",
      "scope": "<approved metric scope and source catalog>",
      "total": 1,
      "bin_ids": [
        "fault_1"
      ],
      "target_percent": 100
    }
  ],
  "approval": {
    "path": "approval.json",
    "sha256": "<actual SHA-256>"
  }
}
