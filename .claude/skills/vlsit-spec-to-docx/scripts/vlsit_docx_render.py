#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_docx_render.py
# Function : render a DOCX to PDF and, when PyMuPDF is present, to one PNG per page
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Render a DOCX so the layout can be inspected.

Exit codes:
    0  PDF and page images produced
    3  no LibreOffice found; nothing rendered
    4  PDF produced, page images not produced (PyMuPDF missing)

Usage:
    vlsit_docx_render.py <document.docx> --out <pages folder> [--dpi 110]
"""

import argparse
import os
import shutil
import subprocess
import sys

CANDIDATES = ("soffice", "soffice.exe", "libreoffice")


def find_soffice():
    """Return the path of a LibreOffice binary, or None."""
    override = os.environ.get("VLSIT_SOFFICE")
    if override and os.path.isfile(override):
        return override
    for candidate in CANDIDATES:
        found = shutil.which(candidate)
        if found:
            return found
        if os.path.isabs(candidate) and os.path.isfile(candidate):
            return candidate
    cache = os.path.join(os.path.expanduser("~"), ".dsh", "office-kit")
    if os.path.isdir(cache):
        for root, _dirs, files in os.walk(cache):
            for name in files:
                if name.lower() in ("soffice", "soffice.exe"):
                    return os.path.join(root, name)
    return None


def main():
    parser = argparse.ArgumentParser(description="Render a DOCX to PDF and page images.")
    parser.add_argument("document", help="the .docx file")
    parser.add_argument("--out", required=True, help="folder for the PDF and page images")
    parser.add_argument("--dpi", type=int, default=110)
    args = parser.parse_args()

    if not os.path.isfile(args.document):
        print("ERROR document not found: %s" % args.document)
        return 2
    if not os.path.isdir(args.out):
        os.makedirs(args.out, exist_ok=True)

    soffice = find_soffice()
    if soffice is None:
        print("NO-RENDER LibreOffice was not found.")
        print("Install LibreOffice, set VLSIT_SOFFICE to its soffice binary, or accept structure-only verification.")
        return 3

    command = [soffice, "--headless", "--norestore", "--convert-to", "pdf",
               "--outdir", args.out, args.document]
    result = subprocess.run(command, capture_output=True, text=True)
    stem = os.path.splitext(os.path.basename(args.document))[0]
    pdf = os.path.join(args.out, stem + ".pdf")
    if result.returncode != 0 or not os.path.isfile(pdf):
        print("ERROR LibreOffice conversion failed: %s" % (result.stderr or result.stdout).strip()[:300])
        return 2

    print("PDF %s (%.1f KB)" % (pdf, os.path.getsize(pdf) / 1024.0))

    try:
        import fitz
    except ImportError:
        print("NO-PAGES PyMuPDF is not installed, so the PDF was produced but no page image was.")
        print("Open the PDF to inspect the layout, or install PyMuPDF with the user's approval.")
        return 4

    document = fitz.open(pdf)
    zoom = args.dpi / 72.0
    for page_number, page in enumerate(document, start=1):
        pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        target = os.path.join(args.out, "%s_p%02d.png" % (stem, page_number))
        pixmap.save(target)
    document.close()
    print("PAGES %d images at %d dpi in %s" % (page_number, args.dpi, args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
