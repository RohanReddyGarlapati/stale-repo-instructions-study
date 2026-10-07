import csv, random, collections

SEED = 20261007
MAX_AGE = 730
EVENT_CAP = 3
REPO_CAP = 20

# columns: id, repo, difficulty, base_date, rename_date, age_days, rename_commit, paths
rows = list(csv.reader(open("manifests/shortlist_full_aged.tsv"), delimiter="\t", quoting=csv.QUOTE_NONE))

best = {}
for r in rows:
    age = int(r[5])
    if age > MAX_AGE:
        continue
    if r[0] not in best or age < int(best[r[0]][5]):
        best[r[0]] = r

tasks = sorted(best.values(), key=lambda r: r[0])
random.Random(SEED).shuffle(tasks)

per_event = collections.Counter()
per_repo = collections.Counter()
pool = []
for r in tasks:
    event = (r[1], r[6])
    if per_event[event] >= EVENT_CAP or per_repo[r[1]] >= REPO_CAP:
        continue
    per_event[event] += 1
    per_repo[r[1]] += 1
    pool.append(r)

pool.sort(key=lambda r: (r[1], r[0]))
with open("manifests/candidate_pool.tsv", "w", newline="") as f:
    csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="\\").writerows(pool)

print("pool size:", len(pool))
for repo, n in sorted(collections.Counter(r[1] for r in pool).items()):
    print(f"  {repo}: {n}")
print("distinct rename events:", len(per_event))
