#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rtl_scan.py
# Function : scan RTL for modules, ports, parameters, instances and always blocks
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Scan comment-free Verilog/SystemVerilog for the structure the skill needs (rule R-006, R-010).

Purpose : one JSON file holds every module with its ports, parameters, child instances
          with their connection map, the always blocks with their line range, the
          continuous assignments, and the parent map that fixes the top module.
Usage   : vlsit_rtl_scan.py WORK/rtl_nocomment --out scan.json [--ext .sv,.v]
Output  : the JSON file and a summary line per module plus the parent map.
Exit    : 0 success, 1 error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_EXT = ('.sv', '.v')
KEYWORDS = {
    'module', 'endmodule', 'input', 'output', 'inout', 'wire', 'logic', 'reg', 'signed',
    'unsigned', 'parameter', 'localparam', 'assign', 'always', 'always_comb', 'always_ff',
    'always_latch', 'begin', 'end', 'if', 'else', 'case', 'casez', 'casex', 'endcase',
    'default', 'for', 'while', 'generate', 'endgenerate', 'genvar', 'function', 'endfunction',
    'task', 'endtask', 'initial', 'posedge', 'negedge', 'or', 'and', 'not', 'int', 'bit',
    'typedef', 'enum', 'struct', 'packed', 'return', 'break', 'continue', 'unique', 'priority',
}


def match_paren(text, start, opening='(', closing=')'):
    """Index of the bracket that closes the one at start, or -1."""
    depth = 0
    index = start
    while index < len(text):
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return -1


def split_top(text, separator=','):
    """Split on a separator that is not nested in brackets or braces."""
    parts, depth, current = [], 0, []
    for char in text:
        if char in '([{':
            depth += 1
        elif char in ')]}':
            depth -= 1
        if char == separator and depth == 0:
            parts.append(''.join(current))
            current = []
        else:
            current.append(char)
    if ''.join(current).strip():
        parts.append(''.join(current))
    return [part.strip() for part in parts if part.strip()]


def parse_ports(header, line_offset):
    ports = []
    names = []
    for chunk in split_top(header):
        text = ' '.join(chunk.split())
        match = re.match(r'(input|output|inout)\b(.*)$', text)
        if match:
            direction = match.group(1)
            rest = match.group(2)
            width_match = re.search(r'\[\s*([^\]]+?)\s*\]', rest)
            width = width_match.group(1).strip() if width_match else '1'
            name_match = re.search(r'([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*$', rest.replace('[]', ''))
            if not name_match:
                continue
            name = name_match.group(1)
            names.append(name)
            ports.append({'name': name, 'direction': direction, 'width': width,
                          'line': None, 'description': ''})
        elif re.match(r'[A-Za-z_]\w*$', text) and names:
            names.append(text)
            ports.append({'name': text, 'direction': None, 'width': '', 'line': None, 'description': ''})
    return ports


