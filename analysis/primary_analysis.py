# Usage: python3 analysis/primary_analysis.py <outroot>      (set ALL=1 to ignore the task-set files, for testing)
import csv, sys, os, io, random, subprocess, collections

root = os.path.expanduser(sys.argv[1])
SEED, B = 20261012, 10000
res = list(csv.DictReader(open(f"{root}/results.tsv"), delimiter="\t"))
out = subprocess.run([sys.executable, "scripts/code_traces.py", root], capture_output=True, text=True).stdout
coded = {(r["task"], r["condition"], r["repeat"]): r for r in csv.DictReader(io.StringIO(out), delimiter="\t")}
every = {r["task"] for r in res}
read = lambda p: {l.strip() for l in open(p) if l.strip()}
effort = every if os.environ.get("ALL") else read("manifests/effort-set.txt") & every
success = every if os.environ.get("ALL") else read("manifests/success-set.txt") & every

def means(metric, tasks):
    acc, skipped = collections.defaultdict(list), 0
    for r in res:
        if r["task"] not in tasks:
            continue
        raw = r["resolved"] if metric == "resolved" else coded[(r["task"], r["condition"], r["repeat"])]["tool_calls"]
        if raw in ("NA", ""):
            skipped += 1
            continue
        acc[(r["task"], r["condition"])].append(float(raw))
    if skipped:
        print(f"  note: {skipped} runs without a {metric} value were left out")
    return {k: sum(v) / len(v) for k, v in acc.items()}

def contrast(m, a, b, label):
    tasks = sorted({t for t, c in m if (t, a) in m and (t, b) in m})
    d = [m[(t, a)] - m[(t, b)] for t in tasks]
    if not d:
        print(f"  {label}: no tasks"); return
    obs = sum(d) / len(d)
    rng = random.Random(SEED)
    boots = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(B))
    flips = sum(abs(sum(x * rng.choice((-1, 1)) for x in d) / len(d)) >= abs(obs) - 1e-12 for _ in range(B))
    print(f"  {label:26s} tasks={len(d):2d}  mean difference={obs:+.3f}  95% CI [{boots[int(.025*B)]:+.3f}, {boots[int(.975*B)-1]:+.3f}]  sign-flip p={(flips+1)/(B+1):.4f}")

def report(title, metric, tasks):
    print(f"\n== {title} ({len(tasks)} tasks) ==")
    m = means(metric, tasks)
    for c in ("none", "accurate", "stale"):
        v = [x for (t, cc), x in m.items() if cc == c]
        if v:
            print(f"  mean {metric} under {c:9s} {sum(v)/len(v):.3f}")
    contrast(m, "stale", "accurate", "stale minus accurate")
    contrast(m, "stale", "none", "stale minus none")
    contrast(m, "accurate", "none", "accurate minus none")

report("H2 primary: tool calls, effort set", "tool_calls", effort)
report("H1 primary: task success, success set", "resolved", success)
report("Secondary: task success, effort set", "resolved", effort)
for repo in sorted({t.rsplit("-", 1)[0] for t in effort}):
    report(f"By repository {repo}: tool calls", "tool_calls", {t for t in effort if t.startswith(repo + "-")})

stale = [r for k, r in coded.items() if k[1] == "stale" and k[0] in effort]
if stale:
    print(f"\n== Stale-following ==\n  stale-condition runs: {len(stale)}  followed the stale path first: {sum(int(r['stale_following']) for r in stale)}")
print("  runs flagged for network use:", sum(int(r["network_flag"]) for r in coded.values()))
