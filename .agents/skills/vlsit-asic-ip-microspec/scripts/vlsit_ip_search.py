#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_ip_search.py
# Function : search public RTL repositories for silicon- or FPGA-proven IP and score the evidence
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Search public RTL repositories for IP that is proven on silicon or FPGA, and score the evidence.

Purpose : the skill only studies reference IP with evidence of ASIC tapeout or FPGA validation, a testbench and
          a licence (rule R-007). This script searches GitHub and Gitee, reads each README, and prints a short
          ranked table with the evidence found, so the assistant does not read whole repositories.
Actions :
  search QUERY [--source github|gitee|both] [--limit 10] [--lang Verilog|SystemVerilog]
  evaluate URL        score one README, repository or web page (any site, including Chinese pages)
Output  : one line per candidate: QUALIFIED/EXCLUDED, score, name, stars, licence, evidence tags, URL.
          Nothing is downloaded to disk. GITHUB_TOKEN (optional environment variable) raises the API limit.
Scoring : tapeout evidence (tapeout, MPW, ChipIgnite, Tiny Tapeout, silicon-proven; Chinese: liu pian) = 3,
          FPGA evidence (board names, Vivado, Quartus, bitstream) = 2, verification (testbench, UVM, cocotb,
          formal) = 1, ASIC flow (OpenLane, sky130, Design Compiler) = 1. QUALIFIED needs tapeout or FPGA
          evidence plus verification evidence plus a licence; everything else is EXCLUDED with the reason.
Exit    : 0 success, 1 error (message on the last line). Network access is required.
Standard library only; text is read as UTF-8.
Examples:
  vlsit_ip_search.py search "apb tilelink bridge" --source github --limit 8
  vlsit_ip_search.py evaluate https://gitee.com/owner/repo
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "vlsit-asic-ip-microspec/1.0", "Accept": "application/vnd.github+json"}
EVIDENCE = {
    "tapeout": (3, r"tape-?out|taped[- ]out|\bMPW\b|multi-project wafer|chipignite|openmpw|tiny ?tapeout|silicon[- ](?:proven|validated|verified)|fabricated|\bshuttle\b|流片|量产|硅验证|芯片回片"),
    "fpga": (2, r"\bFPGA\b|vivado|quartus|bitstream|\barty\b|nexys|basys|zynq|artix|kintex|cyclone|\bice40\b|\becp5\b|上板|开发板"),
    "verification": (1, r"testbench|\buvm\b|cocotb|verilator|symbiyosys|formal|coverage|\btb\b|仿真|验证"),
    "asic-flow": (1, r"openlane|openroad|sky130|gf180|design compiler|genus|innovus|综合|后端"),
}


def get(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers=headers or UA)
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def strip_html(text):
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))


def score(text, licence):
    tags, total = [], 0
    for name, (weight, pattern) in EVIDENCE.items():
        if re.search(pattern, text, flags=re.I):
            tags.append(name)
            total += weight
    ok = ("tapeout" in tags or "fpga" in tags) and "verification" in tags and bool(licence) and licence not in ("NOASSERTION", "none")
    reason = "" if ok else "missing: " + ", ".join(
        [x for x, c in (("tapeout-or-fpga evidence", "tapeout" in tags or "fpga" in tags), ("verification evidence", "verification" in tags), ("licence", bool(licence) and licence not in ("NOASSERTION", "none"))) if not c])
    return total, tags, ok, reason


def line(ok, total, name, stars, licence, tags, url, reason):
    return "%s | score %d | %s | stars %s | %s | %s | %s%s" % (
        "QUALIFIED" if ok else "EXCLUDED", total, name, stars, licence or "no licence", ",".join(tags) or "no evidence", url, "" if ok else " | " + reason)


def github(query, limit, lang):
    q = urllib.parse.quote("%s%s" % (query, " language:" + lang if lang else ""))
    data = json.loads(get("https://api.github.com/search/repositories?q=%s&sort=stars&per_page=%d" % (q, limit)))
    rows = []
    for repo in data.get("items", []):
        try:
            readme = get("https://api.github.com/repos/%s/readme" % repo["full_name"], {**UA, "Accept": "application/vnd.github.raw+json"})
        except urllib.error.URLError:
            readme = ""
        licence = (repo.get("license") or {}).get("spdx_id")
        total, tags, ok, reason = score(readme + " " + (repo.get("description") or "") + " " + " ".join(repo.get("topics", [])), licence)
        rows.append((ok, total, line(ok, total, repo["full_name"], repo["stargazers_count"], licence, tags, repo["html_url"], reason)))
    return rows


def gitee(query, limit):
    url = "https://gitee.com/api/v5/search/repositories?q=%s&per_page=%d&order=desc&sort=stars_count" % (urllib.parse.quote(query), limit)
    data = json.loads(get(url, {"User-Agent": UA["User-Agent"]}))
    rows = []
    for repo in data if isinstance(data, list) else []:
        branch = repo.get("default_branch") or "master"
        try:
            readme = get("https://gitee.com/%s/raw/%s/README.md" % (repo["full_name"], branch), {"User-Agent": UA["User-Agent"]})
        except urllib.error.URLError:
            readme = ""
        licence = repo.get("license")
        total, tags, ok, reason = score(readme + " " + (repo.get("description") or ""), licence)
        rows.append((ok, total, line(ok, total, repo["full_name"], repo.get("stargazers_count"), licence, tags, repo["html_url"], reason)))
    return rows


def action_search(a):
    rows, errors = [], []
    for source in (["github", "gitee"] if a.source == "both" else [a.source]):
        try:
            rows += github(a.query, a.limit, a.lang) if source == "github" else gitee(a.query, a.limit)
        except (urllib.error.URLError, ValueError, OSError) as exc:
            errors.append("%s: %s" % (source, exc))
    rows.sort(key=lambda r: (not r[0], -r[1]))
    for _, _, text in rows:
        print(text)
    for e in errors:
        print("WARNING: source failed (%s); ask the user to search it by hand or to supply a link" % e)
    print("%d candidate(s), %d qualified" % (len(rows), sum(1 for r in rows if r[0])))
    return 0 if rows or not errors else 1


def action_evaluate(a):
    try:
        text = get(a.url, {"User-Agent": "Mozilla/5.0 (vlsit-asic-ip-microspec)"})
    except (urllib.error.URLError, OSError) as exc:
        print("ERROR: cannot read %s: %s; the site may block scripts, ask the user to save the page" % (a.url, exc))
        return 1
    total, tags, ok, reason = score(strip_html(text), a.licence or "unknown-check-manually")
    print(line(ok, total, a.url, "?", a.licence or "unknown (check the page)", tags, a.url, reason))
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--source", choices=["github", "gitee", "both"], default="github")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--lang", default="")
    e = sub.add_parser("evaluate")
    e.add_argument("url")
    e.add_argument("--licence", help="licence you read on the page, if any")
    a = parser.parse_args()
    return {"search": action_search, "evaluate": action_evaluate}[a.action](a)


if __name__ == "__main__":
    sys.exit(main())
