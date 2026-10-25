#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_skillkit.py
# Function : scaffold, validate and mirror skills in the VLSIT house format
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Scaffold, validate and mirror skills in the house format.

A skill in the house format has four parts: SKILL.md (workflow), rule.md
(mandatory rules with IDs), reference/ (background) and scripts/ (code).

Actions:
  new       create a skill folder from the templates in reference/templates.
            Refuses to touch a folder that already exists.
  validate  check one skill folder against the rules of this skill and print a
            short report. Messages carry the rule ID they enforce (R-NNN, see
            rule.md). Exit code 0 = PASS (no errors), 1 = FAIL.
  mirror    copy <repo>/.claude/skills/<name> to <repo>/.agents/skills/<name>
            so both tools find the same skill. With --check it only reports.

validate also looks for rules in rule.md that repeat or contradict each other.
It compares the wording of every pair: near-identical statements are ERRORs;
similar statements with opposite polarity (MUST vs MUST NOT) or heavy overlap
are listed as REVIEW pairs, which a person or the assistant must judge. Wording
cannot reveal two rules that say opposite things in different words.

Standard library only (Python 3.8 or later). Output is deliberately short: one
line per problem and one RESULT line.

Examples:
  vlsit_skillkit.py new --name vlsit-example --description "Does X. Use when the user asks for X." --with-script
  vlsit_skillkit.py validate .claude/skills/vlsit-example
  vlsit_skillkit.py mirror .claude/skills/vlsit-example
  vlsit_skillkit.py mirror .claude/skills/vlsit-example --check
