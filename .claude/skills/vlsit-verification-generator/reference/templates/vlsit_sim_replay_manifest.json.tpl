{
  "schema_version": 2,
  "configuration": "<configuration ID>",
  "test": "<test ID>",
  "top": "<simulation top>",
  "seed": 1,
  "environment": [
    {
      "name": "SIM_ROOT",
      "purpose": "<purpose and setup order>",
      "required": true,
      "secret": false,
      "value": "<effective non-secret value>",
      "source": "<setup script or explicit configuration>",
      "setup_order": 0,
      "override": "<override precedence>"
    }
  ],
  "tools": [
    {
      "name": "<simulator or compiler>",
      "version_argv": [
        "<tool executable>",
        "<version option>"
      ],
      "status": "not_run",
      "reason": "<why not measured yet>"
    }
  ],
  "commands": [
    {
      "name": "compile",
      "stage": "compile",
      "argv": [
        "<exact executable>",
        "<exact argument>"
      ],
      "cwd": "runs/run_001/build",
      "environment": [
        "SIM_ROOT"
      ],
      "timeout_s": 300,
      "status": "not_run",
      "reason": "<execution pending>"
    },
    {
      "name": "simulate",
      "stage": "simulate",
      "argv": [
        "<exact executable>",
        "<exact argument>"
      ],
      "cwd": "runs/run_001/build",
      "environment": [
        "SIM_ROOT"
      ],
      "timeout_s": 300,
      "status": "not_run",
      "reason": "<execution pending>"
    },
    {
      "name": "replay",
      "stage": "replay",
      "argv": [
        "<exact executable>",
        "<exact argument>"
      ],
      "cwd": "runs/run_001/build",
      "environment": [
        "SIM_ROOT"
      ],
      "timeout_s": 300,
      "status": "not_run",
      "reason": "<execution pending>"
    }
  ],
  "cold_replay": {
    "status": "not_run",
    "reason": "Execution outcomes belong to helper-generated per-run receipts, never handwritten success here."
  },
  "external_dependencies": [],
  "environment_policy": {
    "mode": "isolated",
    "empty_reason": "<required only if no variables are needed>"
  },
  "dependency_export": "env/build_inputs.json",
  "replay_plan": {
    "runner": "scripts/project_runner.py",
    "compile": {
      "argv": [
        "<absolute executable>",
        "{snapshot}/scripts/project_runner.py",
        "compile",
        "{run}"
      ],
      "timeout_s": 300
    },
    "simulate": {
      "argv": [
        "<absolute executable>",
        "{snapshot}/scripts/project_runner.py",
        "simulate",
        "{run}"
      ],
      "timeout_s": 300
    },
    "build_outputs": [
      "build/simulator.bin"
    ],
    "result": "reports/result.json",
    "expected_cases": [
      "<reviewed test case ID>"
    ],
    "result_producer": {
      "status": "pending",
      "reviewer": "<named reviewer and qualification reference>",
      "scope": "rtl",
      "evidence": "docs/result_producer_qualification.md"
    }
  }
}
