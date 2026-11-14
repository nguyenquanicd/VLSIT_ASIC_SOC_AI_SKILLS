#!/usr/bin/env python3
# Function : regression tests for false closure, stale baselines and inflated coverage
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
"""Synthetic checker fixtures only; no hardware or external simulator is verified."""
import contextlib
import copy
import csv
import datetime
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from vlsit_verify_closure import assess, canonical, digest, DIMENSIONS, QUAL_EXPECTED
from vlsit_verify_plan import REQUIRED_COLUMNS, plan_stats


class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.today = datetime.date(2026, 11, 14)
        self.refresh = True; self.reapprove = True
        self.index = self.root/'requirements.txt'; self.index.write_text('REQ-1\n', encoding='utf-8')
        self.plan = self.root/'vplan.csv'
        self.rows = [dict(req_id='REQ-1',level='block',feature='transfer',scenario='normal',
                          stimulus='request',checker='chk_data',coverage_bin='cg_ok',assertion='a_stable',
                          test='t_transfer',priority='high',status='passing',evidence='ev_run',owner='reviewer',
                          obligation_id='OB-1',configuration='cfg',dimension='normal')]
        self.write_plan()
        self.ref('spec.md','Synthetic fixture specification, not a real DUT.')
        buildfiles=[]
        for name,role in [('dut.sv','rtl'),('tb.sv','verification'),('model.py','model'),
                          ('filelist.f','filelist'),('producer.py','verification')]:
            buildfiles.append(dict(self.ref(name,'Synthetic checker fixture: '+name),role=role))
        self.config=dict(id='cfg',parameters={},defines={},options=['selftest'],tool='synthetic fixture 1')
        manifest=dict(schema_version=2,source_root='.',top='dut',files=buildfiles,configurations=[self.config])
        baseline=dict(specification=self.ref('spec.md'),rtl_manifest=self.jsonref('rtl_manifest.json',manifest))
        self.baseline={k:v['sha256'] for k,v in baseline.items()}
        scope=dict(schema_version=2,cells=[dict(req_id='REQ-1',configuration='cfg',dimensions=[
            dict(dimension=d,applicability='required' if d=='normal' else 'not_applicable',
                 obligations=['OB-1'] if d=='normal' else [],reason='Synthetic single-scenario fixture only')
            for d in sorted(DIMENSIONS)])])
        modelq=self.qual('model_qualification.json',{'known_answer','boundary','negative','reset','fault_detection'},
                         model_id='oracle',build_manifest_sha256=self.baseline['rtl_manifest'])
        model=self.jsonref('model_contract.json',dict(provenance='Independent synthetic specification fixture',
                           numeric_semantics='exact integer',limitations=['Synthetic model; not a real DUT'],
                           source_files=['model.py'],qualification=modelq))
        checkq=self.qual('checker_qualification.json',{'known_answer','fault_detection'},
                         checker_id='chk_data',build_manifest_sha256=self.baseline['rtl_manifest'])
        producerq=self.qual('producer_qualification.json',{'raw_failure','missing_bin','wrong_configuration',
                           'vacuity','invalid_counter','wrong_baseline'},producer_id='producer',
                           implementation_sha256=self.ref('producer.py')['sha256'])
        self.contract=dict(schema_version=2,baseline=baseline,configurations=['cfg'],
                           scope_matrix=self.jsonref('scope_matrix.json',scope),
                           obligations=[dict(id='OB-1',req_id='REQ-1',configuration='cfg',dimension='normal',
                              checks=['chk_data'],bins=['cg_ok'],assertions=[dict(id='a_stable',kind='implication')])],
                           checkers=[dict(id='chk_data',kind='scoreboard',minimum_comparisons=1,
                                          model_id='oracle',qualification=checkq)],
                           models=[dict(id='oracle',contract=model)],
                           producers=[dict(id='producer',implementation=self.ref('producer.py'),qualification=producerq)],
                           metric_policy=[dict(configuration='cfg',family=f,applicable=True) for f in ('functional','code','assertion','mutation')],
                           metrics=[dict(id=f,configuration='cfg',family=f,scope='synthetic fixture',total=1,
                                         bin_ids=[b],target_percent=100)
                                    for f,b in [('functional','cg_ok'),('assertion','a_stable'),('code','line_1'),('mutation','fault_1')]])
        self.observed=dict(schema_version=2,baseline=copy.deepcopy(self.baseline),sources=[],runs=[dict(
            id='run',test='t_transfer',configuration='cfg',seed=7,tool=self.config['tool'],command='synthetic selftest',
            baseline=copy.deepcopy(self.baseline),configuration_sha256=canonical(self.config),contract_sha256='',
            build=dict(top='dut',files=copy.deepcopy(buildfiles),parameters={},defines={},options=['selftest']),
            source_ids=['ev_run'],compile='pass',result='pass',exit_code=0,obligations=['OB-1'],
            checks={'chk_data':dict(status='pass',comparisons=2,mismatches=0,pending=0,expected=2,observed=2,cancelled=0)},
            bins=['cg_ok'],assertions=[dict(id='a_stable',status='pass',attempts=2,completed=1,antecedent_hits=1,
                                          failures=0,pending=0,disabled=0,cancelled=0)],
            metric_hits={g['id']:list(g['bin_ids']) for g in self.contract['metrics']})],
            metrics=[dict(id=g['id'],configuration='cfg',covered=1,total=1,bin_ids=list(g['bin_ids']),run_ids=['run'])
                     for g in self.contract['metrics']],waivers=[])
        self.raw=[dict(self.ref('compile.log','Synthetic compile success\n'),role='compile_log'),
                  dict(self.ref('sim.log','Synthetic simulation success\n'),role='simulation_log')]
        self.persist()

    def ref(self,name,text=None):
        p=self.root/name
        if text is not None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
        return dict(path=name,sha256=digest(p.read_bytes()))

    def jsonref(self,name,data):return self.ref(name,json.dumps(data,indent=2)+'\n')

    def review(self):return dict(decision='approved',approver='synthetic reviewer',date='2026-11-14')

    def qual(self,name,kinds,**metadata):
        tests=[]
        for k in sorted(kinds):
            test=dict(kind=k,status='pass',command='synthetic selftest',exit_code=0,
                      expected=QUAL_EXPECTED[k],observed=QUAL_EXPECTED[k])
            tests.append(dict(test,evidence=self.jsonref('qualification_'+k+'.json',test)))
        return self.jsonref(name,dict(metadata,review=self.review(),tests=tests))

    def write_plan(self):
        with self.plan.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=REQUIRED_COLUMNS+['assertion','obligation_id','configuration','dimension','notes'])
            w.writeheader();w.writerows(self.rows)

    def persist(self):
        chash=canonical({k:v for k,v in self.contract.items() if k!='approval'})
        if self.reapprove:
            self.contract['approval']=self.jsonref('approval.json',dict(review=self.review(),contract_sha256=chash,
                                                        requirements_sha256=digest(self.index.read_bytes())))
        if self.refresh:
            self.observed['sources']=[]
            for run in self.observed['runs']:
                run['contract_sha256']=chash
                sid=run['source_ids'][0]
                payload={k:v for k,v in run.items() if k!='source_ids'}
                ref=self.jsonref(run['id']+'_receipt.json',dict(schema_version=2,producer_id='producer',run=payload,raw_artifacts=self.raw))
                self.observed['sources'].append(dict(ref,id=sid,role='run_receipt'))
            for w in self.observed.get('waivers',[]):
                record={k:v for k,v in w.items() if k!='source_id'}
                ref=self.jsonref('waiver_'+w['obligation_id']+'.json',record)
                self.observed['sources'].append(dict(ref,id=w['source_id'],role='waiver_record'))
        self.jsonref('contract.json',self.contract);self.jsonref('observations.json',self.observed)

    def outcome(self,allow_waivers=False):
        self.persist()
        with contextlib.redirect_stdout(io.StringIO()):
            try:return assess(self.plan,self.index,self.root/'contract.json',self.root/'observations.json',self.today,allow_waivers)
            except (ValueError,KeyError,TypeError,OSError,AttributeError):return 2

    def reject(self):self.assertNotEqual(self.outcome(),0)

    def test_complete_campaign(self):self.assertEqual(self.outcome(),0)
    def test_missing_requirement(self):self.index.write_text('REQ-1\nREQ-MISSING\n',encoding='utf-8');self.reject()
    def test_protocol_inventory_bypass(self):self.rows[0]['req_id']='PROTO-UNKNOWN';self.write_plan();self.reject()
    def test_changed_live_rtl(self):self.ref('dut.sv','changed RTL');self.reject()
    def test_changed_live_model(self):self.ref('model.py','changed oracle');self.reject()
    def test_missing_build_input(self):(self.root/'filelist.f').unlink();self.reject()
    def test_manifest_hash_mismatch(self):self.ref('rtl_manifest.json','{}');self.reject()
    def test_changed_source_receipt(self):self.ref('run_receipt.json','{}');self.refresh=False;self.reject()
    def test_normalized_payload_contradiction(self):self.refresh=False;self.observed['runs'][0]['seed']=99;self.reject()
    def test_receipt_bool_is_not_integer_exit_code(self):
        self.refresh=False;r=load_json(self.root/'run_receipt.json');r['run']['exit_code']=False
        self.observed['sources'][0].update(self.jsonref('run_receipt.json',r));self.reject()
    def test_wrong_configuration_fingerprint(self):self.observed['runs'][0]['configuration_sha256']='0'*64;self.reject()
    def test_wrong_tool(self):self.observed['runs'][0]['tool']='different simulator';self.reject()
    def test_run_wrong_baseline(self):self.observed['runs'][0]['baseline']['specification']='0'*64;self.reject()
    def test_global_wrong_baseline(self):self.observed['baseline']['specification']='0'*64;self.reject()
    def test_raw_log_failed_but_receipt_pass(self):self.raw[1]=dict(self.ref('sim.log','SIMULATION FAILED: mismatch\n'),role='simulation_log');self.reject()
    def test_fatal_marker(self):self.raw[1]=dict(self.ref('sim.log','FATAL: crash\n'),role='simulation_log');self.reject()
    def test_uvm_zero_summary_is_not_failure(self):self.raw[1]=dict(self.ref('sim.log','UVM_ERROR : 0\nUVM_FATAL : 0\n'),role='simulation_log');self.assertEqual(self.outcome(),0)
    def test_wrong_source_role(self):self.refresh=False;self.observed['sources'][0]['role']='waiver_record';self.reject()
    def test_missing_raw_compile_log(self):self.raw=self.raw[1:];self.reject()
    def test_unknown_producer(self):
        self.refresh=False;r=load_json(self.root/'run_receipt.json');r['producer_id']='unqualified'
        self.observed['sources'][0].update(self.jsonref('run_receipt.json',r));self.reject()
    def test_unqualified_adapter(self):self.contract['producers'][0]['qualification']=self.jsonref('bad_q.json',{});self.reject()
    def test_qualification_counter_result_not_defaulted(self):
        q=load_json(self.root/'producer_qualification.json');q['tests'][0].pop('exit_code')
        self.contract['producers'][0]['qualification']=self.jsonref('producer_qualification.json',q);self.reject()
    def test_qualification_evidence_contradiction(self):
        q=load_json(self.root/'producer_qualification.json');test=q['tests'][0]
        report=load_json(self.root/test['evidence']['path']);report['status']='fail'
        test['evidence']=self.jsonref(test['evidence']['path'],report)
        self.contract['producers'][0]['qualification']=self.jsonref('producer_qualification.json',q);self.reject()
    def test_qualification_wrong_expected_outcome(self):
        q=load_json(self.root/'producer_qualification.json');q['tests'][0]['expected']='match';q['tests'][0]['observed']='match'
        self.contract['producers'][0]['qualification']=self.jsonref('producer_qualification.json',q);self.reject()
    def test_approval_bound_to_contract(self):self.reapprove=False;self.contract['metrics'][0]['target_percent']=90;self.reject()
    def test_future_approval(self):
        self.reapprove=False;a=load_json(self.root/'approval.json');a['review']['date']='2030-01-01'
        self.contract['approval']=self.jsonref('approval.json',a);self.reject()
    def test_no_failure_counter(self):del self.observed['runs'][0]['assertions'][0]['failures'];self.reject()
    def test_assertion_not_run_with_positive_counters(self):self.observed['runs'][0]['assertions'][0]['status']='not_run';self.reject()
    def test_impossible_antecedent_count(self):self.observed['runs'][0]['assertions'][0]['antecedent_hits']=999;self.reject()
    def test_vacuity(self):self.observed['runs'][0]['assertions'][0].update(antecedent_hits=0,completed=0);self.reject()
    def test_pending_assertion(self):self.observed['runs'][0]['assertions'][0]['pending']=1;self.reject()
    def test_failed_assertion(self):self.observed['runs'][0]['assertions'][0]['failures']=1;self.reject()
    def test_missing_assertion(self):self.observed['runs'][0]['assertions']=[];self.reject()
    def test_noop_scoreboard(self):self.observed['runs'][0]['checks']['chk_data'].update(comparisons=0,expected=0,observed=0);self.reject()
    def test_scoreboard_drain(self):self.observed['runs'][0]['checks']['chk_data']['pending']=1;self.reject()
    def test_scoreboard_mismatch(self):self.observed['runs'][0]['checks']['chk_data']['mismatches']=1;self.reject()
    def test_scoreboard_expected_unchecked(self):self.observed['runs'][0]['checks']['chk_data']['expected']=3;self.reject()
    def test_scoreboard_missing_qualification(self):self.contract['checkers'][0]['qualification']=self.jsonref('bad_q.json',{});self.reject()
    def test_missing_model(self):self.contract['models']=[];self.reject()
    def test_scoreboard_no_model_id(self):self.contract['checkers'][0]['model_id']=None;self.reject()
    def test_model_qualification_missing(self):
        m=load_json(self.root/'model_contract.json');m.pop('qualification');self.contract['models'][0]['contract']=self.jsonref('model_contract.json',m);self.reject()
    def test_failing_vplan(self):self.rows[0]['status']='failing';self.write_plan();self.reject()
    def test_planned_vplan(self):self.rows[0].update(status='planned',evidence='');self.write_plan();self.reject()
    def test_unbound_vplan_evidence(self):self.rows[0]['evidence']='ev_other';self.write_plan();self.reject()
    def test_wrong_test(self):self.observed['runs'][0]['test']='t_other';self.reject()
    def test_duplicate_obligation(self):self.contract['obligations'].append(copy.deepcopy(self.contract['obligations'][0]));self.reject()
    def test_missing_scenario_dimension(self):
        m=load_json(self.root/'scope_matrix.json');m['cells'][0]['dimensions']=[d for d in m['cells'][0]['dimensions'] if d['dimension']!='error']
        self.contract['scope_matrix']=self.jsonref('scope_matrix.json',m);self.reject()
    def test_required_reset_without_scenario(self):
        m=load_json(self.root/'scope_matrix.json');next(d for d in m['cells'][0]['dimensions'] if d['dimension']=='reset').update(applicability='required',obligations=[])
        self.contract['scope_matrix']=self.jsonref('scope_matrix.json',m);self.reject()
    def test_one_normal_pass_cannot_close_missing_error(self):
        self.rows.append(dict(self.rows[0],obligation_id='OB-2',dimension='error',status='planned',evidence=''));self.write_plan()
        self.contract['obligations'].append(dict(self.contract['obligations'][0],id='OB-2',dimension='error'))
        m=load_json(self.root/'scope_matrix.json');next(d for d in m['cells'][0]['dimensions'] if d['dimension']=='error').update(applicability='required',obligations=['OB-2'])
        self.contract['scope_matrix']=self.jsonref('scope_matrix.json',m);self.reject()
    def test_metric_family_omitted(self):self.contract['metric_policy']=self.contract['metric_policy'][:-1];self.reject()
    def test_unknown_metric_family(self):self.contract['metrics'][0]['family']='arbitrary';self.reject()
    def test_zero_target(self):self.contract['metrics'][0]['target_percent']=0;self.reject()
    def test_missing_bin(self):self.observed['runs'][0]['bins']=[];self.reject()
    def test_inflated_coverage(self):self.observed['metrics'][0].update(covered=100000,total=100000);self.reject()
    def test_full_catalog_cannot_fake_aggregate_hits(self):
        g=self.contract['metrics'][0];g.update(bin_ids=['cg_ok']+['extra_'+str(i) for i in range(9)],total=10)
        self.observed['metrics'][0].update(bin_ids=list(g['bin_ids']),covered=10,total=10);self.reject()
    def test_schema_v1_cannot_close(self):self.contract['schema_version']=1;self.assertEqual(self.outcome(),2)
    def test_inflated_denominator_in_contract(self):self.contract['metrics'][0]['total']=100000;self.observed['metrics'][0].update(covered=100000,total=100000);self.reject()
    def test_coverage_unrelated_run(self):self.observed['metrics'][0]['run_ids']=['other'];self.reject()
    def test_unknown_coverage_bin(self):self.observed['runs'][0]['metric_hits']['functional']=['invented'];self.reject()
    def test_false_bin_count(self):self.observed['metrics'][0].update(covered=1,bin_ids=[]);self.reject()
    def test_failed_run(self):self.observed['runs'][0]['result']='fail';self.reject()
    def test_missing_exit_code(self):self.observed['runs'][0]['exit_code']=None;self.reject()
    def test_boolean_exit_code(self):self.observed['runs'][0]['exit_code']=False;self.reject()
    def test_unaccounted_immediate_evaluation(self):
        self.contract['obligations'][0]['assertions'][0]['kind']='immediate';self.observed['runs'][0]['assertions'][0].update(completed=1,attempts=2);self.reject()
    def formal(self):
        definition=self.contract['obligations'][0]['assertions'][0]
        definition.update(kind='formal',assumptions=self.jsonref('assumptions.json',dict(id='A1',configuration='cfg',
                          specification_sha256=self.baseline['specification'],constraints=[],review=self.review())))
        self.observed['runs'][0]['assertions']=[dict(id='a_stable',status='proved',proof_kind='unbounded',nonvacuity='pass',
                          failures=0,assumptions_id='A1',assumptions_sha256=definition['assumptions']['sha256'])]
        self.raw.extend([dict(self.ref('assumptions.json'),role='formal_assumptions'),dict(self.ref('proof.json','{}'),role='formal_report')])
    def test_formal_proof(self):self.formal();self.assertEqual(self.outcome(),0)
    def test_bounded_result_is_not_proof(self):self.formal();self.observed['runs'][0]['assertions'][0]['proof_kind']='bounded';self.reject()
    def test_proof_assumptions_hash_mismatch(self):self.formal();self.observed['runs'][0]['assertions'][0]['assumptions_sha256']='0'*64;self.reject()
    def test_missing_formal_assumptions(self):self.formal();self.raw=[r for r in self.raw if r['role']!='formal_assumptions'];self.reject()
    def test_wrong_compiled_top(self):self.observed['runs'][0]['build']['top']='other';self.reject()
    def test_missing_compiled_dependency(self):self.observed['runs'][0]['build']['files'].pop();self.reject()
    def test_wrong_compiled_parameters(self):self.observed['runs'][0]['build']['parameters']={'WIDTH':32};self.reject()
    def test_wrong_compiled_options(self):self.observed['runs'][0]['build']['options']=['different'];self.reject()
    def test_required_assertion_metric_cannot_be_na(self):
        next(p for p in self.contract['metric_policy'] if p['family']=='assertion').update(applicable=False,reason='omitted')
        self.contract['metrics']=[m for m in self.contract['metrics'] if m['family']!='assertion'];self.reject()
    def duplicate_run(self):
        other=copy.deepcopy(self.observed['runs'][0]);other.update(id='run2',seed=8,source_ids=['ev_run2'])
        self.observed['runs'].append(other)
        for m in self.observed['metrics']:m['run_ids'].append('run2')
    def test_merge_unions_bin_identity(self):self.duplicate_run();self.assertEqual(self.outcome(),0)
    def test_merge_must_not_sum_repeated_bins(self):
        self.duplicate_run();self.observed['metrics'][0]['covered']=2;self.reject()
    def test_verdict_json_is_machine_readable(self):
        self.persist();output=self.root/'verdict.json'
        console=io.StringIO()
        with contextlib.redirect_stdout(console):
            code=assess(self.plan,self.index,self.root/'contract.json',self.root/'observations.json',self.today,output=output)
        self.assertNotIn('RESULT: PASS',console.getvalue())
        self.assertEqual(code,0);data=load_json(output);self.assertEqual(data['verdict'],'MET');self.assertFalse(data['human_signoff'])
    def test_existing_output_requires_force(self):
        self.persist();output=self.root/'verdict.json';output.write_text('keep',encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError):assess(self.plan,self.index,self.root/'contract.json',self.root/'observations.json',self.today,output=output)
        self.assertEqual(output.read_text(encoding='utf-8'),'keep')
    def add_waiver(self,oid):
        w=dict(obligation_id=oid,reason='Synthetic approved exception',owner='owner',review=self.review(),expiry='2027-01-01',
               contract_sha256=canonical({k:v for k,v in self.contract.items() if k!='approval'}),baseline=copy.deepcopy(self.baseline),source_id='waiver_'+oid)
        self.observed['waivers'].append(w)
        row=next(r for r in self.rows if r['obligation_id']==oid);row.update(status='waived',notes='waiver=W1; waiver_owner=owner; waiver_expiry=2027-01-01; reason=fixture')
        self.write_plan()
    def test_no_runs_cannot_close_with_waivers(self):
        self.add_waiver('OB-1');self.observed['runs']=[]
        for m in self.observed['metrics']:m.update(run_ids=[],bin_ids=[],covered=0)
        self.assertEqual(self.outcome(),1)
    def test_waiver_requires_record(self):self.add_waiver('OB-1');self.persist();self.refresh=False;self.observed['sources']=[s for s in self.observed['sources'] if s['role']!='waiver_record'];self.reject()
    def test_waiver_must_match_vplan(self):self.add_waiver('OB-1');self.rows[0]['status']='passing';self.write_plan();self.reject()
    def test_waiver_expiry(self):self.add_waiver('OB-1');self.observed['waivers'][0]['expiry']='2020-01-01';self.reject()
    def test_conditional_exit_is_distinct(self):
        self.rows.append(dict(self.rows[0],obligation_id='OB-2'));self.write_plan()
        self.contract['obligations'].append(dict(self.contract['obligations'][0],id='OB-2'))
        m=load_json(self.root/'scope_matrix.json');next(d for d in m['cells'][0]['dimensions'] if d['dimension']=='normal')['obligations'].append('OB-2')
        self.contract['scope_matrix']=self.jsonref('scope_matrix.json',m)
        self.add_waiver('OB-2')
        self.assertEqual(self.outcome(),3)
        self.assertEqual(self.outcome(allow_waivers=True),0)
    def test_plan_stats_not_closure(self):
        self.rows.append(dict(self.rows[0],obligation_id='OB-2',status='failing'));self.write_plan()
        out=io.StringIO()
        with contextlib.redirect_stdout(out):plan_stats(self.plan,None,str(self.index))
        self.assertIn('ALL ROWS MARKED PASSING: 0',out.getvalue());self.assertIn('CLOSURE: NOT ASSESSED',out.getvalue())
    def test_no_vip_manifest_artifact_only(self):
        run=self.root/'evidence';run.mkdir()
        for name in ('compile.log','sim.log','assertions.csv','review.md','coverage/run.dat'):
            p=run/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('synthetic fixture',encoding='utf-8')
        script=Path(__file__).with_name('vlsit_verify_evidence.py')
        cmd=[sys.executable,str(script),'manifest',str(run),'--level','block','--project','selftest','--artifact','block',
             '--version','1','--spec',str(self.root/'spec.md'),'--test','t_transfer','--simulator','synthetic',
             '--simulator-version','fixture','--os','selftest','--compile-option=none','--run-option=none',
             '--seed','1','--timeout-s','5','--coverage','functional=not_measured','--reviewer','selftest',
             '--no-vip-reason','local BFM; synthetic checker test']
        result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        result=subprocess.run([sys.executable,str(script),'check',str(run/'manifest.json')],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertIn('artifact validation only',result.stdout)


def load_json(p):return json.loads(p.read_text(encoding='utf-8-sig'))


if __name__=='__main__':unittest.main()
