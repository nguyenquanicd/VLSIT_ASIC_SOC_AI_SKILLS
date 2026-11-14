# Regression testlist. One testlist is the source of regression scope (R-215).
# test_type uses the same vocabulary as the vplan (R-250 to R-253):
# directed, constrained_random, combined, fault_injection, formal, stress,
# use_case, boot, compliance, regression.
tiers:
  smoke:
    timeout_s: 600
    pass_criteria: "All selected tests pass and no assertion is vacuous."
  nightly:
    timeout_s: 14400
    pass_criteria: "All selected tests pass; known failures are quarantined with a bug ID."
  full:
    timeout_s: 28800
    pass_criteria: "All tests run, coverage is merged, and every failure is triaged."

tests:
  - id: t_vip_apb_write_0wait
    level: vip
    vplan_req: REQ-APB-001
    testbench: vip_apb_master
    test: apb_write_0wait
    test_type: directed
    combines: []
    seed: 1
    timeout_s: 60
    tier: smoke
    owner: dv_apb
    expected: pass
    evidence: ev_vip_apb_0007

  - id: t_vc_apb_random
    level: component
    vplan_req: REQ-APB-004
    testbench: vc_apb_master_selftest
    test: apb_random
    test_type: constrained_random
    combines: []
    constraints_source: "APB 4.1 setup phase, APB 4.2 access phase; address and data random, wait states 0..15"
    seed: 2
    timeout_s: 120
    tier: nightly
    owner: dv_apb
    expected: pass
    evidence: ""

  - id: t_vblk_dma_desc
    level: block
    vplan_req: REQ-DMA-001
    testbench: vblk_dma_env
    test: dma_desc
    test_type: combined
    combines: [descriptor_fetch, data_move]
    seed: 3
    timeout_s: 300
    tier: nightly
    owner: dv_dma
    expected: pass
    evidence: ""

  - id: t_vblk_dcls_fault_inject
    level: block
    vplan_req: REQ-SAFE-001
    testbench: vblk_dcls_env
    test: dcls_fault_inject
    test_type: fault_injection
    combines: [lockstep_compare, error_response]
    fault: "inject a data mismatch into core1 through the compare-path fault hook"
    expected_response: "dcls_error asserted within two cycles and the error interrupt raised"
    seed: 4
    timeout_s: 300
    tier: full
    owner: dv_safety
    expected: pass
    evidence: ""

  - id: t_vsoc_boot
    level: soc
    vplan_req: REQ-SOC-001
    testbench: vsoc_small_env
    test: boot
    test_type: boot
    combines: [boot_from_rom, peripheral_enumeration]
    seed: 1
    timeout_s: 900
    tier: nightly
    owner: dv_soc
    expected: pass
    evidence: ""
