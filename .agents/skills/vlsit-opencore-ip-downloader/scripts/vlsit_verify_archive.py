#!/usr/bin/env python3
# Function: Check archive integrity and member-path safety before extraction.
# Author: VLSI Technology
# GitHub: https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
"""Check a downloaded .zip/.tar* archive before extraction and record its SHA-256.

Checks: archive integrity, unsafe member paths, escaping links, license/README files,
and at least one Verilog/SystemVerilog/VHDL source (.v, .sv, .vhd, .vhdl).
Header-only archives do not qualify as HDL projects.
The script only reads the archive; it never extracts or executes anything.
Uses only the Python standard library.

Usage: python vlsit_verify_archive.py <ARCHIVE> [--json]
Exit code: 0 = no blocking finding, 1 = integrity or path-safety failure, 2 = usage error.
"""

import argparse
import hashlib
import json
import posixpath
import sys
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

LICENSE_HINTS = ("license", "licence", "copying", "copyright")
README_HINTS = ("readme",)
HDL_SOURCE_SUFFIXES = {".v", ".sv", ".vhd", ".vhdl"}


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unsafe_path(name):
    """Return a reason string when a member name could escape the extraction root."""
    normalized = name.replace("\\", "/")
    if normalized.startswith("/") or (len(normalized) > 1 and normalized[1] == ":"):
        return "absolute path"
    if ".." in posixpath.normpath(normalized).split("/"):
        return "parent-directory traversal"
    return None


def inspect_zip(path):
    findings, names, file_names = [], [], []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad is not None:
            findings.append(f"integrity failure: first bad member is '{bad}'")
        for info in archive.infolist():
            names.append(info.filename)
            if not info.is_dir():
                file_names.append(info.filename)
            reason = unsafe_path(info.filename)
            if reason:
                findings.append(f"unsafe member '{info.filename}': {reason}")
    return findings, names, file_names


def inspect_tar(path):
    findings, names, file_names = [], [], []
    with tarfile.open(path) as archive:
        for member in archive:  # iterating forces a full stream read, which detects truncation
            names.append(member.name)
            if member.isfile():
                file_names.append(member.name)
            reason = unsafe_path(member.name)
            if reason:
                findings.append(f"unsafe member '{member.name}': {reason}")
            if member.issym() or member.islnk():
                base = posixpath.dirname(member.name)
                target = member.linkname if member.islnk() else posixpath.join(base, member.linkname)
                if unsafe_path(target):
                    findings.append(f"link '{member.name}' -> '{member.linkname}' escapes the archive root")
            if member.isdev():
                findings.append(f"device member '{member.name}'")
    return findings, names, file_names


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("archive")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    args = parser.parse_args()

    path = Path(args.archive)
    if not path.is_file():
        print(f"error: '{path}' is not a file", file=sys.stderr)
        return 2

    try:
        if zipfile.is_zipfile(path):
            kind, (findings, names, file_names) = "zip", inspect_zip(path)
        elif tarfile.is_tarfile(path):
            kind, (findings, names, file_names) = "tar", inspect_tar(path)
        else:
            print("error: unsupported archive type (expected zip or tar)", file=sys.stderr)
            return 2
    except (zipfile.BadZipFile, tarfile.TarError, OSError, EOFError) as exc:
        kind, names, file_names, findings = "unknown", [], [], [f"integrity failure: {exc}"]

    lowered = [posixpath.basename(n.replace("\\", "/")).lower() for n in names]
    hdl_sources = [n for n in file_names if PurePosixPath(n.replace("\\", "/")).suffix.lower() in HDL_SOURCE_SUFFIXES]
    if not hdl_sources:
        findings.append("no Verilog/SystemVerilog/VHDL source file found; header-only archives do not qualify")
    result = {
        "archive": str(path),
        "type": kind,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_of(path),
        "member_count": len(names),
        "has_license_file": any(b.startswith(LICENSE_HINTS) for b in lowered),
        "has_readme_file": any(b.startswith(README_HINTS) for b in lowered),
        "hdl_source_count": len(hdl_sources),
        "blocking_findings": findings,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            if key != "blocking_findings":
                print(f"{key}: {value}")
        print("blocking_findings: " + ("none" if not findings else ""))
        for finding in findings:
            print(f"  - {finding}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
