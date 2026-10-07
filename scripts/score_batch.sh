# Usage: bash scripts/score_batch.sh <outroot>
set -euo pipefail
root=$(cd "$1" && pwd)
msb=$HOME/multi-swe-bench
cd "$msb"; source .venv/bin/activate
cat "$root"/tasks/*.jsonl > "$root/dataset.jsonl"

for key in $(cut -f2,3 "$root/schedule.tsv" | sort -u | tr '\t' '-'); do
  cond=${key%-*}; rep=${key##*-}
  ev="$root/eval/$cond-r$rep"
  [ -s "$ev/output/final_report.json" ] && continue
  mkdir -p "$ev/workdir" "$ev/output" "$ev/logs"
  : > "$ev/patch.jsonl"
  for t in "$root"/tasks/*.jsonl; do
    id=$(basename "$t" .jsonl); p="$root/runs/$id/$cond-r$rep/agent.patch"
    if [ -s "$p" ]; then jq -c --rawfile p "$p" '{org, repo, number, fix_patch: $p}' "$t" >> "$ev/patch.jsonl"; fi
  done
  [ -s "$ev/patch.jsonl" ] || continue
  jq -n --arg r "$ev" --arg d "$root/dataset.jsonl" --arg repos "$msb/data/repos" '{mode:"evaluation", workdir:($r+"/workdir"), patch_files:[$r+"/patch.jsonl"], dataset_files:[$d], force_build:false, output_dir:($r+"/output"), specifics:[], skips:[], repo_dir:$repos, need_clone:true, global_env:[], clear_env:true, stop_on_error:false, max_workers:4, max_workers_build_image:2, max_workers_run_instance:4, log_dir:($r+"/logs"), log_level:"INFO"}' > "$ev/config.json"
  echo "scoring $cond r$rep"
  python -W ignore -m multi_swe_bench.harness.run_evaluation --config "$ev/config.json" > "$ev/run.log" 2>&1 || echo "harness returned an error for $cond r$rep"
done

{
printf 'task\tcondition\trepeat\tresolved\tturns\tcost_usd\tseconds\tpatch_bytes\n'
while IFS=$'\t' read -r id cond rep; do
  run="$root/runs/$id/$cond-r$rep"; rpt="$root/eval/$cond-r$rep/output/final_report.json"; t="$root/tasks/$id.jsonl"
  key="$(jq -r .org "$t")/$(jq -r .repo "$t"):pr-$(jq -r .number "$t")"
  bytes=$(wc -c < "$run/agent.patch" 2>/dev/null || echo 0)
  if [ "$bytes" = "0" ]; then res=0; else res=$(jq -r --arg k "$key" 'if (.resolved_ids | index($k)) then 1 else 0 end' "$rpt" 2>/dev/null || echo NA); fi
  turns=$(tail -n 1 "$run/trace.jsonl" 2>/dev/null | jq -r '.num_turns // "NA"' 2>/dev/null || echo NA)
  cost=$(tail -n 1 "$run/trace.jsonl" 2>/dev/null | jq -r '.total_cost_usd // "NA"' 2>/dev/null || echo NA)
  secs=$(jq -r '.wall_seconds' "$run/meta.json" 2>/dev/null || echo NA)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$cond" "$rep" "$res" "$turns" "$cost" "$secs" "$bytes"
done < "$root/schedule.tsv"
} > "$root/results.tsv"
column -t -s$'\t' "$root/results.tsv"
