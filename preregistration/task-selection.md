# Task selection rubric (path-staleness category)

Written 2026-10-07, before any agent runs.

Source: Multi-SWE-bench full set, TypeScript and JavaScript tasks (580 tasks, 9 repositories).

A task enters the candidate pool only if all of the following hold:

1. Its reference fix changes 3 or fewer files.
2. At least one non-test file changed by the fix was renamed or moved earlier in the repository history (found with git log --follow --diff-filter=R from the task base commit).
3. The most recent such rename is at most 730 days older than the task base commit.

Caps, applied after a seeded random shuffle (seed 20261007):

- At most 3 tasks per rename event (one rename commit in one repository).
- At most 20 tasks per repository.

Each task is assigned to its most recent qualifying rename event. The stale fact for a task is the pre-rename path of that file; the accurate fact is its path at the base commit.

Selection is mechanical (scripts/select_pool.py). No task is chosen or dropped by hand at this stage. Later exclusions (environment fails to build, competing instruction files, difficulty screening) are recorded with reasons.
