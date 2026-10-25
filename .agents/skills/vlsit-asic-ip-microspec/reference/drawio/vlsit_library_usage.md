# VLSIT draw.io library usage

The sole symbol source is [VLSIT_DRAWIO_LIB_V1.drawio.xml](../assets/VLSIT_DRAWIO_LIB_V1.drawio.xml). The bundled file is an exact copy of the user-supplied library, not a generated substitute.

- Format: mxlibrary XML containing a JSON array of 39 templates.
- Snapshot SHA-256: D1631ACF98A920526B235E8970FEDDC9305EA2F0D6A35C6529CD220D62AFABB6.
- Entries have no titles. Identify them by zero-based JSON array index and actual decoded cells; do not reorder the library.
- This file defines symbol appearance, not RTL behavior. Placeholder labels such as COM, STATE, Description, and enable ? are not evidence about the analyzed design.

## Required template selection

| Index | Library template | Intended diagram use |
|---|---|---|
| 0 | TEXT | Page titles, interface annotations, legends, and external notes |
| 1 | Straight arrow | Straight connections |
| 2 | Segmented arrow | Connections with explicit bends |
| 3–4 | Horizontal/vertical elbow arrows | Elbow connections |
| 5 | Grouped crossed rectangle | Only when its meaning is explicitly established |
| 6–7 | Single/paired rectangle-and-triangle groups | Only for source-grounded logic detail |
| 8–9 | Rotated trapezoids with 1/0 labels | Source-grounded selection logic |
| 10 | COM cloud | Source-grounded combinational logic |
| 11–12 | OR/XOR shapes | Corresponding proven operations |
| 13 | STATE ellipse | Source-grounded state representation |
| 14 | Curved arrow | Connections requiring a curved route |
| 15 | State text template | Source-grounded state/output annotations |
| 16–17 | Curly brackets | Group annotations |
| 18–23 | Electrical XOR, inverted OR/XOR, triangle, and inverted triangle templates | Corresponding proven logic operations; inspect the selected template |
| 24–26 | D-type flip-flop templates with different control pins | Match the actual clock/control semantics before selection |
| 27 | Orthogonal arrow | Preferred hierarchy and functional connectors |
| 28–31 | Partial rectangle templates | Only when their semantics are explicitly established |
| 32 | Description rectangle | All module blocks and bordered note panels |
| 33 | Rounded START rectangle | Source-grounded flow detail, when requested |
| 34 | enable ? diamond | Source-grounded decision detail, when requested |
| 35–38 | Arithmetic/shift squares | Replace placeholders with the actual proven operation |

Logic symbols do not automatically expand a hierarchy request into a gate-level diagram. Use them only when the requested diagram requires that detail and the RTL supports the interpretation. Do not substitute a generic shape for a missing required symbol. Ask the user to extend this library, or agree to a representation using existing templates that preserves the meaning.

## Decode and clone

1. Parse the outer XML, require an mxlibrary root, and parse its text as JSON.
2. Parse the selected entry's xml field as an mxGraphModel. The current snapshot uses XML fragments directly. Do not HTML-unescape the entire fragment again; that can corrupt HTML labels encoded as attribute values.
3. Clone all non-root cells of that entry, including groups, child cells, and internal edges. Allocate unique diagram IDs and consistently remap parent/source/target references. The standard page root cells 0 and 1 are document structure and are not symbols.
4. Preserve template type, shape, perimeter, gate operation, arrowheads, orientation, and internal group topology. Place and size clones for the layout; scale grouped symbols proportionally. Do not discard constituent cells or add arbitrary geometry to a group.
5. Replace placeholders with RTL-grounded labels. For module rectangles from index 32, use exactly two centered lines: instance name, then module name in parentheses.
6. Normalize visible text to fontSize=18 and black text. Use white or transparent fills and black or invisible borders as appropriate to the original template. Preserve text templates and groups as transparent rather than drawing unwanted surrounding boxes. Geometry, routing endpoints, label alignment/spacing, line width, dash patterns, and line jumps (`jumpStyle=arc`, `jumpSize`, RHD-057) may be adjusted for readability.
7. Use index 0 for additional text and index 32 for bordered note panels. Never create untraceable freehand symbols, imported images, external stencils, or vertices selected from another library. Built-in renderer names already present in this library's styles remain valid dependencies of these exact templates.

Each cloned mxCell must contain:

| Attribute | Value |
|---|---|
| vlsit_library_sha256 | SHA-256 of the actual bundled library bytes, uppercase |
| vlsit_library_entry | Zero-based entry index |
| vlsit_library_cell | Original cell ID within that entry |
| vlsit_library_instance | Unique clone identifier within the page |

All cells in one cloned group share the same instance identifier and entry index. This metadata is provenance; it does not establish functional correctness.

## Helper commands

Run from this skill folder. Replace directory tokens with runtime paths.

    python scripts/vlsit_library_symbols.py catalog
    python scripts/vlsit_library_symbols.py clone --entry 32 --instance u_fifo --label "u_fifo<br>(m_fifo)" --output <NEW_FRAGMENT_XML>
    python scripts/vlsit_library_symbols.py validate --diagram <GENERATED_DRAWIO_FILE>

The clone command writes a new mxGraphModel fragment and never overwrites a file. The module template has HTML labels enabled; use an HTML line break as shown for its two-line instance/module label. Do not place descriptions inside module labels.

Prefer generating uncompressed mxGraphModel pages for inspection. The validator also reads standard compressed draw.io pages. It checks library hashes, cell identities, complete groups, parent/internal-edge mappings, immutable style properties, font size, and black/white styling. It does not verify RTL connectivity, diagram readability, proportional scaling, or semantic correctness of substituted labels. Inspect those separately.

A symbol that fails provenance validation must be corrected before the diagram is described as library-compliant. Do not modify the library or its metadata merely to hide a failed check.
