#!/usr/bin/env python3
# Function: Fetch a selected public hardware IP archive and record its provenance.
# Author: VLSI Technology
# GitHub: https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
"""Fetch the public distribution of a selected IP project and record its provenance.

Purpose
    Implements the repeatable download steps of the workflow (OCI-030, OCI-040, OCI-041,
    OCI-042, OCI-060) for two kinds of source:
      * OpenCores projects, read from the anonymous public SVN HTTP view
        (https://opencores.org/ocsvn/<slug>/<slug>/trunk/). The OpenCores "download" button
        needs a login, so it is not used (OCI-023).
      * GitHub repositories, read from the public GitHub API and codeload archive of one
        exact commit.
    Before downloading project files, both fetch paths inspect the online file tree and refuse
    projects without a Verilog/SystemVerilog/VHDL HDL source file. Header-only trees
    do not qualify.
    The script only performs HTTP GET requests to the hosts above and writes only below the
    --out folder you give. It never executes downloaded code (OCI-032).

Usage
    python vlsit_fetch_ip.py oc-info  <slug> [<slug> ...]
    python vlsit_fetch_ip.py gh-info  <owner/repo> [<owner/repo> ...]
    python vlsit_fetch_ip.py oc-fetch <slug> --out <dest-folder> [--name <folder-name>]
    python vlsit_fetch_ip.py gh-fetch <owner/repo> --out <dest-folder> [--name <folder-name>]
                                      [--max-mb 300]

Inputs
    slug        OpenCores project slug, for example aes_core.
    owner/repo  GitHub repository, for example secworks/aes.
    --out       Existing destination folder (the IP's open_source folder). A subfolder per
                project is created; an existing subfolder is never overwritten (OCI-040).
    --max-mb    Refuse archives larger than this size (default 300 MB).

Outputs
    <out>/<name>/                  extracted tree (OpenCores: svn_trunk/ ; GitHub: repo tree)
    <out>/<name>/DOWNLOAD_INFO.md  provenance record (OCI-042)
    <out>/<name>/<name>.zip        archive (GitHub) or snapshot zip of the SVN tree (OpenCores)
    info subcommands print one JSON object per project to stdout.

Exit codes
    0 success, 1 download or integrity failure, 2 bad arguments or refused (exists, too big).
"""
import argparse
import datetime
import hashlib
import http.client
import shutil
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import PurePosixPath

LONG_PREFIX = chr(92) * 2 + "?" + chr(92)   # extended-length path prefix on Windows
UA = {"User-Agent": "Mozilla/5.0 (vlsit-opencore-ip-downloader)"}
TODAY = datetime.date.today().isoformat()
HDL_SOURCE_SUFFIXES = {".v", ".sv", ".vhd", ".vhdl"}


def has_hdl_source(path):
    """Return True for a Verilog/SystemVerilog/VHDL HDL source file."""
    normalized = path.replace("\\", "/")
    return PurePosixPath(normalized).suffix.lower() in HDL_SOURCE_SUFFIXES


