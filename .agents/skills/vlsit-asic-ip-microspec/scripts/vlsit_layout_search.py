#!/usr/bin/env python3
"""Run the diagram generator over many parameter sets and rank the results (RHD-097).

Purpose : progressive search for the arrangement with the fewest crossings, then the smallest maximum
          crossings per connector, then the fewest bends, then the smallest frame, without hand-running
          each case. Rejected: failed routes, unplaced labels, findings, any connector with more than
          5 bends, or more than 2 connectors with exactly 5 bends.
Usage   : python vlsit_layout_search.py SPEC.json PARAM_FILE WORK_DIR [--top N] [--generator PATH]
          PARAM_FILE : one parameter set per line as VAR=value pairs (GAPH, GAPV, SEED and any variant
                       variable named in the spec, for example FACSIDE=B RRDSIDE=L); blank lines and
                       lines starting with # are ignored.
          WORK_DIR   : receives run_N/ folders with the generated diagrams and ranking.txt.
Output  : the ranking table on stdout (best first): crossings, max crossings per connector, bends,
          frame ratio, frame area, parameters, folder. Nothing outside WORK_DIR is written.
Exit    : 0 success, 2 usage error. Only the Python standard library is used.
"""
import argparse
import os
import re
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec")
    ap.add_argument("params")
    ap.add_argument("work")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--generator", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "vlsit_drawio_frame_diagram.py"))
    args = ap.parse_args()
    if not (os.path.isfile(args.spec) and os.path.isfile(args.params) and os.path.isfile(args.generator)):
        print("error: spec, parameter file or generator not found", file=sys.stderr)
        return 2
    os.makedirs(args.work, exist_ok=True)
    rows = []
    with open(args.params, encoding="utf-8") as fh:
        lines = [l.strip() for l in fh if l.strip() and not l.lstrip().startswith("#")]
    for n, line in enumerate(lines, 1):
        env = dict(os.environ)
        env.update(dict(item.split("=", 1) for item in line.split() if "=" in item))
        folder = os.path.join(args.work, f"run_{n}")
        done = subprocess.run([sys.executable, "-I", args.generator, args.spec, folder], env=env,
                              capture_output=True, text=True)
        score = next((l for l in done.stdout.splitlines() if l.startswith("SCORE ")), "")
        kv = dict(re.findall(r"(\w+)=(\S+)", score))
        if not kv or kv.get("failed") != "0" or kv.get("unplaced") != "0" or kv.get("issues") != "0" \
                or kv.get("bend_gt5") != "0" or int(kv.get("bend5", 0)) > 2:
            continue
        w, h = (int(float(v)) for v in kv["frame"].split("x"))
        rows.append((int(kv["cross_total"]), int(kv["cross_max_per_connector"]), int(kv["bends"]),
                     w / h, w * h, line, f"run_{n}"))
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[4]))
    with open(os.path.join(args.work, "ranking.txt"), "w", encoding="utf-8") as out:
        for r in rows:
            out.write(f"{r[0]} {r[1]} {r[2]} {r[3]:.2f} {r[4]} | {r[5]} | {r[6]}\n")
    print("columns: crossings | max crossings per connector | bends | frame ratio | frame area | parameters | folder")
    for r in rows[:args.top]:
        print(f"{r[0]} {r[1]} {r[2]} {r[3]:.2f} {r[4]} | {r[5]} | {r[6]}")
    if not rows:
        print("no parameter set produced an acceptable diagram")
    return 0


if __name__ == "__main__":
    sys.exit(main())
