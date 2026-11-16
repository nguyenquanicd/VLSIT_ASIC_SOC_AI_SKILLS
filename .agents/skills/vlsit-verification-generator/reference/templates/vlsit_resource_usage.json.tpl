{
  "schema_version": 1,
  "run_id": "<run identifier>",
  "budget": "env/resource_budget.json",
  "simulation_jobs": 1,
  "ram": {
    "peak_bytes": null,
    "measurement_method": "<native command or simulator metric>",
    "status": "not_measured",
    "reason": "<required when not_measured>"
  },
  "disk": {
    "free_before_bytes": null,
    "free_after_bytes": null,
    "expected_output_bytes": null,
    "run_output_bytes": null,
    "measurement_method": "<native command or script>",
    "status": "not_measured",
    "reason": "<required when not_measured>"
  },
  "waveform": {
    "status": "not_captured",
    "reason": "<why no waveform was needed, or capture result>",
    "signal_scope": "<signals or none>",
    "time_window": "<time window or none>",
    "paths": []
  },
  "compression": {
    "status": "not_used",
    "method": "",
    "original_sha256": "",
    "archive_sha256": "",
    "round_trip_verified": false
  }
}