"""
import argparse
import ast
import hashlib
import re
import shutil
import sys
from pathlib import Path

SKILL_HOME = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_HOME / "reference" / "templates"
# Default author and project link written into the header of every generated script (R-043).
# Change them here once; validate only requires that a header names an author and a GitHub link.
AUTHOR = "VLSI Technology"
GITHUB_URL = "https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS"
SCRIPT_PREFIX = "vlsit_"
HEADER_LINES = 40
FINDER = Path(__file__).resolve().parent / "vlsit_find_python.ps1"
FINDER_SH = Path(__file__).resolve().parent / "vlsit_find_python.sh"
FINDER_NAMES = ("vlsit_find_python.ps1", "vlsit_find_python.sh")
# Script kinds that must exist for both operating systems (R-040): Windows PowerShell and POSIX sh.
OS_PAIR = {".ps1": ".sh", ".sh": ".ps1"}

# The scaffold marks every blank to be filled with this text. It is built from two
# pieces so that this script does not flag itself.
MARKER_TEXT = "TO" + "DO(fill)"
MARKER_PATTERN = "TO" + r"DO\(fill\)"

SCRIPT_NAME_PATTERN = r"^vlsit_[a-z0-9_]+(\.[a-z0-9]+)?$"
# Files that keep their fixed names (R-042): the tools find a skill by SKILL.md, the house format names rule.md, README.md and
# LICENSE are conventional; anything under assets/ is third-party material kept verbatim.
FIXED_FILE_NAMES = {"SKILL.md", "rule.md", "README.md", "LICENSE", ".gitkeep"}
# rtl_example/ holds example RTL whose file name must equal its module name (the RTL rule HIE-01), so it cannot carry the prefix.
FIXED_FOLDERS = {"assets", "__pycache__", "rtl_example"}
FILE_PREFIX_PATTERN = r"^(vlsit|VLSIT)_[A-Za-z0-9_.-]+$"
SCRIPT_EXTENSIONS = {".ps1", ".sh", ".bat", ".cmd", ".js", ".mjs", ".ts", ".rb", ".pl", ".php", ".lua", ".vbs"}
ALLOWED_KEYS = ("name", "description", "compatibility", "license", "metadata")
STOP = set("""the and for that with from this are any each every only into has have when than then
them they their its was were been before after unless until also one all can may such which who what
how why per via must not never always does did but nor yet out own too very will shall""".split())


class SkillError(Exception):
    """A problem that stops the action with one message."""


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.reviews = []
        self.infos = []

    def add(self, level, rule, message):
        line = "%s %s %s" % (level, rule, message)
        {"ERROR": self.errors, "WARN": self.warnings, "REVIEW": self.reviews, "INFO": self.infos}[level].append(line)


def read_text(path):
    return Path(path).read_text(encoding="utf-8-sig")


def write_text(path, text):
    with open(str(path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def files_under(folder):
    return sorted(p for p in Path(folder).rglob("*") if p.is_file())


def relative(path, base):
    return Path(path).relative_to(base).as_posix()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------- frontmatter

def read_frontmatter(text):
    result = {"ok": False, "keys": {}, "order": [], "multi": set()}
    lines = text.splitlines()
    if len(lines) < 3 or lines[0] != "---":
        return result
    end = -1
    for i in range(1, len(lines)):
        if lines[i] == "---":
            end = i
            break
    if end < 0:
        return result
    result["ok"] = True
    current = None
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            current = match.group(1)
            result["keys"][current] = match.group(2).strip()
            result["order"].append(current)
        elif current and re.match(r"^\s+\S", line):
            result["multi"].add(current)
    return result


def check_name(report, skill_name, folder, prefix):
    if not skill_name:
        report.add("ERROR", "R-004", "name is missing in the frontmatter")
        return
    if len(skill_name) > 64:
        report.add("ERROR", "R-004", "name is %d characters; the limit is 64" % len(skill_name))
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", skill_name):
        report.add("ERROR", "R-004", "name '%s' must use lowercase letters, digits and single hyphens only" % skill_name)
    if folder and skill_name != folder:
        report.add("ERROR", "R-004", "name '%s' must equal the folder name '%s'" % (skill_name, folder))
    if prefix and not skill_name.startswith(prefix):
        report.add("ERROR", "R-004", "name '%s' must start with '%s' (use --prefix to change it)" % (skill_name, prefix))


def check_description(report, text, multi_line):
    block = bool(re.match(r"^[>|][+-]?$", text or ""))
    if multi_line or block:
        report.add("ERROR", "R-006", "description must be a single line, not a multi-line block")
        return
    if not text or not text.strip():
        report.add("ERROR", "R-006", "description is missing or empty")
        return
    if len(text) > 500:
        report.add("ERROR", "R-006", "description is %d characters; the limit is 500" % len(text))
    position = text.find(": ")
    if position >= 0:
        start = max(0, position - 15)
        report.add("ERROR", "R-007", "description contains a colon followed by a space, which breaks the header: '...%s...'" % text[start:start + 35])
    if not re.search(r"(?i)\b(use when|use this|use it when|when the user|whenever|if the user|triggers?)\b", text):
        report.add("WARN", "R-006", 'description does not say when to use the skill (for example "Use when the user ...")')


# --------------------------------------------------------------------- rules

def tokens(text):
    out = set()
    for word in re.sub(r"[^a-z0-9]+", " ", text.lower()).split():
        if len(word) < 3 or word in STOP:
            continue
        for suffix in ("ing", "ed", "es", "s"):
            if len(word) >= len(suffix) + 4 and word.endswith(suffix):
                word = word[: -len(suffix)]
                break
        out.add(word)
    return out


def get_rules(text, report):
    rules = []
    current = None
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r"^#{1,6}\s", line):
            if current:
                rules.append(current)
                current = None
            match = re.match(r"^###\s+(R-\d{3})(?:\s+(.*))?$", line)
            if match:
                current = {"id": match.group(1), "title": match.group(2) or "", "line": number, "body": []}
            elif re.match(r"^###\s", line):
                report.add("ERROR", "R-010", "rule.md line %d: a rule heading must look like '### R-001 Title', got '%s'" % (number, line))
        elif current is not None:
            current["body"].append(line)
    if current:
        rules.append(current)
    return rules


def shorten(text, limit=60):
    return text if len(text) <= limit else text[: limit - 3] + "..."


def check_rules(report, text):
    rules = get_rules(text, report)
    if not rules:
        report.add("ERROR", "R-010", 'rule.md contains no rule headings of the form "### R-001 Title"')
        return None
    seen = {}
    parsed = []
    for rule in rules:
        if rule["id"] in seen:
            report.add("ERROR", "R-010", "%s is used twice (lines %d and %d)" % (rule["id"], seen[rule["id"]], rule["line"]))
        else:
            seen[rule["id"]] = rule["line"]
        statement_lines = []
        has_why = has_check = False
        in_statement = True
        for body_line in rule["body"]:
            if re.match(r"^\s*-\s", body_line):
                in_statement = False
            if re.match(r"^\s*-\s*Why:\s*\S", body_line):
                has_why = True
            if re.match(r"^\s*-\s*Check:\s*\S", body_line):
                has_check = True
            if in_statement and body_line.strip():
                statement_lines.append(body_line.strip())
        statement = " ".join(statement_lines)
        if not statement:
            report.add("ERROR", "R-011", "%s has no statement" % rule["id"])
            continue
        if not re.match(r"^MUST( NOT)?\s+\S", statement):
            report.add("ERROR", "R-011", "%s statement must start with MUST or MUST NOT" % rule["id"])
        if not has_why:
            report.add("ERROR", "R-011", "%s has no '- Why:' line" % rule["id"])
        if not has_check:
            report.add("ERROR", "R-011", "%s has no '- Check:' line" % rule["id"])
        bare = re.sub(r"`[^`]*`", "", statement)  # words in `code spans` are mentions, not requirements
        if len(re.findall(r"\bMUST\b", bare)) > 1:
            report.add("WARN", "R-011", "%s uses MUST more than once; it may hold more than one requirement" % rule["id"])
        parsed.append({"id": rule["id"], "statement": statement, "negative": statement.startswith("MUST NOT"), "tokens": tokens(statement)})

    # Words that occur in many rules ("skill", "rule", "script" ...) say nothing about whether two
    # rules overlap, so they are dropped before comparing. Needs a reasonably long list to be meaningful.
    # The full word set is kept too: for rules about the same subject the common words are exactly
    # what shows the overlap, so a pair is measured on both sets and the higher similarity counts.
    for item in parsed:
        item["full"] = item["tokens"]
    if len(parsed) >= 8:
        frequency = {}
        for item in parsed:
            for word in item["tokens"]:
                frequency[word] = frequency.get(word, 0) + 1
        common = {word for word, count in frequency.items() if count >= max(4, len(parsed) * 0.2)}
        for item in parsed:
            item["tokens"] = item["tokens"] - common

    pairs = []
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            a, b = parsed[i], parsed[j]
            if a["id"] == b["id"]:
                continue
            inter = len(a["tokens"] & b["tokens"])
            union = len(a["tokens"]) + len(b["tokens"]) - inter
            smaller = min(len(a["tokens"]), len(b["tokens"]))
            jaccard = inter / union if union else 0.0
            contain = inter / smaller if smaller else 0.0
            full_inter = len(a["full"] & b["full"])
            full_union = len(a["full"]) + len(b["full"]) - full_inter
            jaccard = max(jaccard, full_inter / full_union if full_union else 0.0)
            opposite = a["negative"] != b["negative"]
            near = jaccard >= 0.7 or (smaller >= 5 and contain >= 0.85)
            # Opposite polarity is the riskier case, so it is flagged at a lower similarity.
            if opposite:
                close = jaccard >= 0.25 or (smaller >= 5 and contain >= 0.5)
            else:
                close = jaccard >= 0.35 or (smaller >= 5 and contain >= 0.6)
            if not near and not close:
                continue
            if near and opposite:
                kind = "conflict"
            elif near:
                kind = "duplicate"
            elif opposite:
                kind = "possible-conflict"
            else:
                kind = "possible-overlap"
            pairs.append((max(jaccard, contain * 0.8), jaccard, kind, a, b))
    for _score, jaccard, kind, a, b in sorted(pairs, key=lambda p: p[0], reverse=True):
        message = '%s vs %s %s (similarity %.2f): "%s" / "%s"' % (a["id"], b["id"], kind, jaccard, shorten(a["statement"]), shorten(b["statement"]))
        if kind in ("duplicate", "conflict"):
            report.add("ERROR", "R-012", message)
        elif len(report.reviews) < 12:
            report.add("REVIEW", "R-012", message)
    return parsed


# ------------------------------------------------------------ python scripts

def check_python_file(report, path, rel, allow, local_modules):
    try:
        tree = ast.parse(read_text(path), filename=str(path))
    except SyntaxError as error:
        report.add("ERROR", "R-021", "%s does not parse as Python: %s (line %s)" % (rel, error.msg, error.lineno))
        return
    found = []  # (line, message) so that problems are reported in line order
    stdlib = getattr(sys, "stdlib_module_names", None)
    third_party = {}
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module.split(".")[0]]
        for name in names:
            if stdlib is not None and name not in stdlib and name not in local_modules and name not in allow:
                third_party.setdefault(name, node.lineno)
    for name, line in third_party.items():
        found.append((line, "R-022", "%s line %d imports '%s', which is not in the standard library (pass --allow-package %s once the user has approved it)" % (rel, line, name, name)))
    if stdlib is None:
        report.add("INFO", "R-022", "this Python has no sys.stdlib_module_names (before 3.10), so imports in %s were not checked" % rel)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        keywords = {k.arg for k in node.keywords}
        if None in keywords:  # **kwargs: cannot tell
            continue
        func = node.func
        problem = None
        is_open = (isinstance(func, ast.Name) and func.id == "open") or (
            isinstance(func, ast.Attribute) and func.attr == "open" and isinstance(func.value, ast.Name) and func.value.id == "io")
        if is_open:
            mode = None
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
                mode = node.args[1].value
            elif len(node.args) >= 2:
                continue
            for k in node.keywords:
                if k.arg == "mode":
                    if isinstance(k.value, ast.Constant) and isinstance(k.value.value, str):
                        mode = k.value.value
                    else:
                        mode = "?"
            if mode == "?" or (mode is not None and "b" in mode):
                continue
            if "encoding" not in keywords and len(node.args) < 4:
                problem = "open()"
        elif isinstance(func, ast.Attribute) and func.attr in ("read_text", "write_text"):
            needed = 1 if func.attr == "read_text" else 2
            if "encoding" not in keywords and len(node.args) < needed:
                problem = func.attr + "()"
        if problem:
            found.append((node.lineno, "R-024", "%s line %d calls %s without an explicit encoding (use encoding='utf-8')" % (rel, node.lineno, problem)))
    for _line, rule, message in sorted(found):
        report.add("ERROR", rule, message)


# ------------------------------------------------------------------ script header

def check_header(report, path, rel):
    """R-043: the first lines of a script say what it does, who wrote it and where its GitHub page is."""
    head = "\n".join(read_text(path).splitlines()[:HEADER_LINES])
    missing = []
    if not re.search(r"(?im)^\W{0,6}(function|description)\s*:\s*\S+", head):
        missing.append("'Function:' (what the script does)")
    if not re.search(r"(?im)^\W{0,6}author\s*:\s*\S+", head):
        missing.append("'Author:'")
    if not re.search(r"(?im)^\W{0,6}github\s*:\s*https://github\.com/\S+", head):
        missing.append("'GitHub: https://github.com/...'")
    if missing:
        report.add("ERROR", "R-043", "%s needs a header in its first %d lines with %s" % (rel, HEADER_LINES, ", ".join(missing)))


# ------------------------------------------------------------------ validate

def read_approved_packages(path):
    """Names listed in scripts/vlsit_approved_packages.txt: one package per line, the first word of the line, '#' starts a
    comment (write there who approved the package and when). It records the user's approval of rule R-022 inside the skill."""
    names = []
    try:
        lines = read_text(path).splitlines()
    except OSError:
        return names
    for line in lines:
        word = line.split("#", 1)[0].strip().split()
        if word:
            names.append(word[0])
    return names


