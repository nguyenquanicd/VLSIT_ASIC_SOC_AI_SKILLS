#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_library_symbols.py
# Function : inspect, clone and validate symbols of the bundled VLSIT draw.io library
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Inspect, clone, and validate symbols from the bundled VLSIT draw.io library."""

import argparse
import base64
import copy
import hashlib
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from html.parser import HTMLParser
from pathlib import Path


LIBRARY = Path(__file__).resolve().parent.parent / 'reference' / 'drawio' / 'VLSIT_DRAWIO_LIB_V1.drawio.xml'
EDITABLE = {
    'fontSize', 'fontColor', 'strokeColor', 'fillColor', 'strokeWidth',
    'dashed', 'dashPattern', 'align', 'verticalAlign', 'whiteSpace', 'overflow',
    'labelPosition', 'verticalLabelPosition', 'spacing', 'spacingTop',
    'spacingBottom', 'spacingLeft', 'spacingRight', 'entryX', 'entryY',
    'entryDx', 'entryDy', 'exitX', 'exitY', 'exitDx', 'exitDy',
    'entryPerimeter', 'exitPerimeter', 'jumpStyle', 'jumpSize',
}
BLACK = {'black', '#000000', '#000'}
WHITE = {'white', '#ffffff', '#fff'}


def style_map(style):
    result = {}
    for part in (style or '').split(';'):
        if part:
            key, separator, value = part.partition('=')
            result[key] = value if separator else None
    return result


def load_library():
    raw = LIBRARY.read_bytes()
    document = ET.fromstring(raw)
    if document.tag != 'mxlibrary':
        raise ValueError('Expected an mxlibrary document.')
    entries = json.loads(document.text or '')
    prototypes = []
    for entry in entries:
        model = ET.fromstring(entry['xml'])
        if model.tag != 'mxGraphModel' or model.find('root') is None:
            raise ValueError('Invalid library template model.')
        cells = {cell.get('id'): cell for cell in model.find('root')}
        if any(cell.tag != 'mxCell' for cell in cells.values()):
            raise ValueError('Unsupported library cell structure.')
        prototypes.append({key: cell for key, cell in cells.items() if key not in {'0', '1'}})
    return hashlib.sha256(raw).hexdigest().upper(), prototypes


def clone_template(digest, prototypes, entry, instance, label=None):
    if not 0 <= entry < len(prototypes):
        raise ValueError('Library entry index is out of range.')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', instance):
        raise ValueError('Instance must start with a letter and contain only letters, digits, _, or -.')
    template = prototypes[entry]
    model = ET.Element('mxGraphModel')
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')
    identifiers = {old: instance + '__' + old for old in template}
    visible = [old for old, cell in template.items() if cell.get('vertex') == '1' and 'group' not in style_map(cell.get('style'))]
    if label is not None and len(visible) != 1:
        raise ValueError('A label override requires a template with exactly one non-group vertex.')
    for old, original in template.items():
        cell = copy.deepcopy(original)
        cell.set('id', identifiers[old])
        for key in ('parent', 'source', 'target'):
            if cell.get(key) in identifiers:
                cell.set(key, identifiers[cell.get(key)])
        cell.set('vlsit_library_sha256', digest)
        cell.set('vlsit_library_entry', str(entry))
        cell.set('vlsit_library_cell', old)
        cell.set('vlsit_library_instance', instance)
        style = style_map(cell.get('style'))
        transparent = 'group' in style or 'text' in style
        style.update(fontSize='18', fontColor='#000000')
        style.setdefault('strokeColor', 'none' if transparent else '#000000')
        style.setdefault('fillColor', 'none' if transparent else '#FFFFFF')
        cell.set('style', ';'.join(key if value is None else key + '=' + value for key, value in style.items()) + ';')
        if label is not None and old == visible[0]:
            cell.set('value', label)
        root.append(cell)
    return model


class LabelCheck(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {'color', 'bgcolor'} and (value or '').lower() not in BLACK | WHITE:
                raise ValueError('HTML label contains a non-monochrome color.')
            if name == 'size':
                raise ValueError('Use fontSize=18 or CSS font-size:18px, not HTML font size.')
            if name == 'style':
                for declaration in (value or '').split(';'):
                    key, separator, setting = declaration.partition(':')
                    if not separator:
                        continue
                    key, setting = key.strip().lower(), setting.strip().lower()
                    if key in {'color', 'background', 'background-color'} and setting not in BLACK | WHITE | {'none', 'transparent'}:
                        raise ValueError('HTML label contains a non-monochrome color.')
                    if key == 'font-size' and setting != '18px':
                        raise ValueError('HTML label font-size must be 18px.')


def read_pages(path):
    document = ET.parse(path).getroot()
    if document.tag == 'mxGraphModel':
        return [document]
    if document.tag != 'mxfile':
        raise ValueError('Expected mxfile or mxGraphModel.')
    pages = []
    for diagram in document.findall('diagram'):
        model = diagram.find('mxGraphModel')
        if model is None:
            payload = (diagram.text or '').strip()
            if payload.startswith('<'):
                model = ET.fromstring(payload)
            else:
                decoded = zlib.decompress(base64.b64decode(payload), -15).decode('utf-8')
                model = ET.fromstring(urllib.parse.unquote(decoded))
        if model.tag != 'mxGraphModel':
            raise ValueError('Invalid diagram page model.')
        pages.append(model)
    if not pages:
        raise ValueError('No diagram pages found.')
    return pages


def validate_pages(pages, digest, prototypes):
    checked = 0
    for page in pages:
        root = page.find('root')
        if root is None or any(cell.tag != 'mxCell' for cell in root):
            raise ValueError('Pages must use direct mxCell children under root.')
        cells = list(root)
        identifiers = [cell.get('id') for cell in cells]
        if None in identifiers or len(set(identifiers)) != len(identifiers):
            raise ValueError('Missing or duplicate page cell IDs.')
        roots = {cell.get('id'): cell for cell in cells if cell.get('id') in {'0', '1'}}
        if set(roots) != {'0', '1'} or roots['0'].get('parent') is not None or roots['1'].get('parent') != '0':
            raise ValueError('Invalid standard page roots.')
        if any(cell.get('vertex') or cell.get('edge') or cell.get('style') or cell.get('value') for cell in roots.values()):
            raise ValueError('Standard page roots must not contain diagram symbols.')
        groups = {}
        for cell in cells:
            if cell.get('id') in roots:
                continue
            if cell.get('vlsit_native_table') == '1':
                native = style_map(cell.get('style'))
                if native.get('fontSize') != '18' or native.get('fontColor', '').lower() not in BLACK:
                    raise ValueError('Native table cells must use black 18 pt text.')
                if native.get('strokeColor', '').lower() not in BLACK | {'none'} or native.get('fillColor', '').lower() not in WHITE | {'none'}:
                    raise ValueError('Native table cells must be black and white.')
                continue
            if cell.get('vlsit_library_sha256') != digest:
                raise ValueError('A cell is missing the correct library hash.')
            entry = int(cell.get('vlsit_library_entry', '-1'))
            old = cell.get('vlsit_library_cell')
            instance = cell.get('vlsit_library_instance')
            if not instance or not 0 <= entry < len(prototypes) or old not in prototypes[entry]:
                raise ValueError('Invalid cell template provenance.')
            original = prototypes[entry][old]
            if any(cell.get(key) != original.get(key) for key in ('vertex', 'edge')):
                raise ValueError('Template vertex/edge type was changed.')
            style, base = style_map(cell.get('style')), style_map(original.get('style'))
            protected = lambda values: {key: value for key, value in values.items() if key not in EDITABLE}
            if protected(style) != protected(base):
                raise ValueError('A template shape, operation, arrowhead, or other protected style was changed.')
            if style.get('fontSize') != '18' or style.get('fontColor', '').lower() not in BLACK:
                raise ValueError('Every cloned cell must specify black text and fontSize=18.')
            if style.get('strokeColor', '').lower() not in BLACK | {'none'}:
                raise ValueError('Borders must be black or invisible.')
            if style.get('fillColor', '').lower() not in WHITE | {'none'}:
                raise ValueError('Fills must be white or transparent.')
            LabelCheck().feed(cell.get('value') or '')
            key = instance
            if key not in groups:
                groups[key] = (entry, {})
            previous_entry, members = groups[key]
            if previous_entry != entry or old in members:
                raise ValueError('Inconsistent or duplicated clone membership.')
            members[old] = cell
            checked += 1
        for entry, members in groups.values():
            template = prototypes[entry]
            if set(members) != set(template):
                raise ValueError('A library group has missing or extra constituent cells.')
            for old, cell in members.items():
                original = template[old]
                for key in ('parent', 'source', 'target'):
                    reference = original.get(key)
                    if reference in template:
                        if cell.get(key) != members[reference].get('id'):
                            raise ValueError('Internal template topology was changed.')
                    elif key == 'parent':
                        if cell.get(key) != reference:
                            raise ValueError('A top-level clone has an unexpected parent.')
                    elif cell.get(key) is not None and cell.get(key) not in identifiers:
                        raise ValueError('A connector endpoint references a missing page cell.')
    if not checked:
        raise ValueError('No library-derived symbols were found.')
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('catalog')
    clone = commands.add_parser('clone')
    clone.add_argument('--entry', type=int, required=True)
    clone.add_argument('--instance', required=True)
    clone.add_argument('--label')
    clone.add_argument('--output', type=Path, required=True)
    validate = commands.add_parser('validate')
    validate.add_argument('--diagram', type=Path, required=True)
    args = parser.parse_args()
    try:
        digest, prototypes = load_library()
        if args.command == 'catalog':
            print(f'Library SHA-256: {digest}; entries: {len(prototypes)}')
            for index, cells in enumerate(prototypes):
                print(f'{index}: ' + ' | '.join(cell.get('style', '') for cell in cells.values()))
        elif args.command == 'clone':
            model = clone_template(digest, prototypes, args.entry, args.instance, args.label)
            validate_pages([model], digest, prototypes)
            payload = ET.tostring(model, encoding='unicode') + '\n'
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(payload)
            print(f'Created template {args.entry} clone; library SHA-256: {digest}')
        else:
            pages = read_pages(args.diagram)
            count = validate_pages(pages, digest, prototypes)
            print(f'PASS: {count} library-derived cells across {len(pages)} pages. RTL semantics and visual layout were not checked.')
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, zlib.error) as error:
        parser.exit(2, f'Library operation failed: {error}\n')


if __name__ == '__main__':
    main()
