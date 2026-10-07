import csv, subprocess, os, hashlib, pathlib

REPOS = os.path.expanduser("~/multi-swe-bench/data/repos")
EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".svelte", ".vue")
TEMPLATE = """# Notes for coding agents

## Where things live

{entries}

## Conventions

- Keep changes minimal and focused on the issue.
- Follow the existing code style of the file you edit.
"""

def label(p):
    s = os.path.basename(p).split(".")[0]
    return os.path.basename(os.path.dirname(p)) if s == "index" else s

def is_src(p):
    b = os.path.basename(p)
    return p.endswith(EXT) and not b.endswith(".d.ts") and ".test." not in b and ".spec." not in b

def read_tsv(path):
    return list(csv.reader(open(path), delimiter="\t", quoting=csv.QUOTE_NONE))

sha = {r[0]: r[4] for r in read_tsv("manifests/candidates_full.tsv")}
rows = []
for r in read_tsv("manifests/candidate_pool.tsv"):
    tid, repo, paths = r[0], r[1], r[7]
    old, new = [s.strip() for s in paths.split(" -> ")]
    clone = f"{REPOS}/{repo}"
    listing = subprocess.run(["git", "-C", clone, "ls-tree", "--name-only", sha[tid], os.path.dirname(new) + "/"],
                             capture_output=True, text=True).stdout.split("\n")
    siblings = sorted(p for p in listing if p and p != new and is_src(p))[:2]
    files = sorted(siblings + [new])
    stale_exists = subprocess.run(["git", "-C", clone, "cat-file", "-e", f"{sha[tid]}:{old}"],
                                  capture_output=True).returncode == 0

    def render(target):
        return TEMPLATE.format(entries="\n".join(f"- `{label(p)}`: `{target if p == new else p}`" for p in files))

    accurate, stale = render(new), render(old)
    folder = pathlib.Path("guides") / tid
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "accurate.md").write_text(accurate)
    (folder / "stale.md").write_text(stale)
    differing = sum(a != b for a, b in zip(accurate.split("\n"), stale.split("\n")))
    rows.append([tid, repo, new, old, len(siblings), differing, int(stale_exists),
                 hashlib.sha256(accurate.encode()).hexdigest()[:12], hashlib.sha256(stale.encode()).hexdigest()[:12]])

with open("manifests/conditions.tsv", "w", newline="") as f:
    csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="\\").writerows(rows)

print(len(rows), "tasks")
print(sum(r[5] == 1 for r in rows), "pairs differ in exactly one line")
print(sum(r[4] == 2 for r in rows), "tasks have two neighbouring entries")
print(sum(r[6] == 1 for r in rows), "tasks where the stale path still exists at the base commit")
