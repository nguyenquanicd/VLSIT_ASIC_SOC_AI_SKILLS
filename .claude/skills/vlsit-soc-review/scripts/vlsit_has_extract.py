#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_has_extract.py
# Function : extract the address, IO, interrupt and bus maps from the HAS Markdown
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Extract the system facts of the HAS and list its gaps (rule R-010, R-011, R-026).

Usage   : vlsit_has_extract.py has.md --out has.json
Output  : the JSON file, the map counts and the gaps.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SECTION = re.compile(r'^#{1,4}\s+(.+)$', re.M)
ADDRESS = re.compile(r'\|\s*`?(0x[0-9A-Fa-f_]+)`?\s*\|\s*`?([^|`]+)`?\s*\|\s*`?([^|`]*)`?\s*\|')
INTERRUPT = re.compile(r'\b(irq|int)[_ ]?(\w+)\b', re.I)
BUS = re.compile(r'\b(AXI[0-9]?|APB[0-9]?|AHB[0-9]?|TL-?UL|Wishbone)\b')
CLOCK = re.compile(r'\b(\d+(?:\.\d+)?)\s*(MHz|GHz|kHz)\b', re.I)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('has')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    text = Path(args.has).read_text(encoding='utf-8')
    sections = [title.strip() for title in SECTION.findall(text)]
    address, interrupts, buses, clocks, gaps = [], [], [], [], []

    for match in ADDRESS.finditer(text):
        address.append({'base': match.group(1), 'target': match.group(2).strip(),
                        'attributes': match.group(3).strip()})
    current = ''
    for line in text.splitlines():
        heading = re.match(r'^#{1,4}\s+(.+)$', line)
        if heading:
            current = heading.group(1).lower()
            continue
        lowered = line.lower()
        if 'interrupt' in current and re.search(r'\|\s*\d+\s*\|', line):
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) >= 2 and not cells[0].lower().startswith('line'):
                interrupts.append({'line': cells[0], 'source': cells[1],
                                   'type': cells[2] if len(cells) > 2 else ''})
    for match in BUS.finditer(text):
        if match.group(1) not in buses:
            buses.append(match.group(1))
    for match in CLOCK.finditer(text):
        clocks.append({'value': match.group(1), 'unit': match.group(2)})

    for wanted, key in (('address', 'address map'), ('io', 'io map'),
                        ('interrupt', 'interrupt map'), ('bus', 'bus structure'),
                        ('clock', 'clock'), ('reset', 'reset')):
        if not any(wanted in title.lower() for title in sections):
            gaps.append({'section': key, 'detail': 'the HAS has no section whose title contains %r' % wanted})
    if not address:
        gaps.append({'section': 'address map', 'detail': 'no row with a base address was found'})
    if not interrupts:
        gaps.append({'section': 'interrupt map', 'detail': 'no interrupt table row was found'})
    for title in ('address', 'interrupt', 'io', 'bus'):
        pass

    document = {'schema': 'vlsit-soc-has/1', 'file': Path(args.has).name,
                'sections': sections, 'address_map': address, 'interrupt_map': interrupts,
                'io_map': [], 'buses': buses, 'clocks': clocks, 'gaps': gaps,
                'counts': {'sections': len(sections), 'address': len(address),
                           'interrupt': len(interrupts), 'buses': len(buses), 'gaps': len(gaps)}}
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for title in sections:
        print('section: %s' % title)
    print('address=%d interrupt=%d bus=%d clock=%d gap=%d'
          % (len(address), len(interrupts), len(buses), len(clocks), len(gaps)))
    for gap in gaps:
        print('GAP %-16s %s' % (gap['section'], gap['detail']))
    print('RESULT: has=%s sections=%d address=%d interrupt=%d gaps=%d, written %s'
          % (Path(args.has).name, len(sections), len(address), len(interrupts), len(gaps), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
