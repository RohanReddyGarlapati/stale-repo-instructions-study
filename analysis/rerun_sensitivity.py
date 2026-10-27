"""Post hoc interruption diagnostics from committed results, not raw traces.

Run from the repository root: python analysis/rerun_sensitivity.py
Selection rules were chosen on 2026-10-26 after primary results were known.
The boundary at schedule row 110 comes from DEVIATIONS.md, item 2.
Do not replace the preregistered analysis with these diagnostics.
"""
import collections
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results' / 'confirmatory'
SEED, B = 20261012, 10000

def key(r):
    return r['task'], r['condition'], r['repeat']

def read_tsv(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))

def summarize(rows, metric):
    groups = collections.defaultdict(list)
    for r in rows:
        groups[(r['task'], r['condition'])].append(float(r[metric]))
    means = {k: sum(v)/len(v) for k,v in groups.items()}
    tasks = sorted({t for t,c in means})
    assert all((t,c) in means for t in tasks for c in ('none','accurate','stale'))
    for t in tasks:
        assert len({len(groups[t,c]) for c in ('none','accurate','stale')}) == 1
    diffs = [means[t,'stale']-means[t,'accurate'] for t in tasks]
    obs = sum(diffs)/len(diffs)
    rng = random.Random(SEED)
    boot = sorted(sum(rng.choice(diffs) for _ in diffs)/len(diffs) for _ in range(B))
    flip = sum(abs(sum(x*rng.choice((-1,1)) for x in diffs)/len(diffs)) >= abs(obs)-1e-12 for _ in range(B))
    return dict(tasks=len(tasks),runs=len(rows),
        means={c:sum(means[t,c] for t in tasks)/len(tasks) for c in ('none','accurate','stale')},
        stale_minus_accurate=obs,bootstrap_95=[boot[int(.025*B)],boot[int(.975*B)-1]],
        sign_flip_p=(flip+1)/(B+1))

def main():
    with (BASE/'schedule.tsv').open(encoding='utf-8',newline='') as f:
        schedule = [tuple(r) for r in csv.reader(f, delimiter='\t') if r]
    assert len(schedule)==len(set(schedule))==276
    scheduled=set(schedule)
    results=read_tsv(BASE/'results.tsv')
    assert len(results)==276 and {key(r) for r in results}==scheduled
    coding=read_tsv(BASE/'trace_coding.tsv')
    selected=[r for r in coding if key(r) in scheduled]
    counts=collections.Counter(key(r) for r in selected)
    assert set(counts)==scheduled and all(n==1 for n in counts.values()), 'Nonunique schedule join'
    coded={key(r):r for r in selected}
    rows=[dict(r,tool_calls=coded[key(r)]['tool_calls']) for r in results]
    assert not any(r['tool_calls'] in ('','NA') for r in rows)
    with (ROOT/'manifests'/'success-set.txt').open(encoding='utf-8') as f:
        success={line.strip() for line in f if line.strip()}
    blocks=collections.defaultdict(list)
    for i,k in enumerate(schedule,1): blocks[k[0],k[2]].append((i,k))
    assert all(len(v)==3 for v in blocks.values())
    # All three conditions must precede row 110; drop row 109's split block.
    before={k for v in blocks.values() if max(i for i,k in v)<110 for i,k in v}
    repeat1={k for k in schedule if k[2]=='1'}
    # Recorded first-wave failures were all slots 110 through 276.
    first_failure_slots=schedule[109:]
    failure_tasks={k[0] for k in first_failure_slots}
    populations={'primary_scheduled':scheduled,'pre_interruption_complete_blocks':before,
                 'first_complete_repeat':repeat1}
    output=dict(post_hoc=True,seed=SEED,resamples=B,
        initial_schedule_slots=276,initial_session_limit_failures=167,
        failure_distribution=dict(collections.Counter(k[1] for k in first_failure_slots)),
        tasks_with_initial_failure=len(failure_tasks),
        tasks_remaining_after_excluding_rerun_tasks=len({k[0] for k in schedule}-failure_tasks),
        split_block_at_first_stop=[list(k) for i,k in enumerate(schedule,1) if i in (109,110,111)],
        schedule_join_extra_coding_rows=len(coding)-len(selected),
        results={})
    assert len(first_failure_slots)==167
    assert output['failure_distribution']==dict(accurate=56,none=55,stale=56)
    assert len(before)==108 and len(repeat1)==69
    for name,keys in populations.items():
        subset=[r for r in rows if key(r) in keys]
        output['results'][name]={'effort':summarize(subset,'tool_calls'),
            'success':summarize([r for r in subset if r['task'] in success],'resolved')}
    print(json.dumps(output,indent=2))

if __name__=='__main__': main()

