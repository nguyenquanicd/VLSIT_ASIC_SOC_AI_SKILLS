#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# This file imports PyMuPDF (AGPL-3.0). Because of that import it is licensed under the GNU Affero General
# Public License v3.0 only; the other scripts of this skill that do not import PyMuPDF keep Apache-2.0.
# ---------------------------------------------------------------------------
# File     : vlsit_pdf_render.py
# Function : render a PDF page, such as a compiled diagram, to SVG or PNG
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Turn the first page of a PDF (for example a compiled LaTeX block diagram) into an SVG or PNG image.

Purpose : the specification is Markdown, which shows images but not PDF pages; this converts the output of
          vlsit_block_diagram.py build into figures/NAME.svg or .png so that section 5.2 shows the diagram.
Usage   : vlsit_pdf_render.py FILE.pdf [--svg OUT.svg] [--png OUT.png] [--dpi 160] [--force]
Output  : the requested image files; one result line.
Exit    : 0 success, 1 error, 3 PyMuPDF missing (python -m pip install pymupdf; ask the user first).
"""
import argparse
import sys
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pdf")
    parser.add_argument("--svg")
    parser.add_argument("--png")
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--force", action="store_true")
    a = parser.parse_args()
    if fitz is None:
        print("ERROR: PyMuPDF missing; install with: python -m pip install pymupdf (ask the user first)")
        return 3
    if not (a.svg or a.png):
        print("ERROR: give --svg and/or --png")
        return 1
    if not Path(a.pdf).is_file():
        print("ERROR: file not found: %s" % a.pdf)
        return 1
    for target in (a.svg, a.png):
        if target and Path(target).exists() and not a.force:
            print("ERROR: %s already exists; pass --force to overwrite it" % target)
            return 1
    page = fitz.open(a.pdf)[0]
    done = []
    if a.svg:
        Path(a.svg).parent.mkdir(parents=True, exist_ok=True)
        Path(a.svg).write_text(page.get_svg_image(text_as_path=False), encoding="utf-8")
        done.append(a.svg)
    if a.png:
        Path(a.png).parent.mkdir(parents=True, exist_ok=True)
        page.get_pixmap(dpi=a.dpi).save(a.png)
        done.append(a.png)
    print("OK: wrote %s" % ", ".join(done))
    return 0


if __name__ == "__main__":
    sys.exit(main())
