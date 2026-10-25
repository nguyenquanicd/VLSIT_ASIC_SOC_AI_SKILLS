#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_doc_to_md.py
# Function : convert a standard document (DOCX, HTML, Markdown, text) to a verbatim Markdown file and verify it
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Convert a standard document (DOCX, HTML, Markdown, text) to a verbatim Markdown file with a protocol header.

Purpose : builds the files of reference/md_doc/. The body keeps the wording of the source; only the layout is
          mapped to Markdown (headings, lists, tables, code). PDF input is handled by vlsit_pdf_to_md.py.
Usage   : vlsit_doc_to_md.py convert SOURCE --protocol NAME --revision REV --source-url URL --license LICENSE
              [--out reference/md_doc/NAME.md] [--notes "text"|--notes-file FILE] [--force]
          vlsit_doc_to_md.py verify SOURCE MARKDOWN      compare word counts of the source and the Markdown body
Output  : a Markdown file with a YAML header (protocol, revision, source, license, date, sha256 of the source,
          converter), a "Key notes" block, and the body between BEGIN/END VERBATIM markers; one result line.
Exit    : 0 success, 1 error (message on the last line), 2 usage error.

Standard library only. Text files are read and written as UTF-8.
Examples:
  vlsit_doc_to_md.py convert README.md --protocol "TileLink UL (OpenTitan)" --revision "master @ 1a2b3c4" \
      --source-url https://raw.githubusercontent.com/... --license Apache-2.0 --out md_doc/opentitan_tlul.md
  vlsit_doc_to_md.py verify UM10204.docx md_doc/i2c_um10204.md
