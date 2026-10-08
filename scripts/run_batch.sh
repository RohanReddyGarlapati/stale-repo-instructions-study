# Usage: bash scripts/run_batch.sh <ids.txt> <repeats> <outroot> <seed>
set -euo pipefail
ids=$1; reps=$2; root=$3; seed=$4
here=$(cd "$(dirname "$0")/.." && pwd)
pool=$HOME/multi-swe-bench/data/pool/dataset.jsonl
mkdir -p "$root/tasks" "$root/runs"

while read -r id; do
  [ -z "$id" ] && continue
  [ -s "$root/tasks/$id.jsonl" ] && continue
  jq -c --arg id "$id" 'select((.instance_id // "\(.org)__\(.repo)-\(.number)") == $id)' "$pool" | head -n 1 > "$root/tasks/$id.jsonl"
done < "$ids"

if [ ! -s "$root/schedule.tsv" ]; then
python3 - "$ids" "$reps" "$seed" > "$root/schedule.tsv" << 'PY'
import sys, random, os
ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
rng = random.Random(int(sys.argv[3]))
for rep in range(1, int(sys.argv[2]) + 1):
    order = ids[:]
    rng.shuffle(order)
    for i in order:
        conds = os.environ.get("CONDS", "none accurate stale").split()
        rng.shuffle(conds)
        for c in conds:
            print(f"{i}\t{c}\t{rep}")
PY
fi

while IFS=$'\t' read -r id cond rep; do
  out="$root/runs/$id/$cond-r$rep"
  [ -s "$out/meta.json" ] && continue
  case "$cond" in none) guide=none ;; *) guide="$here/guides/$id/$cond.md" ;; esac
  echo "== $(date +%H:%M:%S) $id $cond r$rep"
  bash "$here/scripts/run_agent.sh" "$root/tasks/$id.jsonl" "$guide" "$out" < /dev/null || true
  sub=$(tail -n 1 "$out/trace.jsonl" 2>/dev/null | jq -r 'if (.is_error == true and .subtype == "success") then "api_error" else (.subtype // empty) end' 2>/dev/null || true)
  rc=$(jq -r '.exit_code' "$out/meta.json" 2>/dev/null || echo missing)
  if [ "$sub" != "success" ] && [ "$sub" != "error_max_turns" ] && [ "$rc" != "124" ]; then
    mv "$out" "$out.invalid-$(date +%s)"
    echo "INVALID RUN set aside ($id $cond r$rep). Stopping; rerun this command to resume."
    exit 1
  fi
done < "$root/schedule.tsv"
echo "all scheduled runs complete"
