#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rtl_deep_check.py
# Function : deep static checks on synthesizable RTL beyond the rule checker
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Find the defects a lint run alone does not explain: latch, case default, mixed
assignment styles, multiple drivers, reset without a synchroniser and unreset state.

Usage   : vlsit_rtl_deep_check.py RTL_DIR --out deep_check.json [--pattern FILE]
Output  : one line per finding with file:line and severity, then RESULT.
Exit    : 0 no error, 1 error found or bad input.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FINDINGS = []


def add(severity, rule, file, line, message, fix):
    FINDINGS.append({'severity': severity, 'rule': rule, 'file': file, 'line': line,
                     'message': message, 'fix': fix})


def check_file(path):
    text = path.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    always_blocks = []
    for match in re.finditer(r'(always_comb|always_ff|always_latch)\b', text):
        line = text.count('\n', 0, match.start()) + 1
        kind = match.group(1)
        tail = text[match.end():]
        begin = re.match(r'\s*(@\s*\([^)]*\))?\s*begin\b', tail)
        if begin:
            depth, position = 1, match.end() + begin.end()
            token = re.compile(r'\b(begin|end)\b')
            while depth:
                found = token.search(text, position)
                if not found:
                    break
                depth += 1 if found.group(1) == 'begin' else -1
                position = found.end()
            body = text[match.end() + begin.end():position - 3]
            end_line = text.count('\n', 0, position)
        else:
            semi = tail.find(';')
            body = tail[:semi + 1]
            end_line = line
        always_blocks.append({'kind': kind, 'line': line, 'end': end_line, 'body': body,
                              'sensitivity': begin.group(1) if begin and begin.group(1) else ''})

    for block in always_blocks:
        body = block['body']
        if block['kind'] == 'always_comb':
            if re.search(r'\bcase\b', body) and not re.search(r'\bdefault\b', body):
                add('High', 'DEEP-01', path.name, block['line'],
                    'always_comb with a case and no default: a latch is inferred',
                    'add a default item that assigns every output of the block')
            first = re.search(r'^\s*([A-Za-z_]\w*)\s*=', body, re.M)
            if first and re.search(r'\bif\b|\bcase\b', body):
                name = first.group(1)
                if not re.search(r'^\s*%s\s*=\s*[^=]' % re.escape(name), body, re.M):
                    add('High', 'DEEP-02', path.name, block['line'],
                        'always_comb assigns %s without an unconditional default' % name,
                        'assign the default value first, before the if or case')
        if block['kind'] == 'always_ff':
            if re.search(r'^\s*[A-Za-z_]\w*\s*=(?!=)', body, re.M):
                add('High', 'DEEP-03', path.name, block['line'],
                    'always_ff with a blocking assignment',
                    'use <= for every sequential assignment')
            if not re.search(r'\bif\s*\(\s*!\s*[A-Za-z_]\w*\s*\)|negedge|posedge\s+\w*rst', block['sensitivity']):
                add('Medium', 'DEEP-04', path.name, block['line'],
                    'always_ff without a reset in its sensitivity list',
                    'add the asynchronous reset or reset the register synchronously and say why')
        if block['kind'] == 'always_latch':
            add('Critical', 'DEEP-05', path.name, block['line'],
                'always_latch is not allowed in synthesizable VLSIT RTL',
                'replace the latch by an explicit register or a full assignment')

    assignments = {}
    for match in re.finditer(r'^\s*([A-Za-z_]\w*)\s*<=\s*(.+);', text, re.M):
        line = text.count('\n', 0, match.start()) + 1
        owner = next((block['line'] for block in always_blocks if block['line'] <= line <= block['end']), line)
        assignments.setdefault(match.group(1), []).append((owner, line))
    for name, places in assignments.items():
        if len({owner for owner, _ in places}) > 1:
            add('High', 'DEEP-06', path.name, places[1][1],
                'signal %s is driven by %d always blocks' % (name, len({owner for owner, _ in places})),
                'keep one driver per signal and merge the branches into one always_ff')
    code = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    code = '\n'.join(line.split('//', 1)[0] for line in code.splitlines())
    for match in re.finditer(r'\b([A-Za-z_]\w*)\s*/\s*[A-Za-z_(]', code):
        line_text = code.splitlines()[code.count('\n', 0, match.start())]
        if 'http' in line_text or '`' in line_text:
            continue
        add('Low', 'DEEP-07', path.name, code.count('\n', 0, match.start()) + 1,
            'division in RTL: the synthesizer will infer a divider',
            'confirm the divider is intended, or replace it by a shift when the divisor is a power of two')

    resets = set(re.findall(r'negedge\s+([A-Za-z_]\w*)', text))
    for reset in resets:
        chain = re.findall(r'^\s*[A-Za-z_]\w*\s*<=\s*%s\s*;' % re.escape(reset), text, re.M)
        if not chain:
            add('Medium', 'DEEP-08', path.name, text.count('\n', 0) + 1,
                'reset %s drives flops without a visible two-flop synchroniser' % reset,
                'add a reset synchroniser in the destination clock domain (async assert, sync deassert)')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('rtl')
    parser.add_argument('--out', required=True)
    parser.add_argument('--pattern', default='*.sv,*.v')
    args = parser.parse_args()
    root = Path(args.rtl)
    if not root.exists():
        print('ERROR: %s does not exist' % root)
        return 1
    extensions = [part.strip() for part in args.pattern.split(',') if part.strip()]
    files = [root] if root.is_file() else [p for pattern in extensions for p in sorted(root.rglob(pattern))]
    if not files:
        print('ERROR: no RTL file under %s' % root)
        return 1
    for path in files:
        check_file(path)
    severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    FINDINGS.sort(key=lambda item: (severity_order[item['severity']], item['file'], item['line']))
    Path(args.out).write_text(json.dumps({'files': [p.name for p in files],
                                          'counts': {level: sum(1 for f in FINDINGS if f['severity'] == level)
                                                     for level in severity_order},
                                          'findings': FINDINGS}, indent=2) + '\n', encoding='utf-8')
    for finding in FINDINGS:
        print('%-8s %-8s %s:%d  %s' % (finding['severity'], finding['rule'],
                                       finding['file'], finding['line'], finding['message']))
    counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    for finding in FINDINGS:
        counts[finding['severity']] += 1
    print('RESULT: %d finding(s) Critical=%d High=%d Medium=%d Low=%d, written %s'
          % (len(FINDINGS), counts['Critical'], counts['High'], counts['Medium'], counts['Low'], args.out))
    return 1 if counts['Critical'] or counts['High'] else 0


if __name__ == '__main__':
    sys.exit(main())
