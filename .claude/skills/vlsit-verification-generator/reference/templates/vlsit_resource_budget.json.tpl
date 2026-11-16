{
  "schema_version": 1,
  "status": "pending_review",
  "campaign_id": "<campaign identifier>",
  "measured_at": "<ISO-8601 timestamp>",
  "host": {
    "os": "<operating system and version>",
    "ram_total_bytes": null,
    "ram_available_bytes": null,
    "ram_status": "not_measured",
    "ram_measurement_reason": "<required when not_measured>",
    "disk_path_or_volume": "<simulation workspace volume>",
    "disk_free_bytes": null,
    "disk_status": "not_measured",
    "disk_measurement_reason": "<required when not_measured>",
    "measurement_method": "<native command or simulator tool and version>"
  },
  "limits": {
    "reserved_host_ram_bytes": null,
    "simulation_ram_budget_bytes": null,
    "max_concurrent_jobs": 1,
    "disk_stop_free_bytes": null,
    "expected_max_run_output_bytes": null,
    "output_estimation_method": "<prior measured run, bounded pilot, or reviewed tool estimate>"
  },
  "waveform_policy": {
    "default_capture": "only_when_required_by_test_or_review",
    "planned_signal_scope": "<signals or none>",
    "planned_time_windows": "<scenario-specific windows or none>",
    "failure_diagnostic": "rerun_same_configuration_and_seed_with_targeted_capture"
  },
  "compression": {
    "method": "<available lossless method or none>",
    "round_trip_hash_required": true
  },
  "review": {
    "reviewer": "<name>",
    "decision": "<approved, rejected or pending>",
    "record": "<review reference>"
  }
}
