#!/usr/bin/env python3
# Function : preserve complete simulation packages and execute evidence-bound replay
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
"""Package integrity and recorded execution are separate from hardware closure.

Schema 2; init/seal/check/execute/replay. No tool installation or vendor parser.
Exit 0: requested operation succeeded; 2: incomplete/invalid/failed operation.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

DIRS = ('docs','env','tb','models','dut','tests','scripts','runs','coverage','snapshots')
MANIFEST = 'env/workspace_manifest.json'
CATALOG = 'env/retention_catalog.json'
HEADINGS = ('Prerequisites','Structure','Environment variables','Commands','Replay','Results and limitations','Troubleshooting')
RUNTIME = ('VLSIT_BASELINE_ID','VLSIT_RUN_ID','VLSIT_SNAPSHOT','VLSIT_RUN_ROOT')


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.new')
    need(not temp.exists(), 'unfinished metadata transaction: ' + str(temp))
    temp.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)


def filled(value):
    need(isinstance(value, str) and bool(value.strip()) and value not in ('not_configured','unknown','TODO','TBD')
         and '__FILL_' not in value and not (value.startswith('<') and value.endswith('>')), 'unresolved required project value')


def linked(path):
    return path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction())


def inside(root, relative):
    need(isinstance(relative, str), 'path must be a string')
    rel = Path(relative)
    path = root / rel
    need(not rel.is_absolute() and root.resolve() in path.resolve().parents, 'path escapes workspace: ' + relative)
    for part in [path, *path.parents]:
        if part == root:
            break
        need(not linked(part), 'linked package paths must be materialized: ' + str(part))
    return path


def tree(root, package=False):
    """Hash all files, including root build files and merged coverage; exclude only bookkeeping."""
    result = {}
    for path in root.rglob('*'):
        rel = path.relative_to(root).as_posix()
        if package and (rel.split('/')[0] in ('runs','snapshots') or rel in (MANIFEST, CATALOG)):
            continue
        need(not linked(path), 'linked input/output must be materialized: ' + rel)
        if not path.is_file() or path.name == '.gitkeep' or '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        result[rel] = sha(path)
    return result


def inventory(root):
    return tree(root, package=True)


def structure(root):
    need(all((root / name).is_dir() and not linked(root / name) for name in DIRS), 'workspace directory missing or linked')


def records(root, evidence_root):
    readme = (root / 'README.md').read_text(encoding='utf-8-sig')
    need(all(('## ' + h) in readme for h in HEADINGS) and '__FILL_' not in readme, 'README incomplete')
    for name in ('tb','dut','tests'):
        need(any(p.is_file() and p.name != '.gitkeep' for p in (root / name).rglob('*')), 'empty replay input group: ' + name)
    data = load(root / 'env/replay_manifest.json')
    need(data['schema_version'] == 2, 'schema 2 required; migrate schema 1 explicitly, preserving its history')
    for key in ('configuration','test','top'):
        filled(data[key])
    need(type(data['seed']) is int and data['seed'] >= 0, 'seed missing')
    need(data['cold_replay']['status'] == 'not_run', 'handwritten cold_replay success is forbidden; use replay receipts')
    filled(data['cold_replay']['reason'])
    need(data['environment_policy']['mode'] == 'isolated', 'replay must use an isolated declared environment')
    variables = {}
    for item in data['environment']:
        name = item['name']
        need(re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', name) and name not in variables and name not in RUNTIME, 'invalid/duplicate/reserved variable')
        for key in ('purpose','source','override'):
            filled(item[key])
        need(type(item['setup_order']) is int and item['setup_order'] >= 0, 'variable setup order missing')
        need(type(item['required']) is bool and type(item['secret']) is bool, 'variable flags must be booleans')
        if item['secret']:
            need('value' not in item, 'secret values must not be retained')
            filled(item['provisioning'])
        else:
            need(isinstance(item['value'], str), 'effective variable value missing')
            if item['value']:
                filled(item['value'])
        variables[name] = item
    if not variables:
        filled(data['environment_policy']['empty_reason'])
    evidence = {}
    for tool in data['tools']:
        filled(tool['name'])
        need(isinstance(tool['version_argv'], list) and bool(tool['version_argv']), 'version argv missing')
        for arg in tool['version_argv']:
            filled(arg)
        if tool['status'] == 'observed':
            filled(tool['version'])
            path = inside(evidence_root, tool['version_log'])
            need(path.is_file() and sha(path) == tool['version_log_sha256'], 'tool version log missing/changed')
            evidence[tool['version_log']] = sha(path)
        else:
            need(tool['status'] == 'not_run', 'invalid tool status')
            filled(tool['reason'])
    need(bool(data['tools']), 'toolchain missing')
    stages = set()
    for command in data['commands']:
        filled(command['name'])
        need(command['stage'] in ('setup','version','compile','simulate','coverage','replay'), 'unknown command stage')
        stages.add(command['stage'])
        validate_command(command)
        inside(evidence_root, command['cwd'])
        need(set(command['environment']) <= set(variables), 'undocumented command environment')
        if command['status'] == 'not_run':
            filled(command['reason'])
        else:
            need(command['status'] in ('pass','fail') and type(command['exit_code']) is int, 'invalid executed command')
            need((command['status'] == 'pass') == (command['exit_code'] == 0), 'status contradicts exit code')
            path = inside(evidence_root, command['log'])
            need(path.is_file() and sha(path) == command['log_sha256'], 'execution log missing/changed')
            evidence[command['log']] = sha(path)
    need({'compile','simulate','replay'} <= stages, 'compile/simulate/replay instructions missing')
    plan = data['replay_plan']
    producer = plan['result_producer']
    need(producer['status'] in ('qualified','pending') and producer['scope'] in ('synthetic','rtl'), 'result producer qualification/scope missing')
    filled(producer['reviewer'])
    need(inside(root, producer['evidence']).is_file(), 'result producer qualification record missing')
    runner = inside(root, plan['runner'])
    need(runner.is_file() and plan['runner'] != 'scripts/vlsit_sim_workspace.py', 'actual project runner missing')
    for stage in ('compile','simulate'):
        validate_command(plan[stage])
        need(any('{snapshot}/' + plan['runner'] in arg.replace('\\','/') for arg in plan[stage]['argv']), 'run commands must use retained runner')
    need(bool(plan['build_outputs']), 'build outputs missing')
    for path in [*plan['build_outputs'], plan['result']]:
        inside(root, path)
    need(plan['result'] not in plan['build_outputs'], 'simulation result must differ from build outputs')
    need(isinstance(plan['expected_cases'], list) and bool(plan['expected_cases']) and len(plan['expected_cases']) == len(set(plan['expected_cases'])), 'expected simulation case scope missing/duplicate')
    for case in plan['expected_cases']:
        filled(case)
    for dependency in data['external_dependencies']:
        for key in ('name','version','purpose','provisioning','limitation'):
            filled(dependency[key])
    export = load(inside(root, data['dependency_export']))
    need(export['schema_version'] == 1 and not export['unresolved'], 'unresolved build/runtime dependencies')
    need(export['method'] in ('tool_export','reviewed_manual'), 'dependency discovery method missing')
    filled(export['reviewer'])
    need(export['status'] in ('reviewed','pending'), 'dependency review status invalid')
    paths = export['inputs']
    need(isinstance(paths, list) and bool(paths) and len(paths) == len(set(paths)), 'dependency input set empty/duplicate')
    for relative in paths:
        need(inside(root, relative).is_file(), 'missing dependency: ' + relative)
    required = set(inventory(root)) - {'README.md','env/replay_manifest.json',data['dependency_export'],'scripts/vlsit_sim_workspace.py'}
    required = {p for p in required if not p.startswith(('docs/','coverage/'))}
    need(required <= set(paths), 'dependency export omits retained inputs: ' + ', '.join(sorted(required - set(paths))))
    need(plan['runner'] in paths, 'runner absent from dependency export')
    # Static guard for literal HDL includes. Macros/conditional/generated paths still require real compiler discovery.
    include_dirs = [root] + [inside(root, p + '/anchor').parent for p in export['include_dirs']]
    for relative in paths:
        source = root / relative
        if source.suffix.lower() in ('.sv','.svh','.v','.vh'):
            for header in re.findall(r'`include\s+"([^"\r\n]+)"', source.read_text(encoding='utf-8', errors='replace')):
                candidates = [source.parent / header] + [p / header for p in include_dirs]
                need(any(p.is_file() and root.resolve() in p.resolve().parents and p.relative_to(root).as_posix() in paths for p in candidates), 'unretained HDL include: ' + header)
    for command in [*data['commands'], plan['compile'], plan['simulate']]:
        args = command['argv']
        for n, arg in enumerate(args):
            if arg in ('-f','-F','--filelist'):
                need(n + 1 < len(args), 'filelist option lacks argument')
                relative = args[n + 1].replace('{snapshot}/','').replace('{snapshot}\\','')
                need(inside(root, relative).is_file() and relative.replace('\\','/') in paths, 'missing/unexported filelist: ' + relative)
    return evidence


def validate_command(command):
    need(isinstance(command['argv'], list) and bool(command['argv']), 'argv missing')
    for arg in command['argv']:
        filled(arg)
    need(type(command['timeout_s']) is int and command['timeout_s'] > 0, 'timeout missing')


def init(root, rtl_dir):
    root = root.resolve()
    rtl_dir = rtl_dir.resolve()
    need(rtl_dir.is_dir(), 'original RTL directory required')
    need(root != rtl_dir and root not in rtl_dir.parents and rtl_dir not in root.parents, 'RTL and sim directories must be separate')
    need(not root.exists() or not any(root.iterdir()), 'refusing nonempty workspace')
    templates = Path(__file__).resolve().parent.parent / 'reference/templates'
    need(templates.is_dir(), 'init requires installed skill templates; copied helper supports other actions')
    root.mkdir(parents=True, exist_ok=True)
    for name in DIRS:
        (root / name).mkdir()
        (root / name / '.gitkeep').write_text('', encoding='utf-8')
    shutil.copy2(templates / 'vlsit_sim_README.md.tpl', root / 'README.md')
    shutil.copy2(templates / 'vlsit_sim_replay_manifest.json.tpl', root / 'env/replay_manifest.json')
    shutil.copy2(templates / 'vlsit_sim_build_inputs.json.tpl', root / 'env/build_inputs.json')
    shutil.copy2(Path(__file__), root / 'scripts/vlsit_sim_workspace.py')
    write(root / 'docs/source_origin.json', {'original_rtl':os.path.relpath(rtl_dir, root), 'snapshot_status':'not_configured'})
    print('WORKSPACE INITIALIZED: not configured; no tool executed')
    return 0


def snapshot(root, baseline):
    need(re.fullmatch('[0-9a-f]{64}', baseline), 'invalid baseline ID')
    target = inside(root, 'snapshots/' + baseline)
    need((target / MANIFEST).is_file(), 'historical snapshot manifest missing: ' + baseline)
    data = load(target / MANIFEST)
    need(data['baseline_id'] == baseline and data['schema_version'] == 2, 'invalid snapshot manifest')
    need(hashlib.sha256(canonical({'schema_version':2,'files':data['files'],'evidence':data['evidence']})).hexdigest() == baseline, 'snapshot manifest changed')
    need(inventory(target) == data['files'], 'snapshot files missing/changed')
    return target, data


def catalog_check(root, allow_new=False):
    structure(root)
    catpath = root / CATALOG
    if not catpath.exists():
        need(not (root / MANIFEST).exists() and not any((root / 'snapshots').glob('*/' + MANIFEST)), 'retention catalog lost; restore it, do not regenerate history')
        return {'schema_version':2,'baselines':{},'runs':{}}
    cat = load(catpath)
    need(cat['schema_version'] == 2, 'unsupported retention catalog')
    for baseline, record in cat['baselines'].items():
        target, _ = snapshot(root, baseline)
        need(sha(target / MANIFEST) == record['manifest_sha256'], 'historical manifest changed')
    actual_snapshots = {p.name for p in (root / 'snapshots').iterdir() if p.name != '.gitkeep'}
    need(actual_snapshots == set(cat['baselines']), 'snapshot catalog differs; missing/unregistered baseline')
    actual_runs = {p.name for p in (root / 'runs').iterdir() if p.name != '.gitkeep'}
    need(set(cat['runs']) <= actual_runs, 'historical run missing')
    if not allow_new:
        need(actual_runs == set(cat['runs']), 'unregistered run; seal retained history before handoff')
    for run_id, record in cat['runs'].items():
        folder = inside(root, 'runs/' + run_id)
        need(folder.is_dir() and tree(folder) == record['files'], 'historical run files missing/changed: ' + run_id)
    return cat


def seal(root, force=False):
    root = root.resolve()
    cat = catalog_check(root, allow_new=True)
    evidence = records(root, root)
    files = inventory(root)
    data = {'schema_version':2,'files':files,'evidence':evidence}
    baseline = hashlib.sha256(canonical(data)).hexdigest()
    data['baseline_id'] = baseline
    pointer = root / MANIFEST
    need(force or not pointer.exists() or load(pointer) == data, 'changed baseline requires --force; prior snapshots remain')
    target = root / 'snapshots' / baseline
    if target.exists():
        snapshot(root, baseline)
    else:
        target.mkdir()
        for name in DIRS:
            (target / name).mkdir()
        for relative in files:
            p = inside(target, relative)
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / relative, p)
        write(target / MANIFEST, data)
    cat['baselines'][baseline] = {'manifest_sha256':sha(target / MANIFEST)}
    for folder in (root / 'runs').iterdir():
        if folder.name == '.gitkeep':
            continue
        need(folder.is_dir() and not linked(folder), 'run must be an independent directory')
        if folder.name not in cat['runs']:
            cat['runs'][folder.name] = {'files':tree(folder)}
    write(root / CATALOG, cat)
    write(pointer, data)
    return check(root, baseline)


def check(root, baseline=None):
    root = root.resolve()
    cat = catalog_check(root)
    need(bool(cat['baselines']), 'no retained baseline')
    selected = baseline or load(root / MANIFEST)['baseline_id']
    need(selected in cat['baselines'], 'baseline not registered')
    target, data = snapshot(root, selected)
    if not baseline:
        need(load(root / MANIFEST) == data and inventory(root) == data['files'], 'editable inputs differ from selected baseline')
    need(records(target, root) == data['evidence'], 'referenced execution evidence differs')
    for run_id, record in cat['runs'].items():
        if 'receipt' in record:
            validate_receipt(root, run_id, cat)
    print('PACKAGE_INTEGRITY: VALID; all registered baselines/runs checked; baseline=' + selected)
    print('Package validation alone grants no execution, replay or hardware-closure verdict.')
    return 0


def result_record(path, data, baseline):
    result = load(path)
    need(result['schema_version'] == 1 and result['complete'] is True, 'simulation did not report completion')
    for key in ('configuration','test','top','seed'):
        need(result[key] == data[key], 'simulation identity mismatch: ' + key)
    need(result['baseline_id'] == baseline, 'simulation baseline mismatch')
    cases = result['cases']
    need(isinstance(cases, list) and bool(cases), 'no checked simulation cases')
    ids = set()
    for case in cases:
        filled(case['id'])
        need(case['id'] not in ids and case['status'] == 'pass' and type(case['checks']) is int and case['checks'] > 0 and type(case['errors']) is int and case['errors'] == 0, 'invalid/failed/unchecked case')
        ids.add(case['id'])
    need(ids == set(data['replay_plan']['expected_cases']), 'simulation case scope differs from declared scope')
    need(isinstance(result['observables'], dict) and bool(result['observables']), 'comparison observables missing')
    return result


def validate_receipt(root, run_id, cat):
    folder = inside(root, 'runs/' + run_id)
    receipt = load(folder / 'receipt.json')
    need(receipt['schema_version'] == 1 and receipt['run_id'] == run_id, 'execution receipt identity mismatch')
    need(receipt['baseline_id'] in cat['baselines'], 'execution baseline missing')
    target, _ = snapshot(root, receipt['baseline_id'])
    plan = load(target / 'env/replay_manifest.json')
    if receipt['status'] != 'pass':
        need(receipt['status'] == 'fail', 'invalid execution status')
        return receipt
    need(receipt['producer_sha256'] == sha(target / 'scripts/vlsit_sim_workspace.py'), 'execution producer differs from frozen helper')
    producer = plan['replay_plan']['result_producer']
    need(producer['status'] == 'qualified' and receipt['producer_scope'] == producer['scope'] and receipt['qualification_sha256'] == sha(target / producer['evidence']), 'result producer qualification differs')
    need(receipt['dependency_status'] == 'reviewed' and receipt['environment_mode'] == 'isolated', 'unqualified dependency/environment capture')
    need([c['stage'] for c in receipt['commands']] == ['version'] * len(plan['tools']) + ['compile','simulate'], 'execution stages incomplete')
    for cmd in receipt['commands']:
        need(cmd['exit_code'] == 0 and not cmd['timed_out'] and cmd['end_ns'] >= cmd['start_ns'], 'command did not succeed')
        need(sha(inside(folder, cmd['log'])) == cmd['log_sha256'], 'execution command log changed')
        if cmd['stage'] == 'version':
            need(bool(inside(folder, cmd['log']).read_bytes().strip()), 'tool version query produced no identity output')
        if cmd['stage'] in ('compile','simulate'):
            log = inside(folder, cmd['log']).read_text(encoding='utf-8', errors='replace')
            need(not re.search(r'(?im)^\s*(?:FATAL\b|ERROR\s*:|UVM_(?:FATAL|ERROR)\s*@|UVM_(?:FATAL|ERROR)\s*:\s*[1-9])', log), 'failure marker in successful run')
    for relative in plan['replay_plan']['build_outputs']:
        need(inside(folder, relative).is_file(), 'fresh build output missing')
    measured = result_record(inside(folder, plan['replay_plan']['result']), plan, receipt['baseline_id'])
    need(receipt['result_sha256'] == hashlib.sha256(canonical(measured)).hexdigest(), 'result receipt differs')
    if receipt['kind'] == 'replay':
        ref_id = receipt['reference_run']
        need(ref_id != run_id and ref_id in cat['runs'], 'replay reference missing/self-referential')
        ref = load(inside(root, 'runs/' + ref_id + '/receipt.json'))
        need(ref['kind'] == 'execute' and ref['status'] == 'pass' and ref['baseline_id'] == receipt['baseline_id'], 'reference must be a successful original execution of same baseline')
        need([c['log_sha256'] for c in ref['commands'] if c['stage'] == 'version'] == [c['log_sha256'] for c in receipt['commands'] if c['stage'] == 'version'], 'replay tool version output differs from reference')
        need(ref['result_sha256'] == receipt['result_sha256'] and receipt['comparison'] == 'exact_normalized_result', 'replay differs from reference')
    else:
        need(receipt['kind'] == 'execute', 'unknown execution kind')
    return receipt


def execute(root, baseline, run_id, reference=None):
    root = root.resolve()
    check(root, baseline)
    cat = load(root / CATALOG)
    target, _ = snapshot(root, baseline)
    data = load(target / 'env/replay_manifest.json')
    export = load(target / data['dependency_export'])
    need(export['status'] == 'reviewed', 'dependency discovery pending; execution/replay claim blocked')
    need(data['replay_plan']['result_producer']['status'] == 'qualified', 'result producer not qualified; execution/replay claim blocked')
    # Use the exact retained helper; an updated tool must be resealed before producing receipts.
    need(sha(Path(__file__).resolve()) == sha(target / 'scripts/vlsit_sim_workspace.py'), 'execute with the retained helper version')
    need(re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]*', run_id), 'invalid run ID')
    if reference:
        need(reference in cat['runs'] and 'receipt' in cat['runs'][reference], 'reference has no registered execution receipt')
        ref = validate_receipt(root, reference, cat)
        need(ref['kind'] == 'execute' and ref['status'] == 'pass' and ref['baseline_id'] == baseline, 'reference run not successful/same baseline')
    folder = root / 'runs' / run_id
    need(not folder.exists(), 'run ID already exists; refusing evidence overwrite')
    env = {}
    for item in data['environment']:
        if item['secret']:
            value = os.environ.get(item['name'])
            need(value is not None or not item['required'], 'required secret not provisioned: ' + item['name'])
            if value is not None:
                env[item['name']] = value
        else:
            env[item['name']] = item['value']
    env.update(VLSIT_BASELINE_ID=baseline, VLSIT_RUN_ID=run_id, VLSIT_SNAPSHOT=str(target), VLSIT_RUN_ROOT=str(folder))
    folder.mkdir()
    (folder / 'build').mkdir()
    (folder / 'reports').mkdir()
    receipt = {'schema_version':1,'kind':'replay' if reference else 'execute','run_id':run_id,'baseline_id':baseline,
               'producer_sha256':sha(Path(__file__).resolve()),'dependency_status':export['status'],
               'environment_mode':'isolated','producer_scope':data['replay_plan']['result_producer']['scope'],
               'qualification_sha256':sha(target / data['replay_plan']['result_producer']['evidence']),
               'environment':data['environment'],
               'runtime_environment':{name:env[name] for name in RUNTIME},'commands':[],'status':'fail'}
    secrets = [env[i['name']] for i in data['environment'] if i['secret'] and env.get(i['name'])]
    def command(stage, spec):
        argv = [arg.replace('{snapshot}', str(target)).replace('{run}', str(folder)) for arg in spec['argv']]
        need(Path(argv[0]).is_absolute(), 'isolated execution requires absolute executable paths')
        need(not any(secret in arg for secret in secrets for arg in argv), 'secret values in argv are forbidden; use provisioned variables')
        log = stage + '_' + str(len(receipt['commands'])) + '.log'
        start = time.time_ns()
        try:
            process = subprocess.run(argv, cwd=folder / 'build', env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     timeout=spec['timeout_s'], check=False)
            output = process.stdout or b''
            code = process.returncode
            timed_out = False
        except subprocess.TimeoutExpired as error:
            output = error.stdout or b''
            code = -1
            timed_out = True
        for secret in secrets:
            output = output.replace(secret.encode(), b'[REDACTED]')
        (folder / log).write_bytes(output)
        receipt['commands'].append({'stage':stage,'argv':argv,'cwd':'build','timeout_s':spec['timeout_s'],
            'start_ns':start,'end_ns':time.time_ns(),'exit_code':code,'timed_out':timed_out,'log':log,'log_sha256':sha(folder / log)})
        need(code == 0 and not timed_out, stage + ' execution failed/timed out')
    try:
        for tool in data['tools']:
            command('version', {'argv':tool['version_argv'],'timeout_s':30})
        command('compile', data['replay_plan']['compile'])
        for relative in data['replay_plan']['build_outputs']:
            need(inside(folder, relative).is_file(), 'compiler did not create fresh build output')
        need(not inside(folder, data['replay_plan']['result']).exists(), 'result existed before simulation')
        command('simulate', data['replay_plan']['simulate'])
        measured = result_record(inside(folder, data['replay_plan']['result']), data, baseline)
        receipt['result_sha256'] = hashlib.sha256(canonical(measured)).hexdigest()
        if reference:
            receipt['reference_run'] = reference
            receipt['comparison'] = 'exact_normalized_result'
            need(receipt['result_sha256'] == ref['result_sha256'], 'replay result differs from reference')
        receipt['status'] = 'pass'
        write(folder / 'receipt.json', receipt)
        # Validate before printing any execution/replay success.
        provisional = dict(cat)
        provisional['runs'] = dict(cat['runs'])
        provisional['runs'][run_id] = {'files':tree(folder),'receipt':'receipt.json'}
        validate_receipt(root, run_id, provisional)
    except (OSError, ValueError, KeyError, TypeError) as error:
        receipt['status'] = 'fail'
        receipt['reason'] = str(error)
        write(folder / 'receipt.json', receipt)
    cat['runs'][run_id] = {'files':tree(folder),'receipt':'receipt.json'}
    write(root / CATALOG, cat)
    # Detect mutations of the supposedly frozen input baseline during execution.
    try:
        catalog_check(root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('EXECUTION INVALID: ' + str(error))
        return 2
    if receipt['status'] != 'pass':
        print('EXECUTION FAILED; evidence retained in runs/' + run_id + ': ' + receipt['reason'])
        return 2
    print(('REPLAY_EXECUTED: MATCH' if reference else 'EXECUTION_COMPLETED: CHECKED') + '; run=' + run_id + '; producer_scope=' + receipt['producer_scope'])
    print('Scope is the declared normalized cases/observables; no exhaustive hardware-closure claim.')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('init')
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--rtl-dir', required=True, type=Path)
    p = sub.add_parser('seal')
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--force', action='store_true')
    p = sub.add_parser('check')
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--baseline')
    for action in ('execute','replay'):
        p = sub.add_parser(action)
        p.add_argument('--root', required=True, type=Path)
        p.add_argument('--baseline', required=True)
        p.add_argument('--run-id', required=True)
        if action == 'replay':
            p.add_argument('--reference-run', required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == 'init':
            return init(args.root, args.rtl_dir)
        if args.action == 'seal':
            return seal(args.root, args.force)
        if args.action == 'check':
            return check(args.root, args.baseline)
        return execute(args.root, args.baseline, args.run_id, getattr(args, 'reference_run', None))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print('ERROR: ' + str(error))
        return 2


if __name__ == '__main__':
    sys.exit(main())
