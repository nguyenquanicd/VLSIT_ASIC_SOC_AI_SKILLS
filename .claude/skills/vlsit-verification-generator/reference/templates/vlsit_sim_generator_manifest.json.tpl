{
  "schema_version": 1,
  "status": "pending",
  "generators": [
    {
      "purpose": "testcases",
      "name": "<generator name>",
      "version_or_sha256": "<version or source hash>",
      "argv": [
        "<exact executable>",
        "<generator script>",
        "<configuration>"
      ],
      "cwd": "<sim-relative working directory>",
      "inputs": [
        {
          "path": "<requirements/vplan/config/template>",
          "sha256": "<input hash>"
        }
      ],
      "linked_ids": [
        "<REQ-ID or scenario ID>"
      ],
      "outputs": [
        {
          "path": "tests/generated/<file>",
          "sha256": "<output hash>"
        }
      ],
      "log": "runs/<run_id>/generation.log",
      "reviewer": "<reviewer>"
    },
    {
      "purpose": "environment_components",
      "name": "<generator name>",
      "version_or_sha256": "<version or source hash>",
      "argv": [
        "<exact executable>",
        "<generator script>",
        "<configuration>"
      ],
      "cwd": "<sim-relative working directory>",
      "inputs": [
        {
          "path": "<protocol/interface/model contract/template>",
          "sha256": "<input hash>"
        }
      ],
      "linked_ids": [
        "<interface or requirement ID>"
      ],
      "outputs": [
        {
          "path": "env/generated/<file>",
          "sha256": "<output hash>"
        }
      ],
      "log": "runs/<run_id>/generation.log",
      "reviewer": "<reviewer>"
    }
  ],
  "reproducibility": {
    "mode": "clean_copy",
    "command": [
      "<exact regeneration command>"
    ],
    "overwrite_protection": "<how existing outputs are protected>",
    "check_or_diff_command": [
      "<exact check/diff command>"
    ],
    "review_status": "pending"
  }
}
