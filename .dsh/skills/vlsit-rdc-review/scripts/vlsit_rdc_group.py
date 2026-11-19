#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rdc_group.py
# Function : group violations by root cause and set a default verdict per group
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Merge the records of one root cause and propose one verdict per group (rule R-021, R-022).

Purpose : the raw count overstates the work; one path reported in three sections is one
          fix, and one missing synchroniser is one fix for every path it affects.
Usage   : vlsit_rdc_group.py violations_waived.json --out groups.json
Output  : the JSON file and the group table.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

VERDICTS = ('fix RTL', 'fix SDC', 'waive', 'not RDC')


def key_of(record):
    if record.get('from') and record.get('to'):
        return 'same_path', '%s -> %s' % (record['from'], record['to'])
    family = re.sub(r'[._-]?\d+$', '', record['rule'])
    return 'same_rule_family', family


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('violations')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    document = json.loads(Path(args.violations).read_text(encoding='utf-8'))
    buckets = {}
    for record in document['violations']:
        kind, key = key_of(record)
        buckets.setdefault((kind, key), []).append(record)

    groups, ungrouped = [], []
    for index, ((kind, key), members) in enumerate(sorted(buckets.items()), 1):
        sections = sorted({member.get('section', 'unknown') for member in members})
        waived = [member for member in members if member.get('waived')]
        if all(member.get('waived') for member in members):
            verdict = 'waive'
        elif members[0].get('from_reset') and members[0].get('from_reset') == members[0].get('to_reset'):
            verdict = 'not RDC'
        elif re.search(r'exception|constraint|false_path|clock_group', members[0]['rule'], re.I):
            verdict = 'fix SDC'
        else:
            verdict = 'fix RTL'
        group = {'id': 'G-%02d' % index, 'key': kind, 'root_cause_key': key,
                 'root_cause': ('one path reported in %d section(s)' % len(sections)) if len(members) > 1
                 else 'one path, one report',
                 'members': [member['id'] for member in members],
                 'rules': sorted({member['rule'] for member in members}),
                 'paths': sorted({member.get('path', '') for member in members}),
                 'sections': sections,
                 'waived': len(waived), 'active': len(members) - len(waived),
                 'verdict': verdict, 'mechanism': '', 'risk': '', 'invalidation': '',
                 'owner': '', 'sdc_command': ''}
        groups.append(group)
    family_count = {}
    for group in groups:
        family_count[group['root_cause_key']] = family_count.get(group['root_cause_key'], 0) + len(group['members'])
    for group in groups:
        if len(group['members']) == 1 and not group['sections']:
            ungrouped.append(group['id'])

    summary = {'schema': 'vlsit-rdc-groups/1', 'tool': document.get('tool', ''),
               'violations': len(document['violations']),
               'active': document.get('active', 0), 'waived': document.get('waived', 0),
               'groups': groups, 'ungrouped': ungrouped,
               'verdict_counts': {verdict: sum(1 for group in groups if group['verdict'] == verdict)
                                  for verdict in VERDICTS}}
    Path(args.out).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%-6s %-16s %-30s %-6s %-10s %s' % ('group', 'key', 'paths', 'n', 'verdict', 'sections'))
    for group in groups:
        print('%-6s %-16s %-30s %-6d %-10s %s' % (group['id'], group['key'],
                                                  group['paths'][0][:30] if group['paths'] else '-',
                                                  len(group['members']), group['verdict'],
                                                  ', '.join(group['sections'])[:30]))
    print('RESULT: %d violation(s) in %d group(s); verdicts %s; written %s'
          % (len(document['violations']), len(groups),
             ', '.join('%s=%d' % (key, value) for key, value in summary['verdict_counts'].items()), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
