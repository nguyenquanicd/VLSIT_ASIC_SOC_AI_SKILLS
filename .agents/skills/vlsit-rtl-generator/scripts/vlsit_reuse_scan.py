#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_reuse_scan.py
# Function : list the modules of the reusable RTL library common_rtl and rank the ones that may already implement a function of a specification
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Find reusable modules of the library common_rtl for a specification (rule R-037).

Standard library only, Windows and Linux.

  vlsit_reuse_scan.py list [--lib DIR]
      Catalog of the library: module, folder, kind (top of a design, or wrapper / helper), parameters and the
      first sentence of the header description.

  vlsit_reuse_scan.py scan SPEC.md [--lib DIR] [--min-score N]
      Rank the modules whose name or header description share keywords with the specification (title, purpose,
      requirements, glossary). The result is a list of CANDIDATES for the question of rule R-037; it is a keyword
      match, so the person or the agent judges whether the function is really equivalent (ports, parameters,
      behavior) before the designer is asked.

--lib: the folder common_rtl of the repository VLSIT_RTL_Generator_AI_Model. When it is not given the script looks
for a folder common_rtl in the current folder and its parents, and in a folder VLSIT_RTL_Generator_AI_Model beside
them. Exit codes: 0 done (also when there is no candidate), 2 library or specification not found.
"""
import argparse
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {"verification", "lint", "waveforms", "figures", "research", "proto", "build", "sim_logs", "logs",
              "cell_tests", "lib_tests", "rtl_cells", "constraints", "rtl_v2", "__pycache__"}
STOP = set("""this that with from into when then than also each other more most such only used uses using have has
been being will shall must should could would their there which while where these those both over under same about
module modules design designs file files signal signals value values data input output block
blocks function functions parameter parameters bit bits one two zero all any not none the and for are its use""".split())
HINTS = {
    "synchronizer": {"sync", "synchronizer", "synchronizers", "cdc", "metastability", "crossing"},
    "reset": {"reset", "rst"},
    "fifo": {"fifo", "queue", "buffer"},
    "crc": {"crc", "checksum"},
    "bridge": {"bridge", "converter"},
    "tie": {"tie", "tie-off", "tieoff"},
}


# Abbreviations of the naming rule (NAM-08) and of the library module names, with their full words.
ABBR = {"rst": "reset", "sync": "synchronizer synchronous", "afifo": "asynchronous fifo", "sfifo": "synchronous fifo",
        "apbcdc": "apb asynchronous bridge", "mem": "memory", "wr": "write", "rd": "read", "ack": "acknowledge",
        "req": "request", "cdc": "crossing", "mst": "requester", "slv": "completer", "ptr": "pointer",
        "addr": "address", "cmd": "command", "ctrl": "control", "err": "error", "arb": "arbiter", "gnt": "grant",
        "mux": "multiplexer", "dec": "decoder", "enc": "encoder", "buf": "buffer", "cnt": "counter", "en": "enable"}


def find_lib(arg):
    if arg:
        p = Path(arg)
        return p if p.is_dir() else None
    here = Path.cwd().resolve()
    for base in [here] + list(here.parents):
        for cand in (base / "common_rtl", base / "VLSIT_RTL_Generator_AI_Model" / "common_rtl"):
            if cand.is_dir():
                return cand
    return None


def words(text):
    out = set()
    for w in re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", text.lower()):
        if w not in STOP:
            out.add(w)
    return out


def catalog(lib):
    mods = []
    for path in sorted(lib.rglob("*.sv")):
        rel = path.relative_to(lib)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        if rel.parts[0] == "000_Common" and "rtl_lib" not in rel.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = re.search(r"^\s*module\s+(\w+)", text, re.M)
        if not m:
            continue
        head = re.search(r"/\*(.*?)\*/", text, re.S)
        desc = ""
        if head:
            d = re.search(r"Description\s*:(.*)", head.group(1), re.S)
            desc = " ".join(x.strip(" *") for x in (d.group(1) if d else head.group(1)).splitlines()).strip()
        params = re.findall(r"parameter\s+(?:logic\s*\[[^\]]*\]\s*)?(PARA_\w+)", text)
        mods.append({"name": m.group(1), "path": rel.as_posix(), "desc": desc, "params": params, "text": text})
    names = {m["name"] for m in mods}
    for m in mods:
        inst = sum(1 for o in mods if o is not m and re.search(r"\b%s\b" % re.escape(m["name"]), o["text"]))
        m["kind"] = "top / standalone" if (m["name"].endswith("_top") or not inst) else "wrapper / helper"
    return mods


def first_sentence(desc, n=170):
    s = re.split(r"(?<=[a-z0-9\)])\.\s", desc, maxsplit=1)[0]
    return (s[:n] + "...") if len(s) > n else s


def score(mod, spec_words):
    """4 per keyword of the module name found in the specification, plus at most 6 for keywords of the header
    description, plus 3 for each function group (synchronizer, reset, fifo, crc, bridge, tie) shared by both."""
    name_words = words(mod["name"].replace("_", " "))
    for short in list(name_words):
        if short in ABBR:
            name_words |= set(ABBR[short].split())
    name_words -= {"vlsit"}
    name_hit = name_words & spec_words
    desc_hit = (words(mod["desc"]) & spec_words) - name_hit
    extra = 0
    for group in HINTS.values():
        if (group & name_words) and (group & spec_words):
            extra += 3
    return 4 * len(name_hit) + min(len(desc_hit), 6) + extra, sorted(name_hit) + sorted(desc_hit)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("list")
    a.add_argument("--lib")
    b = sub.add_parser("scan")
    b.add_argument("spec")
    b.add_argument("--lib")
    b.add_argument("--min-score", type=int, default=8)
    b.add_argument("--top", type=int, default=8, help="show at most this many candidates")
    args = ap.parse_args()
    lib = find_lib(args.lib)
    if lib is None:
        print("ERROR: library common_rtl not found; pass --lib <folder common_rtl> (ask the designer for the path)")
        sys.exit(2)
    mods = catalog(lib)
    if args.cmd == "list":
        print("library: %s (%d modules)" % (lib, len(mods)))
        for m in mods:
            print("%-32s %-18s %s" % (m["name"], m["kind"], m["path"]))
            print("    parameters: %s" % (", ".join(m["params"]) or "none"))
            print("    %s" % first_sentence(m["desc"]))
        return
    try:
        spec = Path(args.spec).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print("ERROR: cannot read %s: %s" % (args.spec, e))
        sys.exit(2)
    spec_words = words(spec)
    ranked = []
    for m in mods:
        s, hit = score(m, spec_words)
        if s >= args.min_score:
            ranked.append((s, m, hit))
    ranked.sort(key=lambda x: (-x[0], x[1]["name"]))
    print("library: %s (%d modules); specification: %s" % (lib, len(mods), args.spec))
    if not ranked:
        print("no candidate: no module of the library shares enough keywords with the specification (min score %d)" % args.min_score)
        print("RESULT: NO CANDIDATE")
        return
    for s, m, hit in ranked[:args.top]:
        print("score %2d  %-30s %-18s %s" % (s, m["name"], m["kind"], m["path"]))
        print("          keywords: %s" % ", ".join(hit[:12]))
        print("          parameters: %s" % (", ".join(m["params"][:6]) or "none"))
        print("          %s" % first_sentence(m["desc"]))
    print("RESULT: %d CANDIDATE(S) (%d shown): confirm that each is equivalent, then ask the designer (rule R-037)"
          % (len(ranked), min(len(ranked), args.top)))


if __name__ == "__main__":
    main()
