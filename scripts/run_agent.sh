# Usage: bash scripts/run_agent.sh <task.jsonl (one task)> <claude_md_file|none> <outdir>
set -euo pipefail
task=$1; guide=$2; out=$3
MODEL=${MODEL:-claude-sonnet-5-5}
CLAUDE_BIN=${CLAUDE_BIN:-$HOME/.local/share/claude/versions/2.1.292}
TIMEOUT=${TIMEOUT:-1800}

org=$(jq -r .org "$task"); repo=$(jq -r .repo "$task"); num=$(jq -r .number "$task")
image="mswebench/$(echo "${org}_m_${repo}" | tr 'A-Z' 'a-z'):pr-${num}"
workdir="/home/${repo}"
mkdir -p "$out"

jq -r '"Resolve the following GitHub issue in this repository by changing the source code. Do not use the network to look up the fix.\n\n" + ([.resolved_issues[] | "# " + .title + "\n\n" + .body] | join("\n\n---\n\n"))' "$task" > "$out/prompt.txt"

export CLAUDE_CODE_OAUTH_TOKEN=$(tr -d '[:space:]' < "$HOME/.claude_study_token")
cid=$(docker run -d -e CLAUDE_CODE_OAUTH_TOKEN -e DISABLE_AUTOUPDATER=1 -v "$CLAUDE_BIN":/usr/local/bin/claude:ro "$image" sleep infinity)
trap 'docker rm -f "$cid" >/dev/null 2>&1 || true' EXIT

docker exec "$cid" bash -c "rm -f /home/fix.patch /home/test.patch /home/*.sh"
docker exec -w "$workdir" "$cid" bash -c "find . -path ./node_modules -prune -o \( -iname 'CLAUDE.md' -o -iname 'CLAUDE.local.md' -o -iname 'AGENTS.md' -o -name '.cursorrules' -o -name 'copilot-instructions.md' -o -path '*/.claude/*' \) -print" > "$out/preexisting_instruction_files.txt"
if [ "$guide" != "none" ]; then docker cp "$guide" "$cid:$workdir/CLAUDE.md"; fi
docker exec -w "$workdir" "$cid" bash -c "rm -rf .git && git init -q && git add -A && git -c user.name=study -c user.email=study@example.invalid commit -qm base"
docker cp "$out/prompt.txt" "$cid:/tmp/prompt.txt"

start=$(date +%s)
set +e
timeout "$TIMEOUT" docker exec -w "$workdir" "$cid" bash -c 'claude -p "$(cat /tmp/prompt.txt)" --model '"$MODEL"' --strict-mcp-config --disallowedTools "mcp__*,WebSearch,WebFetch" --tools "Bash,Read,Edit,Write,Glob,Grep" --allowedTools "Bash,Read,Edit,Write,Glob,Grep" --permission-mode acceptEdits --no-session-persistence --max-turns 150 --output-format stream-json --verbose' > "$out/trace.jsonl" 2> "$out/stderr.txt"
rc=$?
set -e
end=$(date +%s)

docker exec -w "$workdir" "$cid" bash -c 'git add -A && git diff --cached -- . ":(exclude)CLAUDE.md"' > "$out/agent.patch"

jq -n --arg id "$org/$repo:pr-$num" --arg image "$image" --arg image_id "$(docker image inspect --format '{{.Id}}' "$image")" --arg model "$MODEL" --arg claude "$(basename "$CLAUDE_BIN")" --arg guide "$guide" --argjson rc "$rc" --argjson secs "$((end-start))" '{task:$id, image:$image, image_id:$image_id, model:$model, claude_version:$claude, guide:$guide, exit_code:$rc, wall_seconds:$secs}' > "$out/meta.json"

echo "exit code: $rc, seconds: $((end-start))"
tail -n 1 "$out/trace.jsonl" | jq -c '{subtype, is_error, num_turns, total_cost_usd}' || true
echo "patch bytes: $(wc -c < "$out/agent.patch")"
echo "pre-existing instruction files: $(wc -l < "$out/preexisting_instruction_files.txt")"