def run_validate(skill_path, prefix, allow):
    report = Report()
    path = Path(skill_path)
    if not path.is_dir():
        raise SkillError("Skill folder not found: %s" % skill_path)
    skill_dir = path.resolve()
    folder = skill_dir.name
    skill_file = skill_dir / "SKILL.md"
    rule_file = skill_dir / "rule.md"
    reference_dir = skill_dir / "reference"
    scripts_dir = skill_dir / "scripts"
    allow = list(allow) + read_approved_packages(scripts_dir / "vlsit_approved_packages.txt")

    # R-001 four parts
    if not skill_file.is_file():
        report.add("ERROR", "R-001", "SKILL.md is missing")
    if not rule_file.is_file():
        report.add("ERROR", "R-001", "rule.md is missing")
    for sub, label in ((reference_dir, "reference/"), (scripts_dir, "scripts/")):
        if not sub.is_dir():
            report.add("ERROR", "R-001", "%s is missing" % label)
            continue
        everything = files_under(sub)
        real = [p for p in everything if p.name != ".gitkeep"]
        if not everything:
            report.add("ERROR", "R-001", "%s holds no file (add a .gitkeep if it is intentionally empty)" % label)
        elif not real:
            report.add("INFO", "R-020", "%s is empty (only .gitkeep); confirm that no step is mechanical enough for a script and that no background material is needed" % label)
    if not skill_file.is_file():
        return report

    # R-002 no nested SKILL.md
    for nested in files_under(skill_dir):
        if nested.name.lower() == "skill.md" and nested != skill_file:
            report.add("ERROR", "R-002", "nested SKILL.md would be discovered as a second skill: %s" % relative(nested, skill_dir))

    # frontmatter
    if skill_file.read_bytes()[:3] == b"\xef\xbb\xbf":
        report.add("ERROR", "R-005", "SKILL.md starts with a byte-order mark; the frontmatter must be the very first line")
    skill = read_text(skill_file)
    fm = read_frontmatter(skill)
    if not fm["ok"]:
        report.add("ERROR", "R-005", 'SKILL.md must start with a "---" frontmatter block')
    else:
        for key in fm["order"]:
            if key not in ALLOWED_KEYS:
                report.add("ERROR", "R-005", "frontmatter key '%s' is not portable; allowed: %s" % (key, ", ".join(ALLOWED_KEYS)))
        check_name(report, fm["keys"].get("name", ""), folder, prefix)
        check_description(report, fm["keys"].get("description", ""), "description" in fm["multi"])
        if len(fm["keys"].get("compatibility", "")) > 500:
            report.add("ERROR", "R-005", "compatibility is longer than 500 characters")

    # R-016 size
    line_count = len(skill.splitlines())
    if line_count > 500:
        report.add("ERROR", "R-016", "SKILL.md has %d lines; move detail into reference/ to stay under 500" % line_count)

    # SKILL.md content
    if "rule.md" not in skill:
        report.add("ERROR", "R-014", "SKILL.md never mentions rule.md")
    if not re.search(r"(?i)\brule IDs?\b|\bby ID\b|R-\d{3}", skill):
        report.add("WARN", "R-015", "SKILL.md has no step that verifies the result against the rules by ID")
    precedence_words = r"(wins|overrides?|precedence|prevails?|priority|first)"
    if not re.search(r"(?i)\b%s\b.{0,80}rule\.md|rule\.md.{0,80}\b%s\b" % (precedence_words, precedence_words), skill):
        report.add("WARN", "R-013", "SKILL.md does not state that rule.md overrides it and the reference files")
    if not re.search(r"(?i)reply.{0,60}language", skill):
        report.add("WARN", "R-019", "SKILL.md does not tell the assistant to reply in the language the user uses")

    # rule.md
    rule = ""
    parsed = None
    if rule_file.is_file():
        rule = read_text(rule_file)
        if not re.search(r"(?i)\b(wins|overrides?|precedence|prevails?|priority)\b", rule):
            report.add("WARN", "R-013", "rule.md does not state that it overrides SKILL.md and the reference files")
        parsed = check_rules(report, rule)

    # the two main files: placeholders, neutrality
    main_files = (("SKILL.md", skill), ("rule.md", rule))
    for label, content in main_files:
        if not content:
            continue
        count = len(re.findall(MARKER_PATTERN, content))
        if count:
            report.add("ERROR", "R-031", "%s still has %d unfilled placeholder(s) (%s)" % (label, count, MARKER_TEXT))
        tool = re.search(r"(?i)(?<![./\\\w-])(claude|codex|anthropic|openai|chatgpt|copilot)(?![/\\\w-])", content)
        if tool:
            report.add("ERROR", "R-009", "%s names an AI tool ('%s'); keep SKILL.md and rule.md tool-neutral" % (label, tool.group(1)))
        own = re.search(r"(?m)(^|[\s`])[/$]" + re.escape(folder) + r"\b", content)
        if own:
            report.add("ERROR", "R-009", "%s contains a tool-specific invocation of the skill ('%s')" % (label, own.group(0).strip()))

    # rule ID citations
    if parsed is not None:
        known = {p["id"] for p in parsed}
        for label, content in main_files:
            for cited in sorted(set(re.findall(r"\bR-\d{3}\b", content))):
                if cited not in known:
                    report.add("ERROR", "R-010", "%s cites %s, which is not defined in rule.md" % (label, cited))

    # R-017 links and orphans
    corpus = skill + "\n" + rule
    if reference_dir.is_dir():
        for doc in files_under(reference_dir):
            if doc.suffix.lower() == ".md":
                corpus += "\n" + read_text(doc)
    targets = set()
    for target in re.findall(r"\]\(([^)\s]+)\)", skill):
        if re.match(r"^(https?:|mailto:|#)", target) or "<" in target:
            continue
        targets.add(target.split("#")[0])
    for target in re.findall(r"`((?:scripts|reference)[/\\][A-Za-z0-9_./\\-]*)`", skill):
        targets.add(target)
    for target in sorted(targets):
        if target and not (skill_dir / target.replace("\\", "/")).exists():
            report.add("ERROR", "R-017", "SKILL.md points to '%s', which does not exist" % target)
    for sub in (reference_dir, scripts_dir):
        if not sub.is_dir():
            continue
        for item in files_under(sub):
            if item.name == ".gitkeep":
                continue
            rel = relative(item, skill_dir)
            if item.name not in corpus and rel not in corpus:
                report.add("WARN", "R-017", "%s is not mentioned in SKILL.md or any reference document, so it will never be read or run" % rel)

    # R-042: every file of the skill carries the prefix, except the fixed names
    for item in files_under(skill_dir):
        rel_parts = item.relative_to(skill_dir).parts
        if item.name in FIXED_FILE_NAMES or item.suffix == ".pyc" or any(part in FIXED_FOLDERS for part in rel_parts[:-1]):
            continue
        if not re.match(FILE_PREFIX_PATTERN, item.name):
            report.add("ERROR", "R-042", "%s must be named with the prefix '%s'" % (relative(item, skill_dir), SCRIPT_PREFIX))

    # scripts
    if scripts_dir.is_dir():
        script_files = [p for p in files_under(scripts_dir) if p.name != ".gitkeep"]
        local_modules = {p.stem for p in script_files if p.suffix == ".py"} | {p.name for p in scripts_dir.iterdir() if p.is_dir()}
        for item in script_files:
            rel = relative(item, skill_dir)
            if "__pycache__" in item.parts or item.suffix == ".pyc":
                continue
            if item.name != "README.md":
                if not re.match(SCRIPT_NAME_PATTERN, item.name):
                    report.add("ERROR", "R-042", "%s must be named with the prefix '%s' and lowercase letters, digits and underscores only" % (rel, SCRIPT_PREFIX))
                if item.suffix in (".py", ".ps1", ".sh"):
                    check_header(report, item, rel)
            if item.suffix == ".py":
                check_python_file(report, item, rel, set(allow), local_modules)
            elif item.suffix in SCRIPT_EXTENSIONS and item.suffix not in OS_PAIR:
                report.add("WARN", "R-021", "%s is not Python; Python is the default runtime, so confirm the user asked for %s" % (rel, item.suffix))
            elif item.suffix in OS_PAIR and item.name not in FINDER_NAMES:
                report.add("WARN", "R-021", "%s is not Python; Python is the default runtime, so confirm the user asked for %s" % (rel, item.suffix))
            if item.suffix == ".ps1":
                text = read_text(item)
                bad = re.search(r"[^\x00-\x7f]", text)
                if bad:
                    report.add("ERROR", "R-025", "%s has a non-ASCII character at line %d (PowerShell 5.1 may misread it)" % (rel, text.count("\n", 0, bad.start()) + 1))
            if item.suffix == ".sh":
                raw = item.read_bytes()
                first = raw.splitlines()[0].decode("utf-8", "replace").strip() if raw else ""
                if b"\r" in raw:
                    report.add("ERROR", "R-041", "%s has Windows (CR) line endings; a shell script must use LF only" % rel)
                if first not in ("#!/bin/sh", "#!/usr/bin/env sh"):
                    report.add("ERROR", "R-041", "%s must start with '#!/bin/sh' (portable sh), got '%s'" % (rel, first))
                bashism = re.search(r"(?m)^[^#\n]*(\[\[|\bfunction\s+\w+\s*\(|\bsource\s)", raw.decode("utf-8", "replace"))
                if bashism:
                    report.add("WARN", "R-041", "%s may use a bash-only construct ('%s'); keep it POSIX sh" % (rel, bashism.group(1).strip()))
            if item.suffix in OS_PAIR:
                twin = item.with_suffix(OS_PAIR[item.suffix])
                if not twin.is_file():
                    report.add("ERROR", "R-040", "%s has no %s twin for the other operating system (%s)" % (rel, OS_PAIR[item.suffix], twin.name))
            if item.suffix in (".py", ".ps1", ".sh") and re.search(MARKER_PATTERN, read_text(item)):
                report.add("ERROR", "R-031", "%s still has unfilled placeholders (%s)" % (rel, MARKER_TEXT))
        if any(p.suffix == ".py" for p in script_files):
            for finder in FINDER_NAMES:
                if not (scripts_dir / finder).is_file():
                    report.add("ERROR", "R-023", "scripts are Python but scripts/%s is missing, so a machine without Python cannot be handled" % finder)
                elif finder not in skill:
                    report.add("ERROR", "R-023", "scripts are Python but SKILL.md never runs %s to locate Python first" % finder)
        if script_files and fm["ok"] and "compatibility" not in fm["keys"]:
            report.add("WARN", "R-028", "scripts exist but the frontmatter has no compatibility field; state the runtime, network access and installs they need")
    return report


