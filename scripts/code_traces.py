# Usage: python3 scripts/code_traces.py <outroot>
import csv, json, sys, os, re, glob

root = os.path.expanduser(sys.argv[1])
paths = {r[0]: (r[2], r[3]) for r in csv.reader(open("manifests/conditions.tsv"), delimiter="\t", quoting=csv.QUOTE_NONE)}
NET = re.compile(r"\b(curl|wget|git\s+(clone|fetch|pull|remote)|npm\s+(view|info)|gh\s)|https?://")

print("task\tcondition\trepeat\ttool_calls\tfirst_stale\tfirst_correct\tstale_following\tnetwork_flag")
for run in sorted(glob.glob(f"{root}/runs/*/*-r*")):
    if ".invalid-" in run:
        continue
    tid = os.path.basename(os.path.dirname(run))
    cond, rep = os.path.basename(run).rsplit("-r", 1)
    correct, stale = paths[tid]
    calls = []
    for line in open(f"{run}/trace.jsonl"):
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []) or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                calls.append((block.get("name"), json.dumps(block.get("input", {}))))
    first_stale = next((i for i, (_, s) in enumerate(calls, 1) if stale in s), None)
    first_correct = next((i for i, (_, s) in enumerate(calls, 1) if correct in s), None)
    following = int(first_stale is not None and (first_correct is None or first_stale < first_correct))
    network = int(any(name == "Bash" and NET.search(s) for name, s in calls))
    print(f"{tid}\t{cond}\t{rep}\t{len(calls)}\t{first_stale or 'NA'}\t{first_correct or 'NA'}\t{following}\t{network}")
