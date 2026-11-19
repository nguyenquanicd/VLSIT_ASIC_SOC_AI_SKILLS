#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rtl_strip.py
# Function : copy RTL with every comment removed, keeping every line number
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Copy Verilog/SystemVerilog files without comments, line for line (rule R-008).

Purpose : the analysis reads a comment-free copy, and every citation still points at
          the original file because each comment is replaced by spaces on the same line.
Usage   : vlsit_rtl_strip.py SRC --out WORK/rtl_nocomment [--ext .sv,.v] [--check]
          SRC is one file or one folder (recursive).
Output  : one line per file: "<path>: <n> lines -> <n> lines, <k> comments removed",
          then a RESULT line.
Exit    : 0 success, 1 error.
"""
import argparse
import sys
from pathlib import Path

DEFAULT_EXT = ('.sv', '.v', '.svh', '.vh')


def strip_text(text):
    """Return (text without comments, comment count); newlines are preserved exactly."""
    out = []
    index = 0
    comments = 0
    length = len(text)
    in_string = False
    while index < length:
        char = text[index]
        nxt = text[index + 1] if index + 1 < length else ''
        if in_string:
            out.append(char)
            if char == '\\' and nxt:
                out.append(nxt)
                index += 2
                continue
            if char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            out.append(char)
            index += 1
            continue
        if char == '/' and nxt == '/':
            comments += 1
            while index < length and text[index] != '\n':
                out.append(' ')
                index += 1
            continue
        if char == '/' and nxt == '*':
            comments += 1
            end = text.find('*/', index + 2)
            if end < 0:
                raise ValueError('unterminated block comment at offset %d' % index)
            for pos in range(index, end + 2):
                out.append('\n' if text[pos] == '\n' else ' ')
            index = end + 2
            continue
        out.append(char)
        index += 1
    return ''.join(out), comments


def collect(src, extensions):
    if src.is_file():
        return [src]
    files = []
    for suffix in extensions:
        files += sorted(src.rglob('*' + suffix))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('src', help='one RTL file or one folder')
    parser.add_argument('--out', required=True, help='folder for the comment-free copies')
    parser.add_argument('--ext', default=','.join(DEFAULT_EXT), help='comma separated extensions')
    parser.add_argument('--check', action='store_true', help='verify the copies and write nothing')
    args = parser.parse_args()

    src = Path(args.src)
    if not src.exists():
        print('ERROR: %s does not exist' % src)
        return 1
    out_root = Path(args.out)
    extensions = tuple(part.strip() for part in args.ext.split(',') if part.strip())

    files = collect(src, extensions)
    if not files:
        print('ERROR: no file with %s under %s' % (', '.join(extensions), src))
        return 1

    errors = 0
    total_comments = 0
    for path in files:
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            text = path.read_text(encoding='utf-8', errors='replace')
        try:
            cleaned, comments = strip_text(text)
        except ValueError as exc:
            print('ERROR: %s: %s' % (path, exc))
            errors += 1
            continue
        if cleaned.count('\n') != text.count('\n'):
            print('ERROR: %s: line count changed (%d -> %d)'
                  % (path, text.count('\n'), cleaned.count('\n')))
            errors += 1
            continue
        if args.check:
            if path.exists() is False:
                errors += 1
        else:
            relative = path.name if src.is_file() else path.relative_to(src)
            target = out_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(cleaned, encoding='utf-8')
        total_comments += comments
        print('%s: %d lines -> %d lines, %d comments removed'
              % (relative if src.is_dir() else path.name, text.count('\n'), cleaned.count('\n'), comments))

    print('RESULT: %d file(s), %d comments removed, %d error(s)'
          % (len(files), total_comments, errors))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