def scan_file(path, text):
    modules = []
    for module_match in re.finditer(r'^\s*module\s+([A-Za-z_]\w*)', text, re.M):
        name = module_match.group(1)
        line = text.count('\n', 0, module_match.start()) + 1
        start = module_match.end()
        paren = text.find('(', start)
        end_header = text.find(';', start)
        header_end = end_header if end_header >= 0 else start
        header_text = ''
        if 0 <= paren < header_end:
            close = match_paren(text, paren)
            if close > 0:
                header_text = text[paren + 1:close]
                header_end = close
        body_start = text.find('\n', header_end)
        end_match = re.search(r'^\s*endmodule', text[body_start:], re.M)
        body_end = body_start + end_match.start() if end_match else len(text)
        body = text[body_start:body_end]
        base_line = text.count('\n', 0, body_start) + 1

        ports = parse_ports(header_text, base_line)
        known = {port['name'] for port in ports}
        params = []
        for param_match in re.finditer(r'^\s*(?:parameter|localparam)\s+(?:logic\s+)?(?:\[[^\]]*\]\s*)?(\w+)\s*=\s*([^;,\n]+)',
                                       body, re.M):
            params.append({'name': param_match.group(1), 'default': param_match.group(2).strip(),
                           'line': base_line + body.count('\n', 0, param_match.start())})

        for decl in re.finditer(r'^\s*(input|output|inout)\b\s*(?:wire|logic|reg)?\s*(?:signed)?\s*(\[[^\]]*\])?\s*([A-Za-z_]\w*)\s*[,;]',
                                body, re.M):
            if decl.group(3) in known:
                continue
            width = re.sub(r'[\[\]\s]', '', decl.group(2)) if decl.group(2) else '1'
            ports.append({'name': decl.group(3), 'direction': decl.group(1), 'width': width,
                          'line': base_line + body.count('\n', 0, decl.start()), 'description': ''})
            known.add(decl.group(3))

        instances = []
        for inst in re.finditer(r'^[ \t]*([A-Za-z_]\w*)\s*(#\s*\()?', body, re.M):
            module_name = inst.group(1)
            if module_name in KEYWORDS or module_name == name:
                continue
            cursor = inst.end() - 1 if inst.group(2) else inst.end()
            if inst.group(2):
                close_param = match_paren(body, cursor)
                if close_param < 0:
                    continue
                cursor = close_param + 1
            name_match = re.match(r'\s*([A-Za-z_]\w*)\s*\(', body[cursor:])
            if not name_match:
                continue
            inst_name = name_match.group(1)
            if inst_name in KEYWORDS:
                continue
            open_paren = cursor + name_match.end() - 1
            close_paren = match_paren(body, open_paren)
            if close_paren < 0:
                continue
            connections = []
            for piece in split_top(body[open_paren + 1:close_paren]):
                named = re.match(r'\.([A-Za-z_]\w*)\s*\(\s*([^)]*?)\s*\)', piece)
                if named:
                    connections.append({'port': named.group(1), 'signal': named.group(2).strip()})
                else:
                    connections.append({'port': None, 'signal': piece.strip()})
            instances.append({'name': inst_name, 'module': module_name,
                              'line': base_line + body.count('\n', 0, inst.start()),
                              'connections': connections})

        assigns = []
        for assign in re.finditer(r'\bassign\s+([^=;]+?)\s*=\s*([^;]+);', body, re.S):
            assigns.append({'line': base_line + body.count('\n', 0, assign.start()),
                            'lhs': ' '.join(assign.group(1).split()),
                            'rhs': ' '.join(assign.group(2).split())})

        always_comb, always_ff = [], []
        for block in re.finditer(r'^\s*(always_comb|always_ff|always_latch|always)\b', body, re.M):
            kind = block.group(1)
            start_index = block.start()
            line_start = base_line + body.count('\n', 0, start_index)
            cursor = block.end()
            body_match = re.match(r'[^\S\n]*@?\s*(\([^)]*\))?', body[cursor:])
            if body_match:
                cursor += body_match.end()
            tail = body[cursor:]
            begin = re.match(r'\s*begin\b', tail)
            if begin:
                depth = 1
                pos = cursor + begin.end()
                token_re = re.compile(r'\b(begin|end)\b')
                while depth and pos < len(body):
                    token = token_re.search(body, pos)
                    if not token:
                        break
                    depth += 1 if token.group(1) == 'begin' else -1
                    pos = token.end()
                line_end = base_line + body.count('\n', 0, pos)
                content = body[cursor + begin.end():pos - 3]
            else:
                semi = tail.find(';')
                pos = cursor + (semi + 1 if semi >= 0 else len(tail))
                line_end = base_line + body.count('\n', 0, pos)
                content = body[cursor:pos]
            entry = {'line_start': line_start, 'line_end': line_end,
                     'assignments': []}
            for assignment in re.finditer(r'([A-Za-z_]\w*(?:\s*\[[^\]]*\])?)\s*(<=|=(?!=))\s*([^;]+);', content):
                entry['assignments'].append({
                    'line': line_start + content.count('\n', 0, assignment.start()),
                    'lhs': ' '.join(assignment.group(1).split()),
                    'op': assignment.group(2),
                    'rhs': ' '.join(assignment.group(3).split())})
            (always_comb if kind in ('always_comb', 'always') and '@' not in kind else always_ff).append(entry)
        modules.append({'name': name, 'file': path.name, 'line': line,
                        'ports': ports, 'params': params, 'instances': instances,
                        'assigns': assigns, 'always_comb': always_comb, 'always_ff': always_ff,
                        'end_line': base_line + body.count('\n')})
    return modules


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('src', help='folder or file with the comment-free RTL')
    parser.add_argument('--out', required=True, help='scan JSON')
    parser.add_argument('--ext', default=','.join(DEFAULT_EXT), help='comma separated extensions')
    args = parser.parse_args()
    src = Path(args.src)
    if not src.exists():
        print('ERROR: %s does not exist' % src)
        return 1
    extensions = tuple(part.strip() for part in args.ext.split(',') if part.strip())
    files = [src] if src.is_file() else [p for suffix in extensions for p in sorted(src.rglob('*' + suffix))]
    if not files:
        print('ERROR: no RTL file under %s' % src)
        return 1

    modules, parents = [], {}
    for path in files:
        text = path.read_text(encoding='utf-8')
        found = scan_file(path, text)
        modules += found
        print('%s: %d module(s): %s' % (path.name, len(found), ', '.join(m['name'] for m in found)))
    names = {module['name'] for module in modules}
    for module in modules:
        for instance in module['instances']:
            if instance['module'] in names:
                parents.setdefault(instance['module'], module['name'])
    top_candidates = sorted(name for name in names if name not in parents)
    unknown = sorted({i['module'] for m in modules for i in m['instances']} - names)

    document = {'schema': 'vlsit-scan/1',
                'source': str(src),
                'files': [{'path': p.name, 'sha256': __import__('hashlib').sha256(p.read_bytes()).hexdigest()} for p in files],
                'modules': modules, 'parents': parents,
                'top_candidates': top_candidates, 'external_modules': unknown}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('parents: %s' % ', '.join('%s <- %s' % (k, v) for k, v in sorted(parents.items())))
    print('top candidates: %s' % ', '.join(top_candidates))
    if unknown:
        print('external modules (not in the scan): %s' % ', '.join(unknown))
    print('RESULT: %d file(s), %d module(s), %d top candidate(s), written %s'
          % (len(files), len(modules), len(top_candidates), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
