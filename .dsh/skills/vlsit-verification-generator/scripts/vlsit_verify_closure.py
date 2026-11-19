#!/usr/bin/env python3
# Function : assess source-bound verification evidence under a reviewed closure contract
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
"""Schema v2 closure checks. Exit 0 met, 1 unmet, 2 invalid, 3 met with waivers.

Approved producers/review records are a trust boundary, not digital signatures.
Raw vendor results still require a qualified project-specific producer/adapter.
"""
import argparse
import contextlib
import io
import datetime
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from vlsit_verify_plan import read_rows, check_plan, split_ids, PlanError

DIMENSIONS = {'normal', 'boundary', 'error', 'recovery', 'reset', 'backpressure', 'concurrency'}
FAMILIES = {'functional', 'code', 'assertion', 'mutation'}
QUAL_EXPECTED = dict(known_answer='match', boundary='match', negative='handled', reset='match',
                     fault_detection='detected', **{k:'rejected' for k in
                     ('raw_failure','missing_bin','wrong_configuration','vacuity','invalid_counter','wrong_baseline')})
FAILURE = re.compile(r'^\s*(?:SIMULATION\s+FAILED\b|FATAL(?:\s|:)|%Error(?:\s|:)|UVM_(?:ERROR|FATAL)\b)', re.I | re.M)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return digest(json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                             allow_nan=False).encode('utf-8'))


def load(path):
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    def resolved(value):
        if isinstance(value, str):
            need(not (value.strip().startswith('<') and value.strip().endswith('>'))
                 and value.strip().upper() not in ('TODO', 'TBD'), 'unresolved template placeholder')
        elif isinstance(value, dict):
            for item in value.values(): resolved(item)
        elif isinstance(value, list):
            for item in value: resolved(item)
    resolved(data)
    return data


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(items, field='id'):
    need(isinstance(items, list), '%s records must be a list' % field)
    result = {}
    for item in items:
        need(isinstance(item, dict), 'record must be an object')
        key = item[field]
        need(isinstance(key, str) and key.strip() and key not in result, 'empty/duplicate %s' % field)
        result[key] = item
    return result


def ids(items):
    need(isinstance(items, list) and all(isinstance(x, str) and x.strip() for x in items), 'IDs must be non-empty strings')
    need(len(items) == len(set(items)), 'duplicate ID in list')
    return set(items)


def number(item, key):
    value = item[key]
    need(type(value) is int and value >= 0, '%s must be an explicit non-negative integer' % key)
    return value


def artifact(base, item):
    rel = Path(item['path'])
    path = (base / rel).resolve()
    need(not rel.is_absolute() and base.resolve() in path.parents, 'artifact escapes document folder')
    need(path.is_file(), 'missing artifact: %s' % rel)
    need(digest(path.read_bytes()) == item['sha256'], 'artifact hash mismatch: %s' % rel)
    return path


def reviewed(record, today):
    review = record['review']
    need(review['decision'] == 'approved' and bool(review['approver'].strip()), 'record is not approved')
    need(datetime.date.fromisoformat(review['date']) <= today, 'approval date is in the future')


def qualification(base, ref, today, required):
    path = artifact(base, ref)
    data = load(path)
    reviewed(data, today)
    tests = unique(data['tests'], 'kind')
    need(required <= set(tests), 'qualification lacks required fault/known-answer tests')
    for test in tests.values():
        need(test['status'] == 'pass' and bool(test['command'].strip()), 'qualification test not passed/executed')
        need(number(test, 'exit_code') == 0, 'qualification command failed or did not execute')
        expected = QUAL_EXPECTED.get(test['kind'], test['expected'])
        need(bool(expected) and test['expected'] == expected and test['observed'] == expected, 'qualification did not detect/handle expected behavior')
        report = load(artifact(path.parent, test['evidence']))
        fields = ('kind','status','command','exit_code','expected','observed')
        need(canonical({k:report[k] for k in fields}) == canonical({k:test[k] for k in fields}), 'qualification summary contradicts source result')
    return data


