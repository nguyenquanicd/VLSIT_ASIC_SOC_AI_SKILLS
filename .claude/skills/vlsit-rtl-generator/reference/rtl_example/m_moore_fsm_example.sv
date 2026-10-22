/*
 * Project      : VLSI Technology - AI RTL generator
 * Author       : Nguyen Quan and Claude (user)
 * AI Flow      : VLSIT RTL Generator AI Automation Flow
 * AI Flow Page : https://github.com/nguyenquanicd/VLSIT_RTL_Generator_AI_Model
 * Date         : 2026-10-18
 * Description  : Example of a Moore FSM in three parts: a sequential process for the current
 *                state, a combinational process for the next state and one for the outputs.
 *                The outputs depend on the current state only.
 */
`timescale 1ns/1ps

module m_moore_fsm_example (
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

  // FSM states: IDLE waits for i_start, LOAD prepares one item, SEND offers the item until i_ready,
  // and DONE reports the end of a burst for one cycle. All four encodings of the 2-bit state are
  // used; any other value (for example after a fault) recovers to ENUM_ST_IDLE through default.
  typedef enum logic [1:0] {
    ENUM_ST_IDLE = 2'b00,
    ENUM_ST_LOAD = 2'b01,
    ENUM_ST_SEND = 2'b10,
    ENUM_ST_DONE = 2'b11
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
  // IDLE -> LOAD on i_start; LOAD -> SEND always; SEND stays until i_ready, then goes to DONE on
  // i_last or back to LOAD for the next item; DONE -> IDLE always.
  // The next state is assigned first (COM-02), and every case has a default (COM-03), so the
  // process drives the next state on every path and no latch is inferred (COM-07).
  always_comb begin : p_com_fsm_nxt
    w_fsm_ctrl_nxt_state = reg_fsm_ctrl_current_state;
    case (reg_fsm_ctrl_current_state)
      ENUM_ST_IDLE: begin
        if (i_start)
          w_fsm_ctrl_nxt_state = ENUM_ST_LOAD;
      end
      ENUM_ST_LOAD: w_fsm_ctrl_nxt_state = ENUM_ST_SEND;
      ENUM_ST_SEND: begin
        // Three outcomes depend on {i_ready, i_last}: stay while i_ready is low (i_last is ignored,
        // an intentional wildcard), go to DONE on the last item, otherwise load the next item.
        // The four binary values are covered; the default keeps the current state.
        casez ({i_ready, i_last})
          2'b0?:   w_fsm_ctrl_nxt_state = ENUM_ST_SEND;
          2'b11:   w_fsm_ctrl_nxt_state = ENUM_ST_DONE;
          2'b10:   w_fsm_ctrl_nxt_state = ENUM_ST_LOAD;
          default: w_fsm_ctrl_nxt_state = ENUM_ST_SEND;
        endcase
      end
      ENUM_ST_DONE: w_fsm_ctrl_nxt_state = ENUM_ST_IDLE;
      default:      w_fsm_ctrl_nxt_state = ENUM_ST_IDLE;
    endcase
  end

  // Part 3, combinational: the Moore outputs. They are decoded from the current state only, never
  // from the inputs, so they cannot glitch because of an input change. Every output gets its
  // default first (COM-02), so each output is assigned on every path and no latch is inferred
  // (COM-07).
  always_comb begin : p_com_fsm_out
    o_busy       = 1'b0;
    o_load_en    = 1'b0;
    o_send_valid = 1'b0;
    o_done       = 1'b0;
    case (reg_fsm_ctrl_current_state)
      ENUM_ST_IDLE: begin
        // No output is active while waiting for a start request.
      end
      ENUM_ST_LOAD: begin
        o_busy    = 1'b1;
        o_load_en = 1'b1;
      end
      ENUM_ST_SEND: begin
        o_busy       = 1'b1;
        o_send_valid = 1'b1;
      end
      ENUM_ST_DONE: begin
        o_done = 1'b1;
      end
      default: begin
        // Same as IDLE: all outputs stay at their default value.
      end
    endcase
  end

endmodule
