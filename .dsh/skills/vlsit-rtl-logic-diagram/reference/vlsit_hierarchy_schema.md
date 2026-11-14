# `hierarchy.json` schema

One file describes the whole design. The keys are lower-case snake_case and every
string is English (rule R-005). `vlsit_hierarchy.py build` writes the structure and
`check` verifies it (rule R-010).

```json
{
  "schema": "vlsit-hierarchy/1",
  "design": "m_apb_tlul_bridge",
  "top": "m_apb_tlul_bridge",
  "source": {
    "root": "common_rtl/007_APB2TLUL_Bridge/rtl",
    "files": [{"path": "m_apb_tlul_bridge.sv", "sha256": "..."}]
  },
  "modules": [
    {
      "name": "m_apb_tlul_bridge",
      "file": "m_apb_tlul_bridge.sv",
      "line": 12,
      "parent": null,
      "purpose": "Bridge one APB4 completer port to one TL-UL host port.",
      "behaviour": "Two independent finite state machines, one per side; the response of one side waits for the request of the other.",
      "evidence": ["m_apb_tlul_bridge.sv:120-210"],
      "parameters": [{"name": "PARA_ADDR_W", "default": "32"}],
      "ports": [
        {"name": "i_clk_core", "direction": "input", "width": 1,
         "domain": "core", "description": "Core clock, all logic runs on its rising edge."},
        {"name": "i_apb_paddr", "direction": "input", "width": "PARA_ADDR_W",
         "domain": "apb", "description": "APB byte address."}
      ],
      "instances": [
        {"name": "u_apb_if", "module": "m_apb_if", "line": 85,
         "connections": [{"port": "i_clk", "signal": "i_clk_core"},
                         {"port": "o_req", "signal": "w_apb_req"}]}
      ]
    }
  ]
}
```

## Field contract

| Field | Required | Meaning |
|---|---|---|
| `schema` | yes | `vlsit-hierarchy/1` |
| `design` | yes | Short name of the design, used in file names |
| `top` | yes | Module the diagram is rooted at (rule R-006) |
| `source.root` | yes | Folder or file the analysis started from |
| `source.files[]` | yes | Every scanned file with its SHA-256 before the run (rule R-002) |
| `modules[].name`, `file`, `line` | yes | Identity and the declaration line |
| `modules[].parent` | yes | Parent module name, `null` for the top |
| `modules[].purpose` | yes | One sentence, step 7 |
| `modules[].behaviour` | yes | State, latency, handshake, reset, corner cases |
| `modules[].evidence[]` | yes | `file:start-end` ranges the analysis is based on |
| `modules[].parameters[]` | no | Name and default, when the module has parameters |
| `modules[].ports[]` | yes | `name`, `direction` (`input` / `output` / `inout`), `width` (integer or parameter expression), optional `domain`, `description` |
| `modules[].instances[]` | yes | `name`, `module`, `line`, `connections[]` with `port` and `signal` |

## Rules the checker enforces

- every module has a file that exists, a line above zero, and a parent except the top;
- every port has a direction, a width and a description;
- every instance names a module that exists in `modules`;
- every connection names a port of the instance's module;
- the parent chain from any module reaches `top`.

A field that is unknown stays `null`; it is never filled with a guess (rule R-004).
