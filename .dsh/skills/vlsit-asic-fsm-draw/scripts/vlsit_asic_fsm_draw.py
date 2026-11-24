#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_asic_fsm_draw.py
# Function : validate FSM inputs and publish draw.io, SVG, Markdown and HTML outputs
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Create an editable VLSIT finite-state-machine diagram and portable previews.

Actions:
  check                 report whether the bundled renderer and symbol library exist
  template [--out FILE] write or print an FSM JSON starter
  validate FILE         validate states, transitions and layout data
  build FILE            create .drawio, .svg, .md, .html and a layout report

Exit codes: 0 success, 1 validation or file error, 2 command-line usage error.
Standard library only. All text files use UTF-8. Existing outputs require --force.
"""
import argparse
import html
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


SKILL_DIR = Path(__file__).resolve().parent.parent
ENGINE = SKILL_DIR / "scripts" / "vlsit_fsm_diagram.py"
RENDERER = SKILL_DIR / "scripts" / "vlsit_drawio_to_svg.py"
LIBRARY_CHECKER = SKILL_DIR / "scripts" / "vlsit_library_symbols.py"
LIBRARY = SKILL_DIR / "reference" / "drawio" / "VLSIT_DRAWIO_LIB_V1.drawio.xml"


def run_engine(arguments):
    result = subprocess.run(
        [sys.executable, str(ENGINE)] + [str(item) for item in arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


def action_check(_args):
    missing = [str(path) for path in (ENGINE, RENDERER, LIBRARY_CHECKER, LIBRARY) if not path.is_file()]
    if sys.version_info < (3, 8):
        missing.insert(0, "Python 3.8 or later")
    if missing:
        print("NOT READY")
        for item in missing:
            print("missing: %s" % item)
        return 1
    print("READY: Python %d.%d and bundled FSM tools are available" % sys.version_info[:2])
    return 0


def action_template(args):
    result = subprocess.run(
        [sys.executable, str(ENGINE), "template"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        if result.stderr:
            sys.stderr.write(result.stderr)
        return result.returncode
    if args.out is None:
        sys.stdout.write(result.stdout)
        return 0
    output = Path(args.out)
    if output.exists() and not args.force:
        print("ERROR: %s already exists; pass --force to overwrite it" % output)
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(result.stdout)
    print("OK: wrote %s" % output)
    return 0


def action_validate(args):
    return run_engine(["check", args.spec])


def action_render(args):
    source = Path(args.drawio)
    if not source.is_file():
        print("ERROR: draw.io file not found: %s" % source)
        return 1
    out_dir = Path(args.out_dir)
    stem = source.stem
    svg_path = out_dir / (stem + ".svg")
    md_path = out_dir / (stem + ".md")
    html_path = out_dir / (stem + ".html")
    existing = [path for path in (svg_path, md_path, html_path) if path.exists()]
    if existing and not args.force:
        print("ERROR: output already exists: %s; pass --force to overwrite" % existing[0])
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, str(RENDERER), str(source), "--out", str(svg_path), "--force"]
    if args.page:
        command.extend(["--page", args.page])
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.returncode:
        return result.returncode
    try:
        svg_text = svg_path.read_text(encoding="utf-8")
    except OSError as error:
        print("ERROR: generated SVG is missing or unreadable: %s" % error)
        return 1
    source_link = os.path.relpath(source.resolve(), out_dir.resolve()).replace("\\", "/")
    title = args.page or stem
    md = "# %s\n\n![%s](<%s.svg>)\n\nSource: [%s](<%s>)\n" % (
        title, title, quote(stem), source.name, quote(source_link))
    page = "\n".join([
        "<!doctype html>", '<html lang="en">', "<head>", '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        "  <title>%s</title>" % html.escape(title, quote=True),
        "  <style>body{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#111}svg{max-width:100%;height:auto}</style>",
        "</head>", "<body>", "  <h1>%s</h1>" % html.escape(title),
        "  <figure>%s<figcaption>Source: <a href=\"%s\">%s</a></figcaption></figure>" %
        (svg_text, html.escape(quote(source_link), quote=True), html.escape(source.name)),
        "</body>", "</html>", "",
    ])
    with md_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(md)
    with html_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(page)
    print("OK: wrote %s" % md_path)
    print("OK: wrote %s" % html_path)
    return 0


def action_build(args):
    source = Path(args.spec)
    if not source.is_file():
        print("ERROR: FSM JSON not found: %s" % source)
        return 1
    try:
        spec = json.loads(source.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        print("ERROR: cannot read FSM JSON: %s" % error)
        return 1
    if not isinstance(spec, dict):
        print("ERROR: FSM JSON root must be an object")
        return 1
    out_name = spec.get("out_name", "vlsit_fsm_diagram.drawio")
    if not isinstance(out_name, str) or Path(out_name).name != out_name or Path(out_name).suffix.lower() != ".drawio":
        print("ERROR: out_name must be a simple .drawio filename without a directory")
        return 1
    stem = Path(out_name).stem
    if not stem or stem in (".", "..") or any(not (char.isalnum() or char in "_.-") for char in stem):
        print("ERROR: out_name may use only letters, digits, underscore, hyphen and period")
        return 1

    out_dir = Path(args.out_dir)
    expected = [
        out_dir / out_name,
        out_dir / (stem + ".json"),
        out_dir / (stem + ".svg"),
        out_dir / (stem + "_layout_report.txt"),
        out_dir / (stem + ".md"),
        out_dir / (stem + ".html"),
    ]
    existing = [path for path in expected if path.exists()]
    if existing and not args.force:
        print("ERROR: output already exists: %s; pass --force to overwrite" % existing[0])
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    command = ["build", source, "--out-dir", out_dir]
    if args.force:
        command.append("--force")
    code = run_engine(command)
    if code:
        return code

    svg_path = out_dir / (stem + ".svg")
    try:
        svg_text = svg_path.read_text(encoding="utf-8")
    except OSError as error:
        print("ERROR: rendered SVG is missing or unreadable: %s" % error)
        return 1
    title = str(spec.get("function", spec.get("page_name", "FSM")))
    initial = str(spec.get("initial", ""))
    reset = spec.get("reset", {})
    reset_signal = str(reset.get("signal", ""))
    reset_level = str(reset.get("active_level", ""))
    safe_title = html.escape(title, quote=True)
    safe_initial = html.escape(initial, quote=True)
    safe_reset = html.escape(reset_signal, quote=True)
    safe_reset_level = html.escape(reset_level, quote=True)
    continuation = spec.get("continuation")
    if continuation:
        entries = continuation.get("entries", [continuation])
        entry_text = "; ".join("%s -> %s" % (item["from_view"], item["entry"]) for item in entries)
        entry_line = "Continuation entry: `%s`." % entry_text.replace("`", "\\`")
        entry_line_html = "Continuation entry: <code>%s</code>." % html.escape(entry_text, quote=True)
    else:
        entry_line = "Reset entry: `%s` active-%s." % (reset_signal, reset_level)
        entry_line_html = "Reset entry: <code>%s</code> active-%s." % (safe_reset, safe_reset_level)
    md_title = title.replace("[", "\\[").replace("]", "\\]")
    md_lines = [
        "# FSM: %s" % md_title,
        "",
        "Initial state: `%s`" % initial.replace("`", "\\`"),
        "",
        entry_line,
        "",
        "![FSM: %s](<%s>)" % (md_title, quote(stem + ".svg")),
        "",
        "Sources: [%s.drawio](<%s>) | [%s.json](<%s>) | [%s_layout_report.txt](<%s>)" %
        (stem, quote(stem + ".drawio"), stem, quote(stem + ".json"), stem, quote(stem + "_layout_report.txt")),
    ]
    aliases = spec.get("condition_aliases", [])
    overrides = spec.get("global_overrides", [])
    if overrides:
        md_lines.extend(["", "## Global next-state overrides", ""])
        for item in overrides:
            md_lines.append("- `%s`: `%s -> %s`; guard: `%s`" % (
                item["id"], item["source"], item["destination"],
                str(item["expression"]).replace("`", "\\`")))
            if item.get("note"):
                md_lines.append("  %s" % item["note"])
    if aliases or overrides:
        md_lines.extend(["", "## Transition and global state control mapping", "",
                         "| Kind | Label / effect | Boolean expression |", "|---|---|---|"])
        for alias in aliases:
            label = str(alias["label"]).replace("|", "\\|")
            expression = str(alias["expression"]).replace("|", "\\|").replace("\n", "<br>")
            md_lines.append("| Transition | %s | `%s` |" % (label, expression.replace("`", "\\`")))
        for item in overrides:
            effect = "%s: %s -> %s" % (item["id"], item["source"], item["destination"])
            expression = str(item["expression"]).replace("|", "\\|").replace("\n", "<br>")
            md_lines.append("| Global control | %s | `%s` |" % (effect, expression.replace("`", "\\`")))
    md = "\n".join(md_lines) + "\n"
    page_lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        "  <title>FSM: %s</title>" % safe_title,
        "  <style>body{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#111}svg{max-width:100%;height:auto}a{color:#1457a6}</style>",
        "</head>",
        "<body>",
        "  <h1>FSM: %s</h1>" % safe_title,
        "  <p>Initial state: <code>%s</code></p>" % safe_initial,
        "  <p>%s</p>" % entry_line_html,
        "  <figure>%s<figcaption>Editable source: <a href=\"%s.drawio\">%s.drawio</a> | <a href=\"%s.json\">%s.json</a></figcaption></figure>" %
        (svg_text, html.escape(stem, quote=True), safe_title, html.escape(stem, quote=True), safe_title),
    ]
    if overrides:
        page_lines.append("  <section><h2>Global Next-State Control</h2><ul>")
        for item in overrides:
            effect = html.escape("%s: %s -> %s" % (item["id"], item["source"], item["destination"]))
            expression = html.escape(str(item["expression"]))
            note = " <span>%s</span>" % html.escape(str(item["note"])) if item.get("note") else ""
            page_lines.append("    <li><code>%s</code>; guard <code>%s</code>%s</li>" % (effect, expression, note))
        page_lines.append("  </ul></section>")
    if aliases or overrides:
        page_lines.extend([
            "  <section><h2>Transition and Global State Control Mapping</h2><table><thead><tr><th>Kind</th><th>Label / effect</th><th>Boolean expression</th></tr></thead><tbody>",
        ])
        for alias in aliases:
            label = html.escape(str(alias["label"]))
            expression = html.escape(str(alias["expression"])).replace("\n", "<br>")
            page_lines.append("    <tr><td>Transition</td><td>%s</td><td><code>%s</code></td></tr>" % (label, expression))
        for item in overrides:
            effect = html.escape("%s: %s -> %s" % (item["id"], item["source"], item["destination"]))
            expression = html.escape(str(item["expression"])).replace("\n", "<br>")
            page_lines.append("    <tr><td>Global control</td><td>%s</td><td><code>%s</code></td></tr>" % (effect, expression))
        page_lines.append("  </tbody></table></section>")
    page_lines.extend([
        "</body>",
        "</html>",
    ])
    page = "\n".join(page_lines) + "\n"
    with (out_dir / (stem + ".md")).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(md)
    with (out_dir / (stem + ".html")).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(page)
    print("OK: wrote %s" % (out_dir / (stem + ".md")))
    print("OK: wrote %s" % (out_dir / (stem + ".html")))
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("check", help="report whether the bundled tools are ready")
    template = sub.add_parser("template", help="print or save a starter FSM JSON")
    template.add_argument("--out", help="write the starter JSON to this path")
    template.add_argument("--force", action="store_true", help="overwrite an existing template file")
    validate = sub.add_parser("validate", help="validate an FSM JSON file")
    validate.add_argument("spec")
    render = sub.add_parser("render", help="convert an existing draw.io page to SVG, Markdown and HTML")
    render.add_argument("drawio")
    render.add_argument("--page", help="draw.io page name or 1-based index")
    render.add_argument("--out-dir", default="figures", help="output directory (default: figures)")
    render.add_argument("--force", action="store_true", help="overwrite existing rendered outputs")
    build = sub.add_parser("build", help="generate draw.io, SVG, Markdown and HTML")
    build.add_argument("spec")
    build.add_argument("--out-dir", default="figures", help="output directory (default: figures)")
    build.add_argument("--force", action="store_true", help="overwrite existing generated outputs")
    args = parser.parse_args()
    return {
        "check": action_check,
        "template": action_template,
        "validate": action_validate,
        "render": action_render,
        "build": action_build,
    }[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
