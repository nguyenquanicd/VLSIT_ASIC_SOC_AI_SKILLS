{
  "name": "vip_apb_master",
  "version": "1.0.0",
  "protocol": {
    "name": "APB",
    "version": "AMBA APB",
    "clauses": ["4.1", "4.2", "4.3"]
  },
  "roles": ["master"],
  "parameters": {
    "address_width": 32,
    "data_width": 32,
    "max_wait_states": 16
  },
  "active_passive": ["active", "passive"],
  "files": [
    "src/vip_apb_master_pkg.sv",
    "src/vc_apb_master_driver.sv",
    "src/vc_apb_master_monitor.sv",
    "src/vc_apb_master_agent.sv"
  ],
  "dependencies": [
    {"name": "uvm", "version": "2020-3.2"}
  ],
  "tests": [
    "t_vip_apb_write_0wait",
    "t_vip_apb_read_wait",
    "t_vip_apb_write_error",
    "t_vip_apb_reset_mid_transfer",
    "t_vip_apb_backpressure"
  ],
  "coverage": [
    "cg_apb_protocol",
    "cg_apb_error"
  ],
  "scoreboard_hooks": [
    "apb_predictor",
    "apb_scoreboard_export"
  ],
  "simulators": [
    {"name": "questa", "version": "2026.1"}
  ],
  "license": "internal",
  "owner": "dv_apb",
  "integration_example": "docs/vip_apb_master_ug.md",
  "known_limitations": [
    "Does not model PSLVERR in the same cycle as PSEL rising."
  ]
}
