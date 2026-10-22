# RTL skeletons

Guidance only; the mandatory requirements are in [rule.md](../../rule.md). Copy a skeleton, replace the angle-bracket values with the real ones, and keep the structure. Every skeleton follows the rule file: header, `timescale`, ANSI ports, comments before each section, spaces only, 100 characters per comment line at most.

## Header and leaf module

```systemverilog
/*
 * Project      : <PROJECT_NAME>
 * Author       : <USER_NAME> (user)
 * AI Flow      : VLSIT RTL Generator AI Automation Flow
 * AI Flow Page : https://github.com/nguyenquanicd/VLSIT_RTL_Generator_AI_Model
 * Date         : <YYYY-MM-DD>
 * Description  : <what the module does, in one or two lines>
 */
`timescale 1ns/1ps

module m_<function> #(
  // Parameter Description: <purpose, dependencies>.
  // Parameter values: <legal values or range>; default is <value>.
  // Parameter unit: <bit | byte | count | none>
  parameter logic [31:0] PARA_<NAME> = <default>,
  localparam logic [31:0] LPARA_<NAME> = <expression of the parameters>
) (
  // Clock and reset
  input  wire                    i_clk_<domain>,
  input  wire                    i_rst_n_<domain>,

  // <Function of the group>
  input  wire  [PARA_<NAME>-1:0] i_<name>,
  output logic [PARA_<NAME>-1:0] o_<name>
);

  // <behavior of this process, reset and validity assumptions>
  always_comb begin : p_com_<function>
    w_<name> = '0;
    ...
  end

  // <what is registered, reset policy of this state>
  always_ff @(posedge i_clk_<domain>, negedge i_rst_n_<domain>) begin : p_ff_<function>
    if (!i_rst_n_<domain>)
      reg_<name> <= '0;
    else
      reg_<name> <= w_<name>_nxt;
  end

endmodule
```

## FSM with recovery state

```systemverilog
  // FSM states: <one line per state>. Unused encoding 2'b11 recovers to ENUM_ST_IDLE.
  typedef enum logic [1:0] {
    ENUM_ST_IDLE = 2'b00,
    ENUM_ST_RUN  = 2'b01,
    ENUM_ST_DONE = 2'b10
  } ctrl_state_type_def;

  ctrl_state_type_def reg_fsm_ctrl_current_state;
  ctrl_state_type_def w_fsm_ctrl_nxt_state;

  // Next-state logic: <transitions in words>.
  always_comb begin : p_com_fsm
    w_fsm_ctrl_nxt_state = reg_fsm_ctrl_current_state;
    case (reg_fsm_ctrl_current_state)
      ENUM_ST_IDLE: if (i_start) w_fsm_ctrl_nxt_state = ENUM_ST_RUN;
      ENUM_ST_RUN:  if (w_done)  w_fsm_ctrl_nxt_state = ENUM_ST_DONE;
      ENUM_ST_DONE: w_fsm_ctrl_nxt_state = ENUM_ST_IDLE;
      default:      w_fsm_ctrl_nxt_state = ENUM_ST_IDLE;
    endcase
  end
```

The function part of the state names is at most 8 characters (ENM-04).

## Selection of three or more branches (R-019)

```systemverilog
  // Selection by value: one signal chooses among several results. A plain case with a default.
  always_comb begin : p_com_select
    w_result = '0;
    case (i_sel)
      2'd0:    w_result = i_a;
      2'd1:    w_result = i_b;
      2'd2:    w_result = i_c;
      default: w_result = '0;
    endcase
  end

  // Priority selection: i_req_0 has the highest priority. casez with ? for the lower-priority
  // bits is an intentional wildcard decode; the default assigns a defined value (COM-04).
  always_comb begin : p_com_prio
    w_grant = 3'b000;
    casez ({i_req_2, i_req_1, i_req_0})
      3'b??1:  w_grant = 3'b001;
      3'b?10:  w_grant = 3'b010;
      3'b100:  w_grant = 3'b100;
      default: w_grant = 3'b000;
    endcase
  end
```

## Structural top

```systemverilog
module m_<ip>_top (
  input wire i_clk_<domain>,
  input wire i_rst_n_<domain>,
  ...
);
  logic w_<name>;

  // <what the instance does and how it connects>
  m_<function> #(
    .PARA_<NAME> (<value>)
  ) u_<function> (
    .i_clk_<domain>   (i_clk_<domain>),
    .i_rst_n_<domain> (i_rst_n_<domain>),
    ...
  );

  // Repeated lanes use a zero-based generate with the genvar in the for header.
  for (genvar gen_idx = 0; gen_idx < <count>; gen_idx++) begin : gen_<function>
    m_<function> u_<function> (...);
  end
endmodule
```

The top holds the interface, parameters, wires and instances only. Any logic goes into a named child module (HIE-02). Connect every port by name (HIE-03).

## Point the template at the rule

The rule file's own section 8.2 is the reference when a skeleton and the rule file differ. Note that its example comment line of 101 characters breaks its own limit CMT-05, so shorten a copied comment before it is delivered.
