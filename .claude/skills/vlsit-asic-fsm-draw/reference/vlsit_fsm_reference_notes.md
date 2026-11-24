# Supplied FSM Diagram Reference

## Purpose

`vlsit_fsm_diagram_reference.drawio` is the supplied editable visual example. The SVG, Markdown and HTML files beside it are derived previews made with the skill's offline renderer.

## What it illustrates

- Four state ovals: `ST_IDLE`, `ST_START`, `ST_WORKING` and `ST_DONE`.
- An incoming reset arrow to `ST_IDLE`, labeled `i_rst_n`.
- Curved transitions and state self-loops.
- Transition labels, including `w_start | w_repeat`, `i_restart` and `w_cnt == 8'hFF`.

## Limits

The supplied diagram has unlabeled arrows and unlabeled self-loops. It is a layout reference only, not an authoritative FSM specification. Do not copy its behavior or assume that its transition conditions are complete. New diagrams must take every state and transition from an approved source, show reset polarity, label every state-changing transition, represent default holds without an invented condition, and pass the geometry checks in [rule.md](../rule.md).
