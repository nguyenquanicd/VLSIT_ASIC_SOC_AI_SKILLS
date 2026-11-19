#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_spec_export.py
# Function : export a VLSIT Markdown specification to DOCX and/or PDF with Pandoc
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Export the authoritative Markdown specification to derived DOCX/PDF files.

Usage   : vlsit_spec_export.py export SPEC.md --format {docx,pdf,all} [options]
Math    : Pandoc Markdown with TeX dollar math; figures resolve relative to SPEC.md.
PDF     : Pandoc plus an installed PDF engine; Typst is the default.
Exit    : 0 success, 1 invalid input/output conflict or conversion failure, 3 tool missing.
Packages: Python standard library only. This script never installs software.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_tool(name):
    """Find a tool on PATH or in the default per-user Windows install location."""
    found = shutil.which(name)
    if found or os.name != "nt":
        return found
    local_roots = []
    if os.environ.get("LOCALAPPDATA"):
        local_roots.append(Path(os.environ["LOCALAPPDATA"]))
    profile_local = Path.home() / "AppData" / "Local"
    if profile_local not in local_roots:
        local_roots.append(profile_local)
    candidates = []
    if name == "pandoc":
        candidates.extend(local / "Pandoc" / "pandoc.exe" for local in local_roots)
    elif name == "typst":
        for local in local_roots:
            package_root = local / "Microsoft" / "WinGet" / "Packages"
            if package_root.is_dir():
                for package in package_root.glob("Typst.Typst_*"):
                    candidates.extend(package.glob("typst-*/typst.exe"))
    return next((str(path) for path in candidates if path.is_file()), None)


def run_pandoc(pandoc, source, output, kind, pdf_engine=None, reference_doc=None):
    command = [
        pandoc,
        "--from=markdown+tex_math_dollars",
        "--standalone",
        "--output",
        str(output),
    ]
    if kind == "docx":
        command.extend(["--to=docx"])
        if reference_doc:
            command.extend(["--reference-doc", str(reference_doc)])
    else:
        command.extend(["--pdf-engine=" + pdf_engine])
    command.append(source.name)

    try:
        result = subprocess.run(
            command,
            cwd=str(source.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        print("ERROR: could not start Pandoc: %s" % exc, file=sys.stderr)
        return False

    if result.returncode != 0:
        print("ERROR: Pandoc failed to create %s (exit %d)." % (output, result.returncode), file=sys.stderr)
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        return False
    if not output.is_file() or output.stat().st_size == 0:
        print("ERROR: Pandoc returned success but the output is missing or empty: %s" % output, file=sys.stderr)
        return False
    print("OK: %s" % output)
    return True


def export(args):
    source = Path(args.spec).expanduser().resolve()
    if not source.is_file():
        print("ERROR: specification not found: %s" % source, file=sys.stderr)
        return 1
    if source.suffix.lower() != ".md":
        print("ERROR: the authoritative source must be a .md file: %s" % source, file=sys.stderr)
        return 1

    pandoc = find_tool("pandoc")
    if not pandoc:
        print("ERROR: Pandoc is missing. Install it with the user's approval, then retry.", file=sys.stderr)
        return 3

    formats = ("docx", "pdf") if args.format == "all" else (args.format,)
    engine = None
    if "pdf" in formats:
        engine = find_tool(args.pdf_engine)
        if not engine:
            print(
                "ERROR: PDF engine '%s' is missing. Install it with approval or select an installed engine with --pdf-engine."
                % args.pdf_engine,
                file=sys.stderr,
            )
            return 3

    reference_doc = None
    if args.reference_doc:
        if "docx" not in formats:
            print("ERROR: --reference-doc applies only when exporting DOCX.", file=sys.stderr)
            return 1
        reference_doc = Path(args.reference_doc).expanduser().resolve()
        if not reference_doc.is_file():
            print("ERROR: Word reference document not found: %s" % reference_doc, file=sys.stderr)
            return 1

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else source.parent
    outputs = {kind: output_dir / (source.stem + "." + kind) for kind in formats}
    existing = [str(path) for path in outputs.values() if path.exists()]
    if existing and not args.force:
        print("ERROR: export already exists; review it and obtain approval before replacing it:", file=sys.stderr)
        for path in existing:
            print("  %s" % path, file=sys.stderr)
        print("Use --force only after authorization.", file=sys.stderr)
        return 1

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print("ERROR: cannot create output directory %s: %s" % (output_dir, exc), file=sys.stderr)
        return 1
    failed = False
    for kind in formats:
        if not run_pandoc(pandoc, source, outputs[kind], kind, engine, reference_doc):
            failed = True
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description="Export Markdown ASIC IP specifications to DOCX/PDF with Pandoc.")
    sub = parser.add_subparsers(dest="action")
    exp = sub.add_parser("export", help="export a Markdown specification")
    exp.add_argument("spec", help="authoritative Markdown specification")
    exp.add_argument("--format", choices=("docx", "pdf", "all"), required=True)
    exp.add_argument("--output-dir", help="output directory (default: next to the Markdown source)")
    exp.add_argument("--reference-doc", help="optional Word DOCX style template (DOCX export only)")
    exp.add_argument("--pdf-engine", default="typst", help="installed Pandoc PDF engine (default: typst)")
    exp.add_argument("--force", action="store_true", help="replace existing exports; use only with authorization")
    args = parser.parse_args()
    if args.action != "export":
        parser.print_help()
        return 2
    return export(args)


if __name__ == "__main__":
    sys.exit(main())
