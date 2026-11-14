#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_sdc_clocks.py
# Function : read the SDC alone and report clocks, groups and reset exceptions
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Build the clock and group model from the SDC without reading the RTL (rule R-011).

Purpose : the SDC is the statement of intent; reading it alone is what later exposes
          the reset domains it does not constrain.
Usage   : vlsit_sdc_clocks.py design.sdc --out rdc_sdc.json
Output  : the JSON file, the clock table, the group count and the reset exception count.
Exit    : 0 success, 1 error.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def strip_comments(text):
    return '\n'.join(line.split('#', 1)[0] for line in text.splitlines())


def names(collection):
    return re.findall(r'\[get_(?:ports|pins|clocks)\s+\{?([^\]\}]+)\}?\]', collection)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('sdc')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    path = Path(args.sdc)
    if not path.exists():
        print('ERROR: %s does not exist' % path)
        return 1
    text = strip_comments(path.read_text(encoding='utf-8', errors='replace'))
    lines = text.splitlines()

    clocks, groups, exceptions, exception_refs = [], [], [], []
    for index, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        created = re.match(r'create_clock\b(.*)', stripped)
        if created:
            name = re.search(r'-name\s+(\S+)', created.group(1))
            period = re.search(r'-period\s+([\d.]+)', created.group(1))
            clocks.append({'name': name.group(1) if name else '(unnamed line %d)' % index,
                           'period': period.group(1) if period else '',
                           'type': 'create', 'master': '', 'line': index})
            continue
        generated = re.match(r'create_generated_clock\b(.*)', stripped)
        if generated:
            name = re.search(r'-name\s+(\S+)', generated.group(1))
            master = re.search(r'-master_clock\s+(\S+)', generated.group(1))
            clocks.append({'name': name.group(1) if name else '(unnamed line %d)' % index,
                           'period': '', 'type': 'generated',
                           'master': master.group(1) if master else '', 'line': index})
            continue
        grouped = re.match(r'set_clock_groups\b(.*)', stripped)
        if grouped:
            body = grouped.group(1)
            parts = re.findall(r'-group\s+\{([^}]*)\}', body)
            async_flag = '-asynchronous' in body
            groups.append({'line': index, 'asynchronous': async_flag,
                           'groups': [names(part) or [part.strip()] for part in parts]})
            continue
        if re.match(r'set_(false_path|max_delay|min_delay|multicycle_path)\b', stripped):
            kind = re.match(r'set_(\w+)\b', stripped).group(1)
            objects = re.findall(r'\[(?:get_(?:ports|pins|clocks|nets)\s+\{?[^\]\}]*\}?)\]', stripped)
            exceptions.append({'kind': kind, 'line': index, 'text': stripped, 'objects': objects})
            if re.search(r'rst|reset', stripped, re.I):
                for found in names(stripped):
                    exception_refs.append({'name': found.strip(), 'line': index, 'text': stripped})

    document = {'schema': 'vlsit-cdc-sdc/1',
                'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'clocks': clocks, 'groups': groups, 'exceptions': exceptions,
                'exception_refs': exception_refs}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%-24s %-10s %-10s %s' % ('clock', 'type', 'period', 'line'))
    for clock in clocks:
        print('%-24s %-10s %-10s %d' % (clock['name'], clock['type'], clock['period'], clock['line']))
    for group in groups:
        print('clock group line %d: asynchronous=%s groups=%s'
              % (group['line'], group['asynchronous'], group['groups']))
    for ref in exception_refs:
        print('reset exception line %d: %s' % (ref['line'], ref['name']))
    print('RESULT: %d clock(s), %d clock group(s), %d exception(s), %d reset reference(s), written %s'
          % (len(clocks), len(groups), len(exceptions), len(exception_refs), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