def http_get(url, timeout=90, binary=False, tries=4):
    """GET with retries: the OpenCores host drops connections intermittently."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == tries - 1:
                raise
            time.sleep(3 * (attempt + 1))
        except (urllib.error.URLError, OSError, http.client.HTTPException):
            if attempt == tries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def long_path(path):
    """Windows extended-length path so deep trees (OpenTitan, Caliptra) do not hit MAX_PATH."""
    path = os.path.abspath(path)
    if os.name == "nt" and not path.startswith(LONG_PREFIX):
        return LONG_PREFIX + path
    return path


def extract_zip(z, proj):
    """Extract every member below proj after a traversal check (OCI-060)."""
    for info in z.infolist():
        dest = safe_join(proj, info.filename)
        if info.is_dir():
            os.makedirs(long_path(dest), exist_ok=True)
            continue
        os.makedirs(os.path.dirname(long_path(dest)), exist_ok=True)
        with z.open(info) as src, open(long_path(dest), "wb") as out:
            shutil.copyfileobj(src, out)


def safe_join(base, rel):
    """Join rel below base; refuse traversal (OCI-060)."""
    dest = os.path.normpath(os.path.join(base, rel))
    if os.path.commonpath([os.path.abspath(base), os.path.abspath(dest)]) != os.path.abspath(base):
        raise ValueError("unsafe path: " + rel)
    return dest


# ---------------------------------------------------------------- OpenCores

def oc_page_info(slug):
    html = http_get("https://opencores.org/projects/" + slug)
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("no project data found on the OpenCores page of " + slug)
    info = json.loads(m.group(1))["props"]["pageProps"]["info"]
    body = ""
    try:
        body = json.loads(m.group(1))["props"]["pageProps"]["pageInfo"]["body"]
    except Exception:
        pass
    def day(ts):
        return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d") if ts else None
    return {
        "slug": slug, "title": info.get("title", "").strip(), "category": info.get("category"),
        "language": info.get("language"), "stage": info.get("stage"), "license": info.get("license"),
        "created": day(info.get("created")), "updated": day(info.get("updated")),
        "svn_committed": day(info.get("committed")), "vcs": info.get("vcs"),
        "has_svn_files": info.get("hasSvnFiles"), "has_external_files": info.get("hasExternalFiles"),
        "maintainers": [x.get("title") for x in info.get("maintainers", [])],
        "page_url": "https://opencores.org/projects/" + slug, "description": body[:400],
    }


def oc_list(url, depth=0):
    """Yield (relative path, is_dir) from an SVN HTTP directory listing."""
    html = http_get(url)
    if depth > 12:
        return
    for href in re.findall(r'<li><a href="([^"]+)"', html):
        if href.startswith("..") or href.startswith("/") or "://" in href:
            continue
        name = urllib.parse.unquote(href)
        if name.endswith("/"):
            yield name, True
            for sub, isdir in oc_list(url + href, depth + 1):
                yield name + sub, isdir
        else:
            yield name, False


def oc_fetch(slug, out, name):
    info = oc_page_info(slug)
    base = "https://opencores.org/ocsvn/%s/%s/trunk/" % (slug, slug)
    root_html = http_get(base)
    rev = re.search(r"Revision (\d+)", root_html)
    rev = rev.group(1) if rev else "unknown"
    listing = list(oc_list(base))  # Read directory listings only; no project file is downloaded yet.
    rtl_files = [rel for rel, isdir in listing if not isdir and has_hdl_source(rel)]
    if not rtl_files:
        print("REFUSED: no Verilog/SystemVerilog/VHDL source file was found; no project files downloaded")
        return 2
    proj = os.path.join(out, name)
    if os.path.exists(proj):
        print("REFUSED: %s already exists" % proj)
        return 2
    tree = os.path.join(proj, "svn_trunk")
    os.makedirs(tree)
    files, total = [], 0
    for rel, isdir in listing:
        dest = safe_join(tree, rel)
        if isdir:
            os.makedirs(dest, exist_ok=True)
            continue
        data = http_get(base + urllib.parse.quote(rel), binary=True)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        files.append(rel)
        total += len(data)
        time.sleep(0.15)
        if len(files) > 6000 or total > 300 * 1024 * 1024:
            print("FAILED: project larger than the safety limit")
            return 1
    if not files:
        print("FAILED: no files listed in " + base)
        return 1
    snap = os.path.join(proj, name + "_svn_trunk_r%s.zip" % rev)
    with zipfile.ZipFile(snap, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in sorted(files):
            z.write(safe_join(tree, rel), "svn_trunk/" + rel)
    lic_files = [f for f in files if re.search(r"(^|/)(licen[sc]e|copying)[^/]*$", f, re.I)]
    write_info(proj, {
        "Project": info["title"] or slug, "Catalog URL": info["page_url"],
        "Upstream URL": base + " (OpenCores anonymous SVN, trunk)",
        "Download date": TODAY, "Revision": "SVN trunk revision " + rev,
        "License (OpenCores field)": info["license"] or "not declared on the OpenCores page",
        "License files in tree": ", ".join(lic_files) or "none found",
        "Archive": os.path.basename(snap) + " (snapshot zip of the downloaded tree, made by this script)",
        "SHA-256 of snapshot": sha256_file(snap),
        "Files": "%d files, %d bytes" % (len(files), total),
        "HDL source files": str(sum(1 for path in files if has_hdl_source(path))),
        "Language / stage": "%s / %s" % (info["language"], info["stage"]),
        "Not downloaded": "SVN tags and branches, bug tracker, forum, the login-only OpenCores download archive",
    })
    print("OK %s: %d files, revision %s, license field: %s" % (slug, len(files), rev, info["license"]))
    return 0


# ----------------------------------------------------------------- GitHub

def gh_api(path):
    return json.loads(http_get("https://api.github.com" + path))


def gh_info(repo):
    d = gh_api("/repos/" + repo)
    lic = d.get("license") or {}
    return {
        "repo": d["full_name"], "license": lic.get("spdx_id"), "license_name": lic.get("name"),
        "size_kb": d.get("size"), "default_branch": d.get("default_branch"),
        "pushed_at": d.get("pushed_at"), "archived": d.get("archived"), "fork": d.get("fork"),
        "stars": d.get("stargazers_count"), "language": d.get("language"),
        "description": d.get("description"), "html_url": d.get("html_url"),
    }


def gh_fetch(repo, out, name, max_mb):
    d = gh_info(repo)
    if d["fork"]:
        print("NOTE: %s is a fork; confirm it is not a duplicate of its upstream (OCI-013)" % repo)
    if (d["size_kb"] or 0) / 1024.0 > max_mb:
        print("REFUSED: repository size %.0f MB exceeds --max-mb %d" % (d["size_kb"] / 1024.0, max_mb))
        return 2
    sha = gh_api("/repos/%s/commits/%s" % (repo, d["default_branch"]))["sha"]
    tree_info = gh_api("/repos/%s/git/trees/%s?recursive=1" % (repo, sha))
    tree_paths = [item.get("path", "") for item in tree_info.get("tree", [])
                  if item.get("type") == "blob"]
    rtl_files = [path for path in tree_paths if has_hdl_source(path)]
    if not rtl_files:
        detail = "the GitHub tree is truncated" if tree_info.get("truncated") else "no HDL source file was found"
        print("REFUSED: %s; no repository archive downloaded" % detail)
        return 2
    proj = os.path.join(out, name)
    if os.path.exists(proj):
        print("REFUSED: %s already exists" % proj)
        return 2
    os.makedirs(proj)
    arc = os.path.join(proj, "%s_%s.zip" % (name, sha[:7]))
    data = http_get("https://codeload.github.com/%s/zip/%s" % (repo, sha), timeout=300, binary=True)
    with open(arc, "wb") as f:
        f.write(data)
    try:
        with zipfile.ZipFile(arc) as z:
            if z.testzip() is not None:
                raise zipfile.BadZipFile("corrupt member")
            names = z.namelist()
            for n in names:
                safe_join(proj, n)
            if not any(has_hdl_source(n) for n in names if not n.endswith("/")):
                print("FAILED: fetched archive has no Verilog/SystemVerilog/VHDL source; not extracted")
                return 1
            extract_zip(z, proj)
    except Exception as e:
        print("FAILED: archive check/extract: %s" % e)
        return 1
    top = names[0].split("/")[0]
    files = [n for n in names if not n.endswith("/")]
    lic_files = [n.split("/", 1)[1] for n in files if re.search(r"(^|/)(licen[sc]e|copying)[^/]*$", n, re.I)]
    write_info(proj, {
        "Project": d["repo"], "Catalog URL": "none (GitHub, external to OpenCores)",
        "Upstream URL": d["html_url"], "Download date": TODAY,
        "Revision": "commit %s on branch %s (pushed %s)" % (sha, d["default_branch"], d["pushed_at"]),
        "License (GitHub API)": "%s (%s)" % (d["license"], d["license_name"]),
        "License files in tree": ", ".join(lic_files) or "none found",
        "Archive": os.path.basename(arc) + " (GitHub codeload archive of the commit above)",
        "SHA-256 of archive": sha256_file(arc),
        "Files": "%d files, extracted to %s/" % (len(files), top),
        "HDL source files": str(sum(1 for path in files if has_hdl_source(path))),
        "Not downloaded": "git history, issues, pull requests, releases, git submodule contents (listed in .gitmodules if any)",
    })
    print("OK %s: %d files, commit %s, license %s" % (repo, len(files), sha[:7], d["license"]))
    return 0


def write_info(proj, fields):
    lines = ["# DOWNLOAD_INFO", ""]
    for k, v in fields.items():
        lines.append("- **%s:** %s" % (k, v))
    lines += ["", "Download-integrity record only. The RTL was not simulated, linted or synthesized (OCI-062).", ""]
    with open(os.path.join(proj, "DOWNLOAD_INFO.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["oc-info", "gh-info", "oc-fetch", "gh-fetch"])
    ap.add_argument("items", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--name")
    ap.add_argument("--max-mb", type=int, default=300)
    a = ap.parse_args()
    try:
        if a.cmd in ("oc-info", "gh-info"):
            for it in a.items:
                try:
                    r = oc_page_info(it) if a.cmd == "oc-info" else gh_info(it)
                except Exception as e:
                    r = {"item": it, "error": str(e)}
                print(json.dumps(r, ensure_ascii=False))
            return 0
        if not a.out or not os.path.isdir(a.out):
            print("ERROR: --out must be an existing folder")
            return 2
        if len(a.items) != 1:
            print("ERROR: fetch takes exactly one project")
            return 2
        item = a.items[0]
        name = a.name or re.sub(r"[^A-Za-z0-9._-]+", "_", item.split("/")[-1])
        existed = os.path.exists(os.path.join(a.out, name))
        rc = oc_fetch(item, a.out, name) if a.cmd == "oc-fetch" else gh_fetch(item, a.out, name, a.max_mb)
        if rc == 1 and not existed:
            shutil.rmtree(long_path(os.path.join(a.out, name)), ignore_errors=True)
            print("Removed the partial folder of the failed download")
        return rc
    except (urllib.error.URLError, OSError, ValueError, RuntimeError, http.client.HTTPException) as e:
        print("FAILED: %s" % e)
        if a.cmd in ("oc-fetch", "gh-fetch") and a.out and a.items:
            nm = a.name or re.sub(r"[^A-Za-z0-9._-]+", "_", a.items[0].split("/")[-1])
            tgt = os.path.join(a.out, nm)
            if os.path.isdir(tgt) and not os.path.exists(os.path.join(tgt, "DOWNLOAD_INFO.md")):
                shutil.rmtree(long_path(tgt), ignore_errors=True)
                print("Removed the partial folder of the failed download")
        return 1


if __name__ == "__main__":
    sys.exit(main())
