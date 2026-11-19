# Scripts

All scripts in this directory support the workflows in `../SKILL.md`. Run Python scripts with the executable returned by `vlsit_find_python.ps1` (Windows) or `vlsit_find_python.sh` (Linux/macOS). The `vlsit_spec_tool.py` and figure generators are Python 3 standard-library tools; `vlsit_csr_tool.py` uses `openpyxl`; PDF conversion/rendering uses PyMuPDF; Pandoc and optional PDF engines are external programs. Install nothing without user approval.

| Script | Function |
|---|---|
| `vlsit_spec_tool.py` | Initialize, check and query the specification; verify sections, ports, waveform plan, diagram sources, and FSM figures. |
| `vlsit_spec_diagram.py` | Build and insert VLSIT-library block diagrams and their JSON specification. |
| `vlsit_fsm_diagram.py` | Check, lay out, build and insert VLSIT-library FSM diagrams and their JSON specification. |
| `vlsit_waveform_svg.py` | Check WaveJSON label fit (`check`, honours `config.hscale` and `--cell`) and render waveforms to SVG. |
| `vlsit_csr_tool.py` | Validate CSR JSON, fill/dump workbook sheets and list generated ports. |
| `vlsit_library_symbols.py` | Catalog, clone and validate shapes against the bundled VLSIT draw.io library. |
| `vlsit_drawio_frame_diagram.py` | Render a JSON block-diagram layout to draw.io. |
| `vlsit_drawio_geometry_check.py` | Check diagram geometry, routing and text fit. |
| `vlsit_drawio_to_svg.py` | Render draw.io diagrams to SVG, optionally PNG (blocks, ellipses, connectors with line jumps, transition labels, native tables). |
| `vlsit_layout_search.py` | Compare candidate block-diagram layouts. |
| `vlsit_protocol_docs.py` | Inspect and, after approval, retrieve protocol documents. |
| `vlsit_doc_to_md.py`, `vlsit_pdf_to_md.py` | Convert standards and documents to Markdown for analysis. |
| `vlsit_pdf_render.py` | Render selected PDF pages or diagrams. |
| `vlsit_ip_search.py` | Research public reference-IP evidence. |
| `vlsit_spec_export.py` | Export the Markdown specification to selected DOCX/PDF formats. |
| `vlsit_block_diagram.py` | Legacy LaTeX/TikZ fallback when requested or needed. |

The `tests/` directory contains existing script checks. This consolidation did not run them.
