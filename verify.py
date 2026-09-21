#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
VERSION='2.18.0'
BIND=ROOT/'05_Reproduction_and_Verification/SCRT_Research_Package_Binding_v2_18_0.json'

REQUIRED=[
 'README.md','VERSION','LICENSE','CITATION.cff','NOTICE','.gitattributes','.gitignore',
 '01_Theory/SCRT_Theory_at_a_Glance_v2_18_0.md',
 '01_Theory/SCRT_Framework_Overview_v2_18_0.md',
 '01_Theory/SCRT_Assurance_Coherent_Hardening_Phase_Theorem_v2_18_0.md',
 '01_Theory/SCRT_Assurance_Hardening_Proof_and_Scope_Audit_v2_18_0.md',
 '01_Theory/SCRT_Threat_Model_and_Assumption_Boundary_v2_18_0.md',
 '01_Theory/SCRT_Cyber_Architecture_Encoding_Contract_v2_18_0.md',
 '04_Research_Context/SCRT_Claim_Boundary_v2_18_0.md',
 '04_Research_Context/SCRT_Relationship_to_Established_Structures_v2_18_0.md',
 '04_Research_Context/SCRT_Theorem_Status_v2_18_0.md',
 '05_Reproduction_and_Verification/SCRT_Verification_Evidence_Report_v2_18_0.md',
 '06_Examples/README.md',
 '06_Examples/SCRT_Shared_Signing_Root_Recovery_Contention_Worked_Example_v2_18_0.md',
 '06_Examples/SCRT_Realistic_Supply_Chain_Assurance_Worked_Example_v2_18_0.md',
 '06_Examples/SCRT_Exclusive_Recovery_Resource_Worked_Example_v2_18_0.md']

CURRENT_VERIFY=[
 '03_Verification/Regression/SCRT_Integrated_Universal_Assurance_Continuation_Classification_v2_7_0.py',
 '03_Verification/Regression/SCRT_Integrated_Universal_Assurance_Continuation_Independent_Verifier_v2_7_0.py',
 '03_Verification/Generated/SCRT_Generated_Finite_System_Falsification_Verifier_v2_18_0.py',
 '03_Verification/Generated/SCRT_Assumption_Sharpness_and_Countermodel_Audit_v2_18_0.py',
 '03_Verification/Generated/SCRT_Assurance_Hardening_Adversarial_Verification_v2_18_0.py',
 '03_Verification/Hardening_Phase/SCRT_Universal_Assurance_Coherent_Hardening_Theorem_v2_10_0.py',
 '03_Verification/Hardening_Phase/SCRT_Universal_Assurance_Coherent_Hardening_Independent_Verifier_v2_10_0.py',
 '03_Verification/Hardening_Phase/SCRT_Assurance_Interaction_Phase_Boundary_Theorem_v2_16_0.py',
 '03_Verification/Hardening_Phase/SCRT_Assurance_Interaction_Phase_Boundary_Independent_Verifier_v2_16_0.py',
 '03_Verification/Hardening_Phase/SCRT_Assurance_Audit_Complexity_Phase_Boundary_Theorem_v2_17_0.py',
 '03_Verification/Hardening_Phase/SCRT_Assurance_Audit_Complexity_Phase_Boundary_Independent_Verifier_v2_17_0.py']

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def run_script(rel, mode):
    p=ROOT/rel
    cp=subprocess.run([sys.executable,'-B',str(p),mode],cwd=str(p.parent),capture_output=True,text=True)
    if cp.returncode!=0:
        print(cp.stdout,end=''); print(cp.stderr,end='',file=sys.stderr); raise SystemExit(f'component failed: {rel} {mode}')
    out=cp.stdout.strip().splitlines()
    tail=out[-1] if out else ''
    if not any(x in tail for x in ['PASS','status:PASS','TOTAL']):
        # Some scripts end with a status line not strictly last; require PASS somewhere.
        if 'PASS' not in cp.stdout: raise SystemExit(f'component did not report PASS: {rel}')
    print(f"component:{Path(rel).name}:{mode[2:].replace('-','_')}:PASS")

def local_links_ok():
    text=(ROOT/'README.md').read_text(encoding='utf-8')
    links=re.findall(r'\]\((\./[^)#]+)',text)
    bad=[]
    for link in links:
        p=ROOT/link[2:]
        if not p.exists(): bad.append(link)
    return len(links),bad

def integrity():
    total=passed=0
    def ck(cond):
        nonlocal total,passed; total+=1; passed+=int(bool(cond))
    for rel in REQUIRED: ck((ROOT/rel).exists())
    ck((ROOT/'VERSION').read_text().strip()==VERSION)
    data=json.loads(BIND.read_text())
    ck(data.get('version')==VERSION); ck(data.get('presentation_layer_bound') is False)
    presentation_suffixes={'.md','.txt','.cff','.yml','.yaml'}
    ck(not any(Path(rel).suffix.lower() in presentation_suffixes or Path(rel).name in {'README.md','LICENSE','NOTICE'} for rel in data['files']))
    for rel,want in data['files'].items(): ck((ROOT/rel).exists() and digest(ROOT/rel)==want)
    nlinks,bad=local_links_ok(); ck(not bad)
    # UTF-8/LF and no cache artifacts.
    authored=[]
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.md','.txt','.json','.py','.cff','.yml','.yaml'}:
            authored.append(p)
            try: s=p.read_text(encoding='utf-8'); ck('\r' not in s)
            except UnicodeDecodeError: ck(False)
    ck(not any(p.name=='__pycache__' or p.suffix=='.pyc' for p in ROOT.rglob('*')))
    # Prohibited repository-status marketing terms in project-authored research text.
    prohibited=['external '+'release','public '+'release','release '+'candidate','publication '+'candidate','publication'+'-ready','publication '+'quality','break'+'through','internal '+'commentary','internal '+'novelty']
    bad_terms=[]
    for p in authored:
        if 'LICENSES' in p.parts: continue
        low=p.read_text(encoding='utf-8').lower()
        for term in prohibited:
            if term in low: bad_terms.append((str(p.relative_to(ROOT)),term))
    ck(not bad_terms)
    print(f'integrity_checks:PASS:{passed}/{total}:readme_local_links={nlinks}:bound_files={len(data["files"])}')
    if passed!=total:
        if bad: print('bad_links:',bad)
        if bad_terms: print('bad_terms:',bad_terms)
        raise SystemExit(1)

def algorithm_smoke():
    run_script('02_Algorithms_and_Software/SCRT_Canonical_Quotient_Algorithms_v2_7_0.py','--self-test')

def regression_self_tests():
    scripts=sorted((ROOT/'03_Verification/Regression').glob('*.py'))
    for p in scripts: run_script(p.relative_to(ROOT).as_posix(),'--self-test')
    print(f'historical_regression_self_tests:PASS:{len(scripts)}/{len(scripts)}')

def verify_current():
    for rel in CURRENT_VERIFY: run_script(rel,'--verify')
    print(f'mathematical_falsification_components:PASS:{len(CURRENT_VERIFY)}/{len(CURRENT_VERIFY)}')
    print('written_proof_status:COMPLETE_UNDER_DECLARED_SEMANTICS_NOT_MECHANIZED')
    print('mechanized_proofs:NONE')

def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--self-test',action='store_true'); g.add_argument('--verify',action='store_true')
    a=ap.parse_args()
    print(f'SCRT Scientific Package v{VERSION}')
    integrity(); algorithm_smoke()
    if a.verify:
        regression_self_tests(); verify_current()
    print('status:PASS')
if __name__=='__main__': main()
