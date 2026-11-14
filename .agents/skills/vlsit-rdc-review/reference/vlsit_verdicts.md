# Grouping and verdicts

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

## Grouping by root cause (rule R-021)

Two violation records join one group when one of these holds:

1. **Same path, several sections** - the tool reports the same `from -> to` in, for
   example, "Reset Domain Crossing" and "Reset Tree Convergence". The group keeps all
   the section names so the reader sees the tool counted it twice.
2. **Same missing mechanism** - several paths between the same two domains, none of them
   with a reset synchroniser. The root cause is the missing synchroniser, not each path.
3. **Same over-broad exception** - several paths covered by one `set_false_path` or one
   `set_clock_groups` that is wider than the design needs.
4. **Same reset tree** - paths whose source flops share one reset pin and whose
   destination flops share another, with the same skew problem.

`vlsit_rdc_group.py` applies these keys in that order and prints the key it used per
group, so the grouping is auditable. A record that matches no key is reported as its own
group with the reason `no shared root cause`.

## The four verdicts (rule R-022)

| Verdict | When it applies | What the fix looks like | What must be said |
|---|---|---|---|
| `fix RTL` | the mechanism is `none` or `claimed`, or the deassertion is asynchronous | add a reset synchroniser in the destination domain, or a sequencer, or move the crossing flop to the destination reset | which module changes, which signal, and what the fix protects |
| `fix SDC` | the RTL is correct but the constraint is missing or too wide | add or narrow `set_false_path` / `set_clock_groups`, or constrain the reset pin | the exact command, the object list and the reason the RTL needs it |
| `waive` | the hazard exists but is not reachable, or the two domains are released together by a mechanism the tool cannot see | no change | mechanism, evidence, risk, invalidation condition and owner (rule R-023) |
| `not RDC` | the two domains are the same domain, or the reset is shared and never deasserted independently | no change, but the tool finding is explained | why the tool reported it and why no hazard exists |

## Justification template (rule R-025)

```
Group: G-03
Root cause: the destination flops of u_tlul_if have no reset synchroniser; the reset
            pin comes straight from the port i_rst_n_core (m_tlul_if.sv:41).
Mechanism: none (no chain of two flops on the reset, checked m_tlul_if.sv:1-208).
Verdict: fix RTL.
Risk if accepted: the two flops of the response path leave reset in different cycles
            when the deassertion is close to a clock edge, so the APB side can sample a
            response valid in a cycle where the data is still reset.
Fix: add a reset synchroniser per domain, or connect the destination flops to
            o_rst_sync from the reset synchroniser module, and re-run the tool.
Evidence read: m_tlul_if.sv:41, 175-206; rdc_rtl.json domains; tool section 4.
Owner: digital design lead (to be confirmed).
```

## What a waiver must never say

- "known and accepted" without the mechanism;
- "the tool is wrong" without the same-domain evidence;
- "quasi-static" for a signal that changes once per transaction while the destination is
  in reset;
- "covered by another constraint" without naming the command and its objects.
