   # Usage: bash scripts/rename_history.sh <candidates.tsv> <org/repo> <path-to-clone>
   # For each source file changed by a task's fix, list earlier renames of that file.
   set -euo pipefail
   tsv=$1; repo=$2; clone=$3
   awk -F'\t' -v r="$repo" '$3==r' "$tsv" | while IFS=$'\t' read -r id lang rp diff sha n files; do
     IFS=';' read -ra arr <<< "$files"
     for f in "${arr[@]}"; do
       case "$f" in *__tests__*|*.spec.*|*.test.*|*/test/*|*/tests/*) continue;; esac
       renames=$(git -C "$clone" log --follow --diff-filter=R --name-status \
           --format='COMMIT %h %ad' --date=short "$sha" -- "$f" < /dev/null 2>/dev/null \
         | awk '/^COMMIT/{c=$2" "$3} /^R/{print c" "$2" -> "$3}' | head -n 3 | paste -sd'|' -)
       printf '%s\t%s\t%s\t%s\n' "$id" "$diff" "$f" "${renames:-NONE}"
     done
   done
