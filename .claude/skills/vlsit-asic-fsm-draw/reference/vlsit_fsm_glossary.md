# FSM Drawing Glossary

| Term | Meaning in this skill |
|---|---|
| Finite-State Machine (FSM) | A controller described by a finite set of states and transitions between them. |
| State | A named operating condition represented by one oval in the diagram. |
| Transition | A directed change from a source state to a destination state, labeled with its triggering event or condition. |
| Initial state | The state entered on reset or startup, as defined by the approved design source. |
| Reset assertion condition | The reset signal value that asserts reset, derived from its approved active polarity. |
| Self-loop | An arrow that returns to its source state; it may be unlabeled for a default hold or labeled with an explicit source guard. |
| Condition alias | A short English transition label mapped to the exact Boolean expression on a condition-mapping page. |
| draw.io | The editable diagram format used for source diagrams. The `.drawio` file is XML. |
| Scalable Vector Graphics (SVG) | A vector image format suitable for Markdown and browser rendering. |
| JavaScript Object Notation (JSON) | The structured input and sidecar format for states, transitions and layout settings. |