# ----------------------------------------------------------------------- new

def render(template_name, values, with_script):
    text = read_text(TEMPLATE_DIR / template_name)
    flags = {"SCRIPTS": with_script, "NOSCRIPTS": not with_script}
    for flag, keep in flags.items():
        pattern = r"(?s)\{\{#%s\}\}\n(.*?)\{\{/%s\}\}\n" % (flag, flag)
        text = re.sub(pattern, (lambda m: m.group(1)) if keep else "", text)
    for key, value in values.items():
        text = text.replace(key, value)
    counter = [0]

    def renumber(_match):
        counter[0] += 1
        return "### %d. " % counter[0]

    text = re.sub(r"(?m)^### \d+\. ", renumber, text)
    return text.replace("\r\n", "\n")


def run_new(args):
    if not args.name:
        raise SkillError("new needs --name <skill-name>.")
    if not args.description:
        raise SkillError('new needs --description "<what the skill does and when to use it>".')
    report = Report()
    check_name(report, args.name, args.name, args.prefix)
    check_description(report, args.description, False)
    if report.errors:
        raise SkillError("; ".join(re.sub(r"^ERROR ", "", e) for e in report.errors))

    if args.root:
        skills_root = Path(args.root)
    else:
        cwd = Path.cwd()
        if not (cwd / ".claude").is_dir():
            raise SkillError("There is no .claude folder in %s. Run from the repository root or pass --root <skills folder>." % cwd)
        skills_root = cwd / ".claude" / "skills"
    target = skills_root / args.name
    if target.exists():
        raise SkillError("Skill folder already exists, nothing was changed: %s" % target)

    base = args.name[len(args.prefix):] if args.prefix and args.name.startswith(args.prefix) else args.name
    heading = args.title or (base.replace("-", " ")[:1].upper() + base.replace("-", " ")[1:])
    stem = base.replace("-", "_")
    script_name = (stem if stem.startswith(SCRIPT_PREFIX) else SCRIPT_PREFIX + stem) + ".py"
    values = {"{{NAME}}": args.name, "{{DESCRIPTION}}": args.description, "{{TITLE}}": heading, "{{SCRIPT}}": script_name,
              "{{AUTHOR}}": args.author or AUTHOR, "{{GITHUB}}": args.github or GITHUB_URL}

    made = []
    (target / "reference").mkdir(parents=True)
    (target / "scripts").mkdir(parents=True)
    write_text(target / "SKILL.md", render("vlsit_SKILL.md.tpl", values, args.with_script))
    made.append("SKILL.md")
    write_text(target / "rule.md", render("vlsit_rule.md.tpl", values, args.with_script))
    made.append("rule.md")
    write_text(target / "reference" / ".gitkeep", "")
    made.append("reference/.gitkeep")
    if args.with_script:
        write_text(target / "scripts" / script_name, render("vlsit_script.py.tpl", values, True))
        made.append("scripts/" + script_name)
        shutil.copyfile(str(FINDER), str(target / "scripts" / "vlsit_find_python.ps1"))
        made.append("scripts/vlsit_find_python.ps1")
        # copyfile keeps the LF endings and the executable bit is not needed: the script is run with "sh"
        shutil.copyfile(str(FINDER_SH), str(target / "scripts" / "vlsit_find_python.sh"))
        made.append("scripts/vlsit_find_python.sh")
    else:
        write_text(target / "scripts" / ".gitkeep", "")
        made.append("scripts/.gitkeep")
    print("Created %s" % target)
    print("  files: %s" % ", ".join(made))
    print("Next: replace every %s in SKILL.md, rule.md%s, then run validate." % (MARKER_TEXT, " and scripts/" + script_name if args.with_script else ""))
    return 0


