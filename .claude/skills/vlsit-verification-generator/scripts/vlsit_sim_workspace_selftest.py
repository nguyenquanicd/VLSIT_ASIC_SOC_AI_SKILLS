#!/usr/bin/env python3
# Function : regression-test retention, dependency checks and actually executed replay
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
"""Synthetic Python producer only; these tests do not simulate hardware."""
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from vlsit_sim_workspace import init, seal, check, execute, MANIFEST, CATALOG, sha

RUNNER = '''import sys,json,os
from pathlib import Path
stage=sys.argv[1];run=Path(sys.argv[2]);name=run.name
assert 'UNDECLARED_HOST_STATE' not in os.environ
print(os.environ.get('TEST_SECRET','no secret'))
if stage=='compile':
 if 'compilefail' in name: sys.exit(7)
 if 'missingbuild' not in name: (run/'build/simulator.bin').write_text('synthetic build',encoding='utf-8')
 if 'preseed' in name: (run/'reports/result.json').write_text('{}',encoding='utf-8')
else:
 if 'simfail' in name: sys.exit(9)
 if 'noresult' in name: sys.exit(0)
 if 'fatal' in name: print('FATAL: synthetic simulator error')
 if 'mutate' in name: (Path(os.environ['VLSIT_SNAPSHOT'])/'tb/top.sv').write_text('changed',encoding='utf-8')
 if 'timeout' in name:
  import time
  time.sleep(4)
 result={'schema_version':1,'complete':'incomplete' not in name,'configuration':'cfg','test':'synthetic',
  'top':'tb','seed':7,'baseline_id':'wrong' if 'wrongbaseline' in name else os.environ['VLSIT_BASELINE_ID'],'cases':[{'id':'smoke','status':'pass','checks':0 if 'unchecked' in name else 2,'errors':1 if 'errors' in name else 0}],
  'observables':{'value':2 if 'mismatch' in name else 1}}
 (run/'reports/result.json').write_text(json.dumps(result),encoding='utf-8')
'''


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.rtl = self.base / 'rtl'
        self.rtl.mkdir()
        (self.rtl / 'dut.sv').write_text('module dut; endmodule\n', encoding='utf-8')
        self.root = self.base / 'sim'
        self.call(init, self.root, self.rtl)
        p = self.root / 'README.md'
        p.write_text(re.sub('__FILL_[A-Z_]+__', 'Synthetic package fixture.', p.read_text(encoding='utf-8')), encoding='utf-8')
        shutil.copy2(self.rtl / 'dut.sv', self.root / 'dut/dut.sv')
        (self.root / 'tb/top.sv').write_text('module tb; endmodule\n', encoding='utf-8')
        (self.root / 'tests/scenarios.json').write_text('{}', encoding='utf-8')
        (self.root / 'scripts/project_runner.py').write_text(RUNNER, encoding='utf-8')
        self.profile = dict(schema_version=2, configuration='cfg', test='synthetic', top='tb', seed=7,
            environment_policy=dict(mode='isolated', empty_reason='Synthetic runner uses absolute executables and no extra variables'),
            environment=[], tools=[dict(name='Synthetic Python producer',version_argv=[sys.executable,'--version'],status='not_run',reason='Measured during actual execute/replay')],
            commands=[dict(name=s,stage=s,argv=[sys.executable,'-c','print(1)'],cwd='runs/example/build',environment=[],timeout_s=30,status='not_run',reason='Documentation only') for s in ('compile','simulate','replay')],
            cold_replay=dict(status='not_run',reason='Outcomes use generated receipts'),external_dependencies=[],dependency_export='env/build_inputs.json',
            replay_plan=dict(runner='scripts/project_runner.py',compile=dict(argv=[sys.executable,'{snapshot}/scripts/project_runner.py','compile','{run}'],timeout_s=30),
                simulate=dict(argv=[sys.executable,'{snapshot}/scripts/project_runner.py','simulate','{run}'],timeout_s=30),build_outputs=['build/simulator.bin'],result='reports/result.json',expected_cases=['smoke']))
        self.profile['replay_plan']['result_producer']=dict(status='qualified',reviewer='Synthetic test fixture',scope='synthetic',evidence='docs/producer_qualification.md')
        (self.root/'docs/producer_qualification.md').write_text('Synthetic helper qualification only; not RTL evidence.',encoding='utf-8')
        self.export = dict(schema_version=1,method='reviewed_manual',reviewer='Synthetic test fixture',status='reviewed',unresolved=[],include_dirs=[],
            inputs=['dut/dut.sv','tb/top.sv','tests/scenarios.json','scripts/project_runner.py'])
        self.save()

    def call(self, function, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return function(*args)

    def save(self):
        (self.root / 'env/replay_manifest.json').write_text(json.dumps(self.profile), encoding='utf-8')
        (self.root / 'env/build_inputs.json').write_text(json.dumps(self.export), encoding='utf-8')

    def sealed(self):
        self.assertEqual(self.call(seal, self.root, False), 0)
        return json.loads((self.root / MANIFEST).read_text(encoding='utf-8'))['baseline_id']

    def invalid_seal(self):
        with self.assertRaises((ValueError, KeyError, OSError)):
            self.call(seal, self.root, False)

    def invalid_check(self):
        with self.assertRaises((ValueError, KeyError, OSError)):
            self.call(check, self.root)

    def test_valid_retained_package(self):
        self.sealed(); self.assertEqual(self.call(check,self.root),0)

    def test_init_refuses_nonempty(self):
        with self.assertRaises(ValueError): self.call(init,self.root,self.rtl)

    def test_init_refuses_inside_rtl(self):
        with self.assertRaises(ValueError): self.call(init,self.rtl/'sim',self.rtl)

    def test_init_refuses_same_directory(self):
        with self.assertRaises(ValueError): self.call(init,self.rtl,self.rtl)

    def test_init_refuses_rtl_inside_target(self):
        with self.assertRaises(ValueError): self.call(init,self.base,self.rtl)

    def test_empty_dut(self):
        (self.root/'dut/dut.sv').unlink(); self.invalid_seal()

    def test_empty_tb(self):
        (self.root/'tb/top.sv').unlink(); self.invalid_seal()

    def test_unfinished_readme(self):
        (self.root/'README.md').write_text('__FILL_PROJECT__',encoding='utf-8'); self.invalid_seal()

    def test_missing_project_runner(self):
        (self.root/'scripts/project_runner.py').unlink(); self.invalid_seal()

    def test_missing_dependency_export_input(self):
        self.export['inputs'].append('env/missing.f'); self.save(); self.invalid_seal()

    def test_unresolved_dependency(self):
        self.export['unresolved']=['missing_agent.svh']; self.save(); self.invalid_seal()

    def test_missing_command_filelist(self):
        self.profile['commands'][0]['argv'] += ['-f','../lost/filelist.f']; self.save(); self.invalid_seal()

    def test_literal_include_missing(self):
        (self.root/'tb/top.sv').write_text('`include "missing_agent.svh"',encoding='utf-8'); self.invalid_seal()

    def test_dependency_export_omits_model(self):
        (self.root/'models/model.py').write_text('print(1)',encoding='utf-8'); self.invalid_seal()

    def test_include_retained(self):
        (self.root/'tb/agent.svh').write_text('// fixture',encoding='utf-8')
        (self.root/'tb/top.sv').write_text('`include "agent.svh"',encoding='utf-8')
        self.export['inputs'].append('tb/agent.svh'); self.save(); self.sealed()

    def test_empty_environment_needs_reason(self):
        self.profile['environment_policy']['empty_reason']=''; self.save(); self.invalid_seal()

    def variable(self):
        self.profile['environment']=[dict(name='TEST_SETTING',purpose='fixture',source='explicit config',override='no override',setup_order=0,required=True,secret=False,value='value')]

    def test_variable_metadata_missing(self):
        self.variable(); del self.profile['environment'][0]['source']; self.save(); self.invalid_seal()

    def test_secret_plaintext(self):
        self.variable(); self.profile['environment'][0].update(secret=True,provisioning='external host variable'); self.save(); self.invalid_seal()

    def test_undocumented_command_variable(self):
        self.profile['commands'][0]['environment']=['UNKNOWN']; self.save(); self.invalid_seal()

    def test_inherited_environment_forbidden(self):
        self.profile['environment_policy']['mode']='inherit'; self.save(); self.invalid_seal()

    def test_escaping_cwd(self):
        self.profile['commands'][0]['cwd']='../outside'; self.save(); self.invalid_seal()

    def test_handwritten_replay_pass_even_with_old_log(self):
        (self.root/'runs/old').mkdir()
        log=self.root/'runs/old/log'; log.write_text('FATAL: stale synthetic log',encoding='utf-8')
        self.profile['commands'][2].update(status='pass',exit_code=0,log='runs/old/log',log_sha256=sha(log))
        self.profile['cold_replay']=dict(status='pass',log='runs/old/log',log_sha256=sha(log))
        self.save(); self.invalid_seal()

    def test_missing_exit_code(self):
        self.profile['commands'][0]['status']='pass'; self.save(); self.invalid_seal()

    def test_status_exit_contradiction(self):
        self.profile['commands'][0].update(status='pass',exit_code=1); self.save(); self.invalid_seal()

    def test_editable_source_changed(self):
        self.sealed(); (self.root/'tb/top.sv').write_text('changed',encoding='utf-8'); self.invalid_check()

    def test_old_snapshot_survives_editable_changes(self):
        baseline=self.sealed(); (self.root/'tb/top.sv').write_text('changed',encoding='utf-8')
        self.assertEqual(self.call(check,self.root,baseline),0)

    def test_snapshot_tamper(self):
        baseline=self.sealed(); (self.root/'snapshots'/baseline/'tb/top.sv').write_text('changed',encoding='utf-8'); self.invalid_check()

    def test_root_makefile_preserved_and_loss_detected(self):
        (self.root/'Makefile').write_text('all:',encoding='utf-8'); self.export['inputs'].append('Makefile'); self.save()
        baseline=self.sealed(); self.assertTrue((self.root/'snapshots'/baseline/'Makefile').is_file())
        (self.root/'Makefile').unlink(); self.invalid_check()

    def test_merged_coverage_loss(self):
        (self.root/'coverage/merged.xml').write_text('<coverage/>',encoding='utf-8'); self.sealed()
        (self.root/'coverage/merged.xml').unlink(); self.invalid_check()

    def test_failed_history_loss(self):
        run=self.root/'runs/failed'; run.mkdir(); (run/'failure.log').write_text('failure',encoding='utf-8')
        self.sealed(); shutil.rmtree(run); self.invalid_check()

    def test_historical_run_file_loss(self):
        run=self.root/'runs/failed'; run.mkdir(); (run/'failure.log').write_text('failure',encoding='utf-8')
        self.sealed(); (run/'failure.log').unlink(); self.invalid_check()

    def test_historical_baseline_loss(self):
        old=self.sealed(); (self.root/'tb/top.sv').write_text('new',encoding='utf-8')
        self.assertEqual(self.call(seal,self.root,True),0); shutil.rmtree(self.root/'snapshots'/old); self.invalid_check()

    def test_force_cannot_hide_history_loss(self):
        old=self.sealed(); (self.root/'tb/top.sv').write_text('new',encoding='utf-8')
        self.call(seal,self.root,True); shutil.rmtree(self.root/'snapshots'/old)
        with self.assertRaises(ValueError): self.call(seal,self.root,True)

    def test_lost_catalog_blocks_reinitialization(self):
        self.sealed(); (self.root/CATALOG).unlink()
        with self.assertRaises(ValueError): self.call(seal,self.root,True)

    def test_force_preserves_old_snapshot(self):
        old=self.sealed(); (self.root/'tb/top.sv').write_text('new',encoding='utf-8')
        with self.assertRaises(ValueError): self.call(seal,self.root,False)
        self.call(seal,self.root,True); self.assertEqual(self.call(check,self.root,old),0)

    def test_actual_synthetic_execution_and_replay(self):
        baseline=self.sealed()
        self.assertEqual(self.call(execute,self.root,baseline,'original'),0)
        self.assertEqual(self.call(execute,self.root,baseline,'replay','original'),0)
        self.assertEqual(self.call(check,self.root),0)
        receipt=json.loads((self.root/'runs/replay/receipt.json').read_text(encoding='utf-8'))
        self.assertEqual([c['stage'] for c in receipt['commands']],['version','compile','simulate'])
        self.assertEqual(receipt['comparison'],'exact_normalized_result')

    def test_replay_requires_executed_reference(self):
        baseline=self.sealed()
        with self.assertRaises(ValueError): self.call(execute,self.root,baseline,'replay','missing')

    def test_replay_refuses_existing_run_id(self):
        baseline=self.sealed(); self.call(execute,self.root,baseline,'original')
        with self.assertRaises(ValueError): self.call(execute,self.root,baseline,'original','original')

    def test_unqualified_producer_blocks_execution(self):
        self.profile['replay_plan']['result_producer']['status']='pending'; self.save(); baseline=self.sealed()
        with self.assertRaises(ValueError): self.call(execute,self.root,baseline,'original')

    def test_pending_dependency_review_blocks_execution(self):
        self.export['status']='pending'; self.save(); baseline=self.sealed()
        with self.assertRaises(ValueError): self.call(execute,self.root,baseline,'original')

    def test_environment_isolation(self):
        baseline=self.sealed(); old=os.environ.get('UNDECLARED_HOST_STATE'); os.environ['UNDECLARED_HOST_STATE']='must not leak'
        try: self.assertEqual(self.call(execute,self.root,baseline,'isolated'),0)
        finally:
            if old is None: os.environ.pop('UNDECLARED_HOST_STATE',None)
            else: os.environ['UNDECLARED_HOST_STATE']=old

    def test_missing_compile_output(self): self.failed_execution('missingbuild')
    def test_compile_nonzero(self): self.failed_execution('compilefail')
    def test_simulation_nonzero(self): self.failed_execution('simfail')
    def test_zero_exit_without_result(self): self.failed_execution('noresult')
    def test_zero_exit_with_fatal(self): self.failed_execution('fatal')
    def test_zero_checks(self): self.failed_execution('unchecked')
    def test_nonzero_errors(self): self.failed_execution('errors')
    def test_incomplete_simulation(self): self.failed_execution('incomplete')
    def test_compile_preseeds_result(self): self.failed_execution('preseed')

    def failed_execution(self,name):
        baseline=self.sealed(); self.assertEqual(self.call(execute,self.root,baseline,name),2)
        self.assertEqual(json.loads((self.root/'runs'/name/'receipt.json').read_text(encoding='utf-8'))['status'],'fail')
        self.assertEqual(self.call(check,self.root),0)

    def test_simulation_timeout(self):
        self.profile['replay_plan']['simulate']['timeout_s']=1; self.save(); self.failed_execution('timeout')

    def test_result_mismatch(self):
        baseline=self.sealed(); self.call(execute,self.root,baseline,'original')
        self.assertEqual(self.call(execute,self.root,baseline,'mismatch','original'),2)

    def test_snapshot_mutation_blocks_success(self):
        baseline=self.sealed(); self.assertEqual(self.call(execute,self.root,baseline,'mutate'),2); self.invalid_check()

    def test_run_receipt_loss(self):
        baseline=self.sealed(); self.call(execute,self.root,baseline,'original')
        (self.root/'runs/original/receipt.json').unlink(); self.invalid_check()

    def test_command_log_loss(self):
        baseline=self.sealed(); self.call(execute,self.root,baseline,'original')
        (self.root/'runs/original/compile_1.log').unlink(); self.invalid_check()

    def test_wrong_baseline_result(self): self.failed_execution('wrongbaseline')

    def test_missing_declared_case(self):
        self.profile['replay_plan']['expected_cases'].append('missing_case'); self.save(); self.failed_execution('missingcase')

    def test_empty_tool_version_output(self):
        self.profile['tools'][0]['version_argv']=[sys.executable,'-c','pass']; self.save(); self.failed_execution('emptyversion')

    def test_cross_baseline_reference_rejected(self):
        old=self.sealed(); self.call(execute,self.root,old,'original')
        p=self.root/'README.md'; p.write_text(p.read_text(encoding='utf-8')+'\nnew baseline',encoding='utf-8')
        self.call(seal,self.root,True)
        new=json.loads((self.root/MANIFEST).read_text(encoding='utf-8'))['baseline_id']
        with self.assertRaises(ValueError): self.call(execute,self.root,new,'replay','original')

    def test_unknown_historical_receipt_cannot_be_reference(self):
        run=self.root/'runs/imported'; run.mkdir(); (run/'receipt.json').write_text('{}',encoding='utf-8')
        baseline=self.sealed()
        with self.assertRaises(ValueError): self.call(execute,self.root,baseline,'replay','imported')

    def test_secret_output_redacted(self):
        self.profile['environment']=[dict(name='TEST_SECRET',purpose='synthetic fixture',source='externally provisioned',override='host source',setup_order=0,required=True,secret=True,provisioning='test-only injected value')]
        self.save(); baseline=self.sealed(); previous=os.environ.get('TEST_SECRET'); os.environ['TEST_SECRET']='synthetic-secret-value'
        try:
            self.assertEqual(self.call(execute,self.root,baseline,'secret'),0)
            for p in (self.root/'runs/secret').glob('*.log'):
                self.assertNotIn('synthetic-secret-value',p.read_text(encoding='utf-8'))
        finally:
            if previous is None: os.environ.pop('TEST_SECRET',None)
            else: os.environ['TEST_SECRET']=previous

    def test_missing_secret_creates_no_unregistered_run(self):
        self.profile['environment']=[dict(name='VLSIT_TEST_ABSENT_SECRET',purpose='test',source='host variable',override='no override',setup_order=0,required=True,secret=True,provisioning='external')]
        self.save(); baseline=self.sealed()
        with self.assertRaises(ValueError): self.call(execute,self.root,baseline,'absent')
        self.assertFalse((self.root/'runs/absent').exists())
        self.assertEqual(self.call(check,self.root),0)

    def test_tool_version_difference_blocks_replay(self):
        self.profile['tools'][0]['version_argv']=[sys.executable,'-c',"import os;print(os.environ['VLSIT_RUN_ID'])"]
        self.save(); baseline=self.sealed(); self.assertEqual(self.call(execute,self.root,baseline,'original'),0)
        self.assertEqual(self.call(execute,self.root,baseline,'replay','original'),2)

    def test_copied_helper_cli_executes_and_replays(self):
        baseline=self.sealed(); helper=str(self.root/'scripts/vlsit_sim_workspace.py')
        common=['--root',str(self.root),'--baseline',baseline]
        for action,extra in [('execute',['--run-id','cli_original']),('replay',['--run-id','cli_replay','--reference-run','cli_original'])]:
            result=subprocess.run([sys.executable,helper,action,*common,*extra],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('producer_scope=synthetic',result.stdout)
            if action=='replay': self.assertIn('REPLAY_EXECUTED: MATCH',result.stdout)
        self.assertEqual(self.call(check,self.root),0)

    def test_copied_project_checker(self):
        self.sealed()
        result=subprocess.run([sys.executable,str(self.root/'scripts/vlsit_sim_workspace.py'),'check','--root',str(self.root)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('PACKAGE_INTEGRITY: VALID',result.stdout); self.assertNotIn('REPLAY_EXECUTED: MATCH',result.stdout)

    def test_relocated_whole_package(self):
        baseline=self.sealed(); other=self.base/'relocated'; shutil.copytree(self.root,other)
        self.assertEqual(self.call(check,other),0)
        self.assertEqual(self.call(execute,other,baseline,'relocated'),0)

    def test_schema_one_explicitly_rejected(self):
        self.profile['schema_version']=1; self.save(); self.invalid_seal()


if __name__=='__main__':
    unittest.main()