def check_property(prop, definition):
    kind = definition['kind']
    need(kind in ('immediate', 'implication', 'formal'), 'unknown property kind')
    if number(prop, 'failures') != 0:
        return False
    if kind == 'formal':
        return (prop['status'] == 'proved' and prop['proof_kind'] == 'unbounded'
                and prop['nonvacuity'] == 'pass' and bool(prop['assumptions_id'].strip()))
    if prop['status'] != 'pass':
        return False
    attempts, completed = number(prop, 'attempts'), number(prop, 'completed')
    pending, disabled, cancelled = (number(prop, key) for key in ('pending', 'disabled', 'cancelled'))
    need(disabled <= attempts and completed <= attempts, 'inconsistent property counters')
    if cancelled and not definition.get('allow_cancelled', False):
        return False
    if pending or not completed:
        return False
    if kind == 'implication':
        hits = number(prop, 'antecedent_hits')
        need(completed + cancelled == hits and hits <= attempts - disabled,
             'antecedent/completion counters are inconsistent')
    else:
        need(completed + disabled + cancelled == attempts, 'immediate evaluations are unaccounted')
    return True


def assess(plan_path, index_path, contract_path, observations_path, today,
           allow_waivers=False, output=None, force=False):
    plan_output = io.StringIO()
    with contextlib.redirect_stdout(plan_output):
        plan_status = check_plan(plan_path, None, str(index_path), None, today)
    if plan_status:
        print(plan_output.getvalue(), end='')
        return 1
    _, rows = read_rows(plan_path)
    contract, observed = load(contract_path), load(observations_path)
    need(contract['schema_version'] == 2 and observed['schema_version'] == 2, 'schema_version 2 required')
    contract_hash = canonical({k: v for k, v in contract.items() if k != 'approval'})
    approval = load(artifact(contract_path.parent, contract['approval']))
    reviewed(approval, today)
    need(approval['contract_sha256'] == contract_hash, 'contract changed after approval')
    need(approval['requirements_sha256'] == digest(index_path.read_bytes()), 'inventory changed after approval')
    errors = []
    baseline = {}
    for key in ('specification', 'rtl_manifest'):
        path = artifact(contract_path.parent, contract['baseline'][key])
        baseline[key] = digest(path.read_bytes())
    need(observed['baseline'] == baseline, 'observation baseline mismatch')
    manifest_path = artifact(contract_path.parent, contract['baseline']['rtl_manifest'])
    manifest = load(manifest_path)
    need(manifest['schema_version'] == 2 and bool(manifest['top'].strip()), 'invalid RTL/build manifest')
    source_root = Path(manifest['source_root'])
    need(not source_root.is_absolute(), 'source_root must be portable and relative to manifest')
    source_root = (manifest_path.parent / source_root).resolve()
    files = unique(manifest['files'], 'path')
    need(bool(files), 'build manifest has no files')
    resolved_files = set()
    for file in files.values():
        resolved_path = artifact(source_root, file)
        need(resolved_path not in resolved_files, 'same build input repeated under multiple paths/roles')
        resolved_files.add(resolved_path)
        need(file['role'] in ('rtl', 'include', 'filelist', 'verification', 'model', 'build', 'configuration'), 'unknown build input role')
    need(any(f['role'] == 'rtl' for f in files.values()), 'no RTL source in manifest')
    configs = ids(contract['configurations'])
    need(bool(configs), 'no configurations')
    build_configs = unique(manifest['configurations'])
    need(configs == set(build_configs), 'manifest configuration set differs')
    for config in build_configs.values():
        need(isinstance(config['parameters'], dict) and isinstance(config['defines'], dict)
             and isinstance(config['options'], list) and bool(config['tool'].strip()), 'incomplete build configuration')
    plan, obligations = unique(rows, 'obligation_id'), unique(contract['obligations'])
    need(set(plan) == set(obligations), 'vplan/contract obligation IDs differ')
    scope_path = artifact(contract_path.parent, contract['scope_matrix'])
    matrix = load(scope_path)
    need(matrix['schema_version'] == 2, 'invalid scope matrix schema')
    inventory = {s.strip() for s in index_path.read_text(encoding='utf-8-sig').splitlines() if s.strip() and not s.startswith('#')}
    cells = {}
    for cell in matrix['cells']:
        key = (cell['req_id'], cell['configuration'])
        need(key not in cells, 'duplicate scope matrix cell')
        cells[key] = cell
    need(set(cells) == {(req, cfg) for req in inventory for cfg in configs}, 'scope matrix inventory/configuration mismatch')
    matrix_obligations = set()
    for (req, cfg), cell in cells.items():
        dims = unique(cell['dimensions'], 'dimension')
        need(DIMENSIONS <= set(dims), 'scope matrix lacks required scenario dimensions')
        for dimension, entry in dims.items():
            mapped = ids(entry['obligations'])
            if entry['applicability'] == 'not_applicable':
                need(not mapped and bool(entry['reason'].strip()), 'N/A dimension needs reason and no obligations')
            else:
                need(entry['applicability'] == 'required' and bool(mapped), 'required dimension lacks obligations')
            for key in mapped:
                need(key in obligations and key not in matrix_obligations, 'unknown/multiply scoped obligation')
                o, row = obligations[key], plan[key]
                need((o['req_id'], o['configuration'], o['dimension']) == (req, cfg, dimension), 'contract obligation scope mismatch')
                need((row['req_id'], row['configuration'], row['dimension']) == (req, cfg, dimension), 'vplan obligation scope mismatch')
                matrix_obligations.add(key)
    need(matrix_obligations == set(obligations), 'obligation outside reviewed scenario matrix')
    checkers = unique(contract['checkers'])
    producers = unique(contract['producers'])
    need(bool(producers), 'no qualified result producer')
    for producer in producers.values():
        q = qualification(contract_path.parent, producer['qualification'], today,
                          {'raw_failure', 'missing_bin', 'wrong_configuration', 'vacuity', 'invalid_counter', 'wrong_baseline'})
        need(q['producer_id'] == producer['id'], 'producer qualification identity mismatch')
        producer_path = artifact(contract_path.parent, producer['implementation'])
        need(q['implementation_sha256'] == digest(producer_path.read_bytes()), 'producer implementation differs from qualification')
    models = unique(contract['models'])
    for model in models.values():
        mpath = artifact(contract_path.parent, model['contract'])
        m = load(mpath)
        need(bool(m['provenance'].strip()) and bool(m['numeric_semantics']) and bool(m['limitations']), 'incomplete model contract')
        refs = ids(m['source_files'])
        need(bool(refs) and refs <= set(files) and all(files[f]['role'] == 'model' for f in refs), 'model sources not frozen in build manifest')
        q = qualification(mpath.parent, m['qualification'], today, {'known_answer', 'boundary', 'negative', 'reset', 'fault_detection'})
        need(q['model_id'] == model['id'] and q['build_manifest_sha256'] == baseline['rtl_manifest'], 'model qualification baseline mismatch')
    for checker in checkers.values():
        need(number(checker, 'minimum_comparisons') > 0, 'checker minimum comparisons must be positive')
        q = qualification(contract_path.parent, checker['qualification'], today, {'known_answer', 'fault_detection'})
        need(q['checker_id'] == checker['id'] and q['build_manifest_sha256'] == baseline['rtl_manifest'], 'checker qualification identity/baseline mismatch')
        need(checker['kind'] in ('protocol', 'scoreboard', 'model_compare', 'formal_adapter'), 'unknown checker kind')
        if checker['kind'] in ('scoreboard', 'model_compare'):
            need(checker['model_id'] is not None, 'data checker requires qualified independent model')
        if checker['model_id'] is not None:
            need(checker['model_id'] in models, 'checker model is unqualified')
    for key, obligation in obligations.items():
        row = plan[key]
        need(ids(obligation['checks']) == set(split_ids(row['checker'])), 'contract checker IDs differ from vplan')
        need(ids(obligation['bins']) == set(split_ids(row['coverage_bin'])), 'contract bins differ from vplan')
        props = unique(obligation['assertions'])
        need(set(props) == set(split_ids(row.get('assertion', ''))), 'contract assertion IDs differ from vplan')
        for prop in props.values():
            if prop['kind'] == 'formal':
                assumptions = load(artifact(contract_path.parent, prop['assumptions']))
                reviewed(assumptions, today)
                need(assumptions['configuration'] == obligation['configuration'] and assumptions['specification_sha256'] == baseline['specification'], 'formal assumptions scope differs from baseline')
                need(isinstance(assumptions['constraints'], list), 'formal constraints must be explicit')
        need(set(obligation['checks']) <= set(checkers), 'obligation uses unqualified checker')
        need(bool(obligation['checks'] or props) and bool(obligation['bins'] or props), 'unchecked/uncovered obligation')
    policy = {}
    for item in contract['metric_policy']:
        key = (item['configuration'], item['family'])
        need(key not in policy and type(item['applicable']) is bool, 'invalid metric policy')
        if not item['applicable']:
            need(bool(item['reason'].strip()), 'N/A metric family requires approved reason')
        policy[key] = item
    need(set(policy) == {(cfg, family) for cfg in configs for family in FAMILIES}, 'metric policy must explicitly cover every family/configuration')
    for cfg in configs:
        scoped = [o for o in obligations.values() if o['configuration'] == cfg]
        if any(o['bins'] for o in scoped):
            need(policy[(cfg, 'functional')]['applicable'], 'required functional bins cannot be N/A')
        if any(o['assertions'] for o in scoped):
            need(policy[(cfg, 'assertion')]['applicable'], 'required assertions cannot have N/A activity coverage')
    goals = unique(contract['metrics'])
    universes = {}
    for key, goal in goals.items():
        cfg, family = goal['configuration'], goal['family']
        need((cfg, family) in policy and policy[(cfg, family)]['applicable'], 'metric outside applicable policy')
        bins = ids(goal['bin_ids'])
        need(bool(bins) and goal['total'] == len(bins) and type(goal['total']) is int, 'metric denominator differs from bin catalog')
        target = goal['target_percent']
        need(type(target) in (int, float) and math.isfinite(target) and 0 < target <= 100, 'active coverage target must be in (0,100]')
        universes[key] = bins
    for (cfg, family), item in policy.items():
        matching = [g for g in goals.values() if (g['configuration'], g['family']) == (cfg, family)]
        need(bool(matching) == item['applicable'], 'applicable metric family missing (or N/A family measured)')
    for cfg in configs:
        required_bins = set().union(*(set(o['bins']) for o in obligations.values() if o['configuration'] == cfg))
        catalog = set().union(*(universes[k] for k, g in goals.items() if g['configuration'] == cfg and g['family'] == 'functional'))
        need(required_bins <= catalog, 'mandatory functional bins missing from metric catalog')
    sources = unique(observed['sources'])
    need(bool(sources), 'no source receipts')
    receipts = {}
    for key, source in sources.items():
        need(source['role'] in ('run_receipt', 'waiver_record'), 'unknown source role')
        path = artifact(observations_path.parent, source)
        receipts[key] = (path, load(path))
    runs = unique(observed['runs'])
    hits = {key: set() for key in goals}
    metric_runs = {key: set() for key in goals}
    valid_runs = set()
    for key, run in runs.items():
        cfg = run['configuration']
        need(cfg in configs and type(run['seed']) is int and bool(run['command'].strip()), 'invalid run identity')
        need(run['baseline'] == baseline and run['configuration_sha256'] == canonical(build_configs[cfg])
             and run['contract_sha256'] == contract_hash and run['tool'] == build_configs[cfg]['tool'], 'run baseline/configuration/tool mismatch')
        expected_build = dict(top=manifest['top'], files=manifest['files'], parameters=build_configs[cfg]['parameters'],
                              defines=build_configs[cfg]['defines'], options=build_configs[cfg]['options'])
        need(canonical(run['build']) == canonical(expected_build), 'actual compiled inputs/top/options differ from approved manifest')
        source_ids = ids(run['source_ids'])
        need(len(source_ids) == 1 and source_ids <= set(receipts), 'run requires exactly one known receipt')
        sid = next(iter(source_ids))
        need(sources[sid]['role'] == 'run_receipt', 'run source is not a run receipt')
        path, receipt = receipts[sid]
        need(receipt['schema_version'] == 2 and receipt['producer_id'] in producers, 'receipt uses unknown producer/schema')
        payload = {k: v for k, v in run.items() if k != 'source_ids'}
        need(canonical(receipt['run']) == canonical(payload), 'normalized run contradicts source receipt')
        roles = set()
        raw_paths = set()
        raw_failed = False
        for raw in receipt['raw_artifacts']:
            raw_path = artifact(path.parent, raw)
            need(raw_path not in raw_paths, 'raw artifact repeated under different roles')
            raw_paths.add(raw_path)
            role = raw['role']; roles.add(role)
            if role in ('compile_log', 'simulation_log', 'formal_log'):
                content = raw_path.read_text(encoding='utf-8', errors='replace')
                content = re.sub(r'^\s*UVM_(?:ERROR|FATAL)\s*:\s*0\s*$', '', content, flags=re.M | re.I)
                raw_failed |= bool(FAILURE.search(content))
        need('compile_log' in roles and ('simulation_log' in roles or 'formal_log' in roles), 'receipt lacks compile and execution logs')
        good = (run['compile'] == 'pass' and run['result'] == 'pass'
                and type(run['exit_code']) is int and run['exit_code'] == 0 and not raw_failed)
        check_values = run['checks']
        need(isinstance(check_values, dict) and set(check_values) <= set(checkers), 'unknown checker results')
        for cid, result in check_values.items():
            compared = number(result, 'comparisons')
            cancelled = number(result, 'cancelled')
            need(number(result, 'expected') == compared + cancelled and number(result, 'observed') == compared, 'scoreboard counts do not reconcile')
            if cancelled and not checkers[cid].get('allow_cancelled', False):
                good = False
            good &= (result['status'] == 'pass' and compared >= checkers[cid]['minimum_comparisons']
                     and number(result, 'mismatches') == 0 and number(result, 'pending') == 0)
        definitions = {}
        for oid in ids(run['obligations']):
            need(oid in obligations and obligations[oid]['configuration'] == cfg, 'run obligation scope mismatch')
            need(run['test'] in split_ids(plan[oid]['test']), 'wrong test for obligation')
            for prop in obligations[oid]['assertions']:
                need(prop['id'] not in definitions or definitions[prop['id']] == prop, 'inconsistent property definitions')
                definitions[prop['id']] = prop
        properties = unique(run['assertions'])
        if any(d['kind'] == 'formal' for d in definitions.values()):
            need('formal_assumptions' in roles and 'formal_report' in roles, 'formal proof lacks assumptions/report artifacts')
        need(set(properties) == set(definitions), 'missing or unexpected property result')
        for pid, definition in definitions.items():
            if definition['kind'] == 'formal':
                assumption_path = artifact(contract_path.parent, definition['assumptions'])
                assumption = load(assumption_path)
                need(properties[pid]['assumptions_id'] == assumption['id'] and properties[pid]['assumptions_sha256'] == definition['assumptions']['sha256'], 'proof uses different assumptions')
                need(any(raw['role'] == 'formal_assumptions' and raw['sha256'] == definition['assumptions']['sha256'] for raw in receipt['raw_artifacts']), 'proof raw assumptions differ from approved contract')
            good &= check_property(properties[pid], definition)
        need(ids(run['bins']) <= set().union(*(universes[k] for k,g in goals.items() if g['configuration'] == cfg and g['family']=='functional')), 'unknown functional bins')
        run_metric_hits = run['metric_hits']
        need(isinstance(run_metric_hits, dict) and set(run_metric_hits) <= set(goals), 'unknown run metric')
        for mid, bin_ids in run_metric_hits.items():
            goal = goals[mid]; measured = ids(bin_ids)
            need(goal['configuration'] == cfg and measured <= universes[mid], 'metric hit outside configuration/catalog')
            if goal['family'] == 'functional':
                need(measured == set(run['bins']) & universes[mid], 'functional metric contradicts observed bins')
            if goal['family'] == 'assertion':
                need(measured == set(properties) & universes[mid], 'assertion metric contradicts property results')
        for mid,g in goals.items():
            if g['configuration'] == cfg and g['family'] in ('functional','assertion'):
                need(mid in run_metric_hits, 'run omits derived metric')
        if good:
            valid_runs.add(key)
            for mid, bin_ids in run_metric_hits.items():
                hits[mid].update(bin_ids);metric_runs[mid].add(key)
        else:
            errors.append('failed/unexecuted/contradictory run: '+key)
    if not valid_runs:
        errors.append('no successfully executed measured run')
    waivers = unique(observed.get('waivers', []), 'obligation_id')
    for oid, waiver in waivers.items():
        need(oid in obligations and waiver['source_id'] in receipts, 'unknown waiver/approval source')
        sid = waiver['source_id'];path,record=receipts[sid]
        need(sources[sid]['role'] == 'waiver_record' and canonical(record) == canonical({k:v for k,v in waiver.items() if k!='source_id'}), 'waiver contradicts approval record')
        reviewed(record,today)
        need(record['contract_sha256'] == contract_hash and record['baseline'] == baseline, 'waiver baseline/contract mismatch')
        need(bool(record['reason'].strip()) and bool(record['owner'].strip()), 'waiver lacks technical reason/owner')
        need(datetime.date.fromisoformat(record['expiry']) >= today, 'expired waiver')
    closed = 0
    for oid,o in obligations.items():
        row = plan[oid]
        if oid in waivers:
            need(row['status']=='waived', 'waiver must be reconciled into vplan status')
            continue
        if row['status'] != 'passing':
            errors.append('vplan status not passing: '+oid)
        met = False
        for run_id in valid_runs:
            run=runs[run_id]
            if oid in run['obligations'] and set(split_ids(row['evidence'])) & set(run['source_ids']):
                met |= (set(o['checks']) <= set(run['checks']) and set(o['bins']) <= set(run['bins']))
        if met and row['status']=='passing':closed+=1
        else:errors.append('unmet obligation or unbound vplan evidence: '+oid)
    measurements=unique(observed['metrics'])
    need(set(measurements)==set(goals), 'aggregate metrics differ from approved policy')
    metric_report=[]
    for mid,g in goals.items():
        actual=measurements[mid]
        need(actual['configuration']==g['configuration'] and ids(actual['run_ids'])==metric_runs[mid], 'aggregate metric uses unrelated runs')
        covered,total=len(hits[mid]),len(universes[mid])
        need(number(actual,'covered')==covered and number(actual,'total')==total
             and ids(actual['bin_ids'])==hits[mid], 'coverage counters disagree with measured bin union')
        percent=100*covered/total
        metric_report.append(dict(id=mid,covered=covered,total=total,percent=percent,target=g['target_percent']))
        if percent<g['target_percent']:errors.append('coverage target missed: '+mid)
    verdict='UNMET' if errors else 'MET_WITH_WAIVERS' if waivers else 'MET'
    result=dict(schema_version=2,verdict=verdict,measured=closed,waived=len(waivers),total=len(obligations),
                metrics=metric_report,errors=errors,human_signoff=False,
                not_applicable_metrics=[p for p in policy.values() if not p['applicable']],
                contract_sha256=contract_hash,baseline=baseline)
    if output:
        need(force or not output.exists(),'output exists; use --force')
        output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for error in errors:print('ERROR '+error)
    print('CLOSURE_RESULT: '+json.dumps(result,sort_keys=True))
    return 1 if errors else 3 if waivers and not allow_waivers else 0


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('vplan','spec-index','contract','observations'):
        parser.add_argument('--'+name,required=True,type=Path)
    waiver=parser.add_mutually_exclusive_group()
    waiver.add_argument('--allow-waivers',action='store_true',help='allow exit 0 for MET_WITH_WAIVERS; verdict remains conditional')
    waiver.add_argument('--require-no-waivers',action='store_true',help='strict default: conditional closure returns exit 3')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--force',action='store_true')
    parser.add_argument('--today',type=datetime.date.fromisoformat,default=datetime.date.today())
    args=parser.parse_args(argv)
    try:
        return assess(args.vplan,args.spec_index,args.contract,args.observations,args.today,args.allow_waivers,args.output,args.force)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,PlanError) as error:
        print('ERROR invalid/untrusted closure input: '+str(error));return 2


if __name__=='__main__':
    sys.exit(main())