# -------------------------------------------------------------------- mirror

def run_mirror(args):
    path = Path(args.path)
    if not path.is_dir():
        raise SkillError("Skill folder not found: %s" % args.path)
    skill_dir = path.resolve()
    skills_dir = skill_dir.parent
    claude_dir = skills_dir.parent
    if skills_dir.name != "skills" or claude_dir.name != ".claude":
        raise SkillError("mirror expects <repo>/.claude/skills/<name>, got: %s" % skill_dir)
    target = claude_dir.parent / ".agents" / "skills" / skill_dir.name

    changed = []
    for source in files_under(skill_dir):
        rel = source.relative_to(skill_dir)
        destination = target / rel
        if destination.is_file() and file_hash(destination) == file_hash(source):
            continue
        changed.append(rel.as_posix())
        if not args.check:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(str(source), str(destination))
    extra = []
    if target.is_dir():
        for item in files_under(target):
            if not (skill_dir / item.relative_to(target)).is_file():
                extra.append(item.relative_to(target).as_posix())
    verb = "out of sync" if args.check else "copied"
    for rel in changed:
        print("%s: %s" % (verb, rel))
    for rel in extra:
        print("only in .agents (left alone, delete by hand if stale): %s" % rel)
    if not changed and not extra:
        print("IN SYNC: .agents/skills/%s matches .claude/skills/%s" % (skill_dir.name, skill_dir.name))
    elif not changed:
        print("IN SYNC apart from the extra files listed above.")
    elif args.check:
        print("OUT OF SYNC: %d file(s). Run mirror without --check." % len(changed))
        return 1
    else:
        print("MIRRORED: %d file(s) copied to %s" % (len(changed), target))
    return 0