"""
import argparse
import hashlib
import html.parser
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

BEGIN = "<!-- BEGIN VERBATIM SOURCE -->"
END = "<!-- END VERBATIM SOURCE -->"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def words(text):
    return len(re.findall(r"\w+", text, flags=re.UNICODE))


# ----------------------------------------------------------------------------- DOCX

def docx_text(node):
    out = []
    for el in node.iter():
        if el.tag == W + "t" and el.text:
            out.append(el.text)
        elif el.tag in (W + "tab",):
            out.append("\t")
        elif el.tag in (W + "br", W + "cr"):
            out.append("\n")
    return "".join(out)


def docx_to_md(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    lines = []

    def table(tbl):
        rows = []
        for tr in tbl.findall(W + "tr"):
            rows.append([docx_text(tc).replace("\n", "<br>").replace("|", "\\|").strip() for tc in tr.findall(W + "tc")])
        if not rows:
            return
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        lines.append("| " + " | ".join(rows[0]) + " |")
        lines.append("|" + "---|" * width)
        for r in rows[1:]:
            lines.append("| " + " | ".join(r) + " |")
        lines.append("")

    for el in body:
        if el.tag == W + "tbl":
            table(el)
        elif el.tag == W + "p":
            text = docx_text(el).strip()
            if not text:
                continue
            style = el.find(W + "pPr/" + W + "pStyle")
            name = (style.get(W + "val") if style is not None else "") or ""
            m = re.match(r"(?i)heading\s*(\d)", name) or re.match(r"(?i)title", name)
            if m and m.groups():
                lines += ["#" * min(int(m.group(1)), 6) + " " + text, ""]
            elif m:
                lines += ["# " + text, ""]
            elif el.find(W + "pPr/" + W + "numPr") is not None:
                lines.append("- " + text)
            else:
                lines += [text, ""]
    return "\n".join(lines).strip() + "\n"


# ----------------------------------------------------------------------------- HTML

class HtmlToMd(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.row, self.cell, self.rows, self.in_pre = [], 0, None, None, [], False
        self.href = None

    def text_target(self, data):
        if self.cell is not None:
            self.cell.append(data)
        else:
            self.out.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head"):
            self.skip += 1
        elif self.skip:
            return
        elif re.fullmatch(r"h[1-6]", tag):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag in ("p", "div", "br"):
            self.out.append("\n\n" if tag != "br" else "\n")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag == "pre":
            self.in_pre = True
            self.out.append("\n\n```\n")
        elif tag == "table":
            self.rows = []
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell = []
        elif tag == "code" and not self.in_pre:
            self.out.append("`")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head"):
            self.skip = max(0, self.skip - 1)
        elif self.skip:
            return
        elif re.fullmatch(r"h[1-6]", tag) or tag == "p":
            self.out.append("\n\n")
        elif tag == "pre":
            self.in_pre = False
            self.out.append("\n```\n\n")
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()).replace("|", "\\|"))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        elif tag == "table" and self.rows:
            width = max(len(r) for r in self.rows)
            rows = [r + [""] * (width - len(r)) for r in self.rows]
            md = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
            md += ["| " + " | ".join(r) + " |" for r in rows[1:]]
            self.out.append("\n\n" + "\n".join(md) + "\n\n")
            self.rows = []
        elif tag == "code" and not self.in_pre:
            self.out.append("`")

    def handle_data(self, data):
        if self.skip:
            return
        self.text_target(data if self.in_pre else re.sub(r"\s+", " ", data))


def html_to_md(path):
    parser = HtmlToMd()
    parser.feed(Path(path).read_text(encoding="utf-8", errors="replace"))
    text = "".join(parser.out)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


# ----------------------------------------------------------------------------- document

def source_body(path):
    suffix = Path(path).suffix.lower()
    if suffix in (".md", ".markdown", ".txt"):
        return Path(path).read_text(encoding="utf-8")
    if suffix == ".docx":
        return docx_to_md(path)
    if suffix in (".html", ".htm"):
        return html_to_md(path)
    raise ValueError("unsupported input %s (PDF input: use vlsit_pdf_to_md.py)" % suffix)


def build_document(body, protocol, revision, source, licence, src_sha, converter, notes, redistribution="unknown"):
    header = ["---",
              'protocol: "%s"' % protocol, 'revision: "%s"' % revision, 'source: "%s"' % source,
              'license: "%s"' % licence, 'redistribution: "%s"' % redistribution,
              "retrieved: %s" % date.today().isoformat(), 'source_sha256: "%s"' % src_sha,
              'converter: "%s"' % converter, "---", "",
              "# %s - revision %s" % (protocol, revision), "",
              "> **Key notes (written by the converter operator, not part of the source):**"]
    for line in (notes or "none recorded").splitlines():
        header.append("> - " + line.strip().lstrip("-").strip())
    header += ["", "> The text between the markers below is the source text, converted without rewording.", "",
               BEGIN, "", body.rstrip("\n"), "", END, ""]
    return "\n".join(header)


def verbatim_part(md_text):
    if BEGIN not in md_text or END not in md_text:
        raise ValueError("markers not found")
    return md_text.split(BEGIN, 1)[1].split(END, 1)[0]


def action_convert(args):
    src = Path(args.source)
    if not src.is_file():
        print("ERROR: source not found: %s" % src)
        return 1
    out = Path(args.out) if args.out else Path("md_doc") / (src.stem + ".md")
    if out.exists() and not args.force:
        print("ERROR: %s already exists; pass --force to overwrite it" % out)
        return 1
    try:
        body = source_body(src)
    except (ValueError, OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        print("ERROR: %s" % exc)
        return 1
    notes = Path(args.notes_file).read_text(encoding="utf-8") if args.notes_file else args.notes
    doc = build_document(body, args.protocol, args.revision, args.source_url, args.license, sha256(src),
                         "vlsit_doc_to_md.py", notes, args.redistribution)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print("OK: wrote %s (%d words in body, source sha256 %s...)" % (out, words(body), sha256(src)[:12]))
    return 0


def action_verify(args):
    try:
        body = verbatim_part(Path(args.markdown).read_text(encoding="utf-8"))
        src_words = words(source_body(args.source))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print("ERROR: %s" % exc)
        return 1
    md_words = words(body)
    diff = abs(src_words - md_words) / max(src_words, 1)
    print("%s: source %d words, markdown %d words, difference %.2f%%" % ("OK" if diff < 0.01 else "CHECK", src_words, md_words, diff * 100))
    return 0 if diff < 0.01 else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    conv = sub.add_parser("convert")
    conv.add_argument("source")
    conv.add_argument("--protocol", required=True)
    conv.add_argument("--revision", required=True)
    conv.add_argument("--source-url", "--source", dest="source_url", required=True,
                      help="where the document was obtained (URL or title)")
    conv.add_argument("--license", required=True, help="licence as observed, e.g. Apache-2.0 or 'vendor click-through'")
    conv.add_argument("--redistribution", default="unknown", choices=["allowed", "forbidden", "unknown"])
    conv.add_argument("--notes", default="")
    conv.add_argument("--notes-file")
    conv.add_argument("--out")
    conv.add_argument("--force", action="store_true")
    ver = sub.add_parser("verify")
    ver.add_argument("source")
    ver.add_argument("markdown")
    args = parser.parse_args()
    return {"convert": action_convert, "verify": action_verify}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
