/*
 * Project      : VLSI Technology - AI RTL generator
 * Author       : Nguyen Quan and Claude (user)
 * AI Flow      : VLSIT RTL Generator AI Automation Flow
 * AI Flow Page : https://github.com/nguyenquanicd/VLSIT_RTL_Generator_AI_Model
 * Date         : 2026-10-18
 * Description  : Example of a Mealy FSM in three parts: a sequential process for the current
 *                state, a combinational process for the next state and one for the outputs. The
 *                outputs depend on the current state and on the inputs of the same cycle.
 */
`timescale 1ns/1ps

module m_mealy_fsm_example (
  // Clock and reset
  input  wire  i_clk_core,
  input  wire  i_rst_n_core,

  // Transfer request
  input  wire  i_start,
  input  wire  i_ready,
  input  wire  i_last,

  // Status and control
  output logic o_busy,
  output logic o_load_en,
  output logic o_send_valid,
  output logic o_done
);

  // FSM states: IDLE waits for i_start and SEND offers one item at a time until the last one is
  // accepted. Both encodings of the 1-bit state are used; default recovers to ENUM_ST_IDLE.
  typedef enum logic [0:0] {
    ENUM_ST_IDLE = 1'b0,
    ENUM_ST_SEND = 1'b1
  } ctrl_state_type_def;

  // Internal signal declarations
  ctrl_state_type_def reg_fsm_ctrl_current_state;
  ctrl_state_type_def w_fsm_ctrl_nxt_state;

  // Part 1, sequential: the current state register. The control state is reset asynchronously to
  // IDLE and otherwise takes the next state every clock cycle.
  always_ff @(posedge i_clk_core, negedge i_rst_n_core) begin : p_ff_fsm_ctrl
    if (!i_rst_n_core)
      reg_fsm_ctrl_current_state <= ENUM_ST_IDLE;
    else
      reg_fsm_ctrl_current_state <= w_fsm_ctrl_nxt_state;
  end

  // Part 2, combinational: the next state depends on the current state and the inputs.
  // IDLE -> SEND on i_start; SEND stays until the last item is accepted (i_ready and i_last), then
  // goes back to IDLE.
  // The next state is assigned first (COM-02), and every case has a default (COM-03), so the
  // process drives the next state on every path and no latch is inferred (COM-07).
  always_comb begin : p_com_fsm_nxt
    w_fsm_ctrl_nxt_state = reg_fsm_ctrl_current_state;
    case (reg_fsm_ctrl_current_state)
      ENUM_ST_IDLE: begin
        if (i_start)
          w_fsm_ctrl_nxt_state = ENUM_ST_SEND;
      end
      ENUM_ST_SEND: begin
        if (i_ready & i_last)
          w_fsm_ctrl_nxt_state = ENUM_ST_IDLE;
      end
      default: w_fsm_ctrl_nxt_state = ENUM_ST_IDLE;
    endcase
  end

  // Part 3, combinational: the Mealy outputs. They depend on the current state and on the inputs,
  // so o_load_en and o_done react in the same cycle as i_start, i_ready and i_last (no extra state
  // is needed), but a change of an input can reach an output through combinational logic. Register
  // an output in its own process when a glitch-free or late-arriving output is required.
  // In SEND, three cases depend on {i_ready, i_last}: not accepted (i_last is ignored, an
  // intentional wildcard), the last item accepted, or an item accepted and the next one loaded.
  // Each output gets its default first (COM-02), so even the outputs set only inside a branch
  // are assigned on every path and no latch is inferred (COM-07).
  always_comb begin : p_com_fsm_out
    o_busy       = 1'b0;
    o_load_en    = 1'b0;
    o_send_valid = 1'b0;
    o_done       = 1'b0;
    case (reg_fsm_ctrl_current_state)
      ENUM_ST_IDLE: begin
        if (i_start)
          o_load_en = 1'b1;
      end
      ENUM_ST_SEND: begin
        o_busy       = 1'b1;
        o_send_valid = 1'b1;
        casez ({i_ready, i_last})
          2'b0?:   o_done    = 1'b0;
          2'b11:   o_done    = 1'b1;
          2'b10:   o_load_en = 1'b1;
          default: o_done    = 1'b0;
        endcase
      end
      default: begin
        // Same as IDLE without a start: all outputs stay at their default value.
      end
    endcase
  end

endmodule
