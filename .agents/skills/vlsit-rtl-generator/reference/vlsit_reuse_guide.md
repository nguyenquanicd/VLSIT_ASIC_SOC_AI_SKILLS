# Reusing the library common_rtl

Guidance only; the mandatory requirement is R-037 in [rule.md](../rule.md). Read this before step 4c of the workflow.

## 1. What the library is

`common_rtl` (in the repository `VLSIT_RTL_Generator_AI_Model`) holds reusable RTL: shared wrappers and helpers in `000_Common/rtl_lib` (reset synchronizer, tie-off, synchronizer cell wrappers with a metastability model, SRAM macro wrappers) and complete designs (FIFOs, CRC, bridges), each with a specification, a `rtl/filelist.f` and, where the folder says so, lint logs, a testbench and simulation evidence. Its `README.md` is the directory map; the `list` action of `vlsit_reuse_scan.py` prints the catalog with the parameters of each module.

## 2. Find the candidates

```
python <skill>/scripts/vlsit_reuse_scan.py scan <spec.md> --lib <path of common_rtl>
```

The script ranks the modules by shared keywords (module name, with the abbreviations of the naming rule expanded, and header description). It does not decide anything. For each candidate judge, from the module header, the port list and the parameters of the library module and from the specification:

| Check | Equivalent when |
|---|---|
| Function | The module does what the specification section describes, not only a similar word (a "synchronizer" for one bit is not a FIFO pointer crossing) |
| Interface | The ports and their meaning match, or differ only in widths and parameters that the module already offers |
| Parameters | Every value the specification needs is inside the legal range of the module |
| Behavior and timing | Latency, reset values and corner cases agree with the requirements; read the module's own specification, not only its header |
| Flow | The module follows the same rule file (naming, reset, CDC), so no exception is needed |

A module that fits only partly is not equivalent: say so in the question (option C below) and let the designer decide.

## 3. The question (rule R-006 format)

Ask once per equivalent function, in the language of the designer. Name the library module and its folder, and the section of the specification it would replace. Example of the wording:

> The specification section 7.2 needs a reset synchronizer with asynchronous assertion and synchronous release. The library already has `m_vlsit_rst_sync` (`common_rtl/000_Common/rtl_lib`, parameter `PARA_RST_SYNC_TYPE` for 2, 3 or 4 stages), which passed the rule check and lint and has its own test in `000_Common/lib_tests`. How do you want to proceed?
>
> **A (recommended): reuse the library module.** I instantiate `m_vlsit_rst_sync` and add its file to `filelist.f`; I write no new reset synchronizer.
> Advantages: the module is already checked, so you do not review it again; names, reset style and clock-domain-crossing structure stay the same as in your other designs; and the AI model spends its effort, and your review time goes, on the functions that do not exist yet, which makes those functions more likely to be right.
> Limits: the interface and the parameters are those of the module; a change in the library module reaches this design.
>
> **B: generate new RTL for this function.** Choose this when you need a different interface, behavior or technology cell, or want the function inside this design for another reason. Cost: new code to verify and review, and a second implementation of the same function to maintain.
>
> **C: reuse the module and adapt around it.** I instantiate the library module and add a small wrapper or glue logic in the new design for the missing part (for example a different reset polarity). The library module itself is not edited.
>
> **D: your own idea.** Write it.

Rules for the question:

- Mark reuse (A) as the recommended option, because the rule asks to reuse by default; give the reason in the text (the checked code is not generated and reviewed again, and the effort goes to the new functions).
- Give the concrete facts of the module: path, parameters, evidence found (rule check, lint, simulation, specification), and what it would replace.
- Group candidates that belong together (for example a FIFO and its memory wrapper) in one question, at most four questions in a message.
- A designer who says "generate it again" or gives a reason for a new module overrides the default; write the reason in the report.

## 4. After the answer

- **Reuse (A or C):** do not copy or edit the library file. Instantiate the module with named connections, add its path to `filelist.f` (relative path from the output folder, or the folder `common_rtl/...`), and add the cell models it needs (`000_Common/rtl_cells`) to the lint file list. Check the connection with the rule check and lint of the whole set.
- **Generate (B):** write the module under the rules as usual and record the designer's reason in the report; do not name it like a library module.
- **Record every answer** in the report of R-016: module, folder, answer, reason, and the files added to the filelist.

## 5. When the library is not found

The script searches the current folder and its parents for `common_rtl`. If it is not found, ask the designer for the path (R-003 style) or whether the project has no library; do not skip the check silently.