# ---------------------------------------------------------------------- main

def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="vlsit_skillkit.py", description="Scaffold, validate and mirror skills in the house format.")
    sub = parser.add_subparsers(dest="action", required=True)

    p_new = sub.add_parser("new", help="create a skill folder from the templates")
    p_new.add_argument("--name", help="skill name, for example vlsit-example")
    p_new.add_argument("--description", help="one-line description: what it does and when to use it")
    p_new.add_argument("--title", help="heading of SKILL.md (default: derived from the name)")
    p_new.add_argument("--root", help="skills folder to create the skill in (default: .claude/skills of the current folder)")
    p_new.add_argument("--prefix", default="vlsit-", help="required name prefix; pass an empty string to switch the check off")
    p_new.add_argument("--author", help="author written into the script headers (default: %s)" % AUTHOR)
    p_new.add_argument("--github", help="GitHub link written into the script headers (default: %s)" % GITHUB_URL)
    p_new.add_argument("--with-script", action="store_true", help="also create a starter Python script and the Python locators for Windows and Linux")

    p_val = sub.add_parser("validate", help="check a skill folder against the rules")
    p_val.add_argument("path", help="the skill folder")
    p_val.add_argument("--prefix", default="vlsit-", help="required name prefix; pass an empty string to switch the check off")
    p_val.add_argument("--allow-package", action="append", default=[], metavar="NAME", help="a third-party package the user approved (repeatable)")

    p_mir = sub.add_parser("mirror", help="copy a skill to .agents/skills")
    p_mir.add_argument("path", help="the skill folder under .claude/skills")
    p_mir.add_argument("--check", action="store_true", help="report differences, change nothing")

    args = parser.parse_args(argv)
    try:
        if args.action == "new":
            return run_new(args)
        if args.action == "mirror":
            return run_mirror(args)
        report = run_validate(args.path, args.prefix, args.allow_package)
        print("validate %s" % args.path)
        for line in report.errors + report.warnings + report.reviews + report.infos:
            print(line)
        verdict = "FAIL" if report.errors else "PASS"
        print("RESULT: %s (%d errors, %d warnings, %d review pairs)" % (verdict, len(report.errors), len(report.warnings), len(report.reviews)))
        if report.reviews:
            print("REVIEW pairs: judge each one; reword a rule if the two really overlap or conflict (rule R-012).")
        return 1 if report.errors else 0
    except SkillError as error:
        print("ERROR: %s" % error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
