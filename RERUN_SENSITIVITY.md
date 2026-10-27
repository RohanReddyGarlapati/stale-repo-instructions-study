# Post hoc sensitivity checks for interrupted confirmatory runs

Prepared October 26, 2026. These checks were specified after the primary findings were known. They supplement the original analysis and do not change its preregistered status, task sets, estimates, or interpretation.

## What the records establish

The first scheduled batch contained 276 task-condition-repeat entries. The deviation log records 167 session-limit failures: 56 accurate, 56 stale, and 55 no-guidance. It states that these attempts never successfully called the model. Failures began at schedule row 110 and covered the remaining 167 entries. These are first-batch counts, not a count of every process launch in the entire study. The log separately records an abandoned duplicate launch, a later session-limit stop, and the rerunning of interrupted three-condition blocks.

Three already completed runs were set aside so that the two interrupted task-and-repeat blocks could be rerun together: one run in the first block and two in the later block. The final results contain all 276 scheduled entries, with 92 entries per condition. The invalid-run rule was based on error status, rather than patch success or tool-call count. The discarded error traces are not committed, so this check verifies the schedule and final committed outputs and relies on the deviation log for the nature of the failures.

Similar failure counts across conditions do not establish random missingness. In this batch, failure exposure follows schedule position. According to the log, the failures occurred before a successful model call; this differs from discarding an observed long model execution. Nevertheless, resuming at another time can introduce order or session effects that the final committed data cannot rule out.

## Why excluding every rerun task is not estimable

All 23 tasks have at least one entry in the first-wave affected schedule positions. Excluding every task with a rerun therefore leaves zero tasks. There is no defensible task-exclusion estimate to report. The script explicitly records this empty set rather than computing or inventing a result.

## Diagnostic selection rules

Two alternative checks use retained results from before the first interruption. Both preserve complete three-condition comparisons within task-and-repeat blocks. Outcomes were not used to select the subsets. The rules themselves are post hoc and must not be described as preregistered.

The first check includes only complete blocks whose three scheduled positions precede row 110. It includes the first 108 entries, comprising 36 blocks across all 23 tasks. The split block beginning at row 109 is excluded. Each task has one or two repeats in this subset; repeats are averaged within task and condition before calculating task-level differences, so each task receives equal weight.

The second check includes only repeat 1, which finished before the first interruption. It includes 69 runs, one three-condition block for each of the 23 tasks. It provides a balanced-repeat comparison but has fewer observations and greater run-to-run variability.

## Results and interpretation

The script first reproduces the primary effort contrast from committed outputs: stale minus accurate is +0.7609 tool calls per run, with a 95% task-level bootstrap interval of [+0.0652, +1.4891] and sign-flip p = .0556. This matches the saved original analysis to its reported precision. The original success contrast is also reproduced: -0.0833, interval [-0.2708, +0.0833], p = .5389, across 12 tasks.

For the 108-run complete-block subset, the effort difference is +1.1304 tool calls per run, with interval [+0.3043, +2.0435] and p = .0175. The success difference is -0.1250, with interval [-0.4583, +0.2083] and p = .6537. Success uses 51 runs from the same 12-task success set, with repetitions averaged within tasks.

For repeat 1 alone, the effort difference is +3.4783 tool calls per run, with interval [+0.6087, +8.3478] and p = .0138. The success difference is -0.1667, with interval [-0.5000, +0.1667] and p = .6263, using 36 runs across the 12-task success set.

Both post hoc effort estimates remain positive, but they differ substantially in magnitude from the primary estimate. Neither check proves that rerunning had no effect. They also cannot recover a paired comparison of an original successful attempt with its replacement, because the needed original traces and attempt-level provenance are not in the committed files. Their smaller p-values do not replace the primary p-value or establish a confirmatory effect. The primary effort evidence remains suggestive, and the success comparisons remain inconclusive.

## Reproduction and provenance

Run `python analysis/rerun_sensitivity.py` from a checkout containing the study's committed files. The script uses only the Python standard library. It reads `results/confirmatory/schedule.tsv`, `results.tsv`, `trace_coding.tsv`, and `manifests/success-set.txt`; uses seed 20261012 and 10,000 resamples; and follows the original task-level averaging, percentile bootstrap, and sign-flip procedure. Results are saved in `results/confirmatory/rerun_sensitivity.json`.

The trace-coding file contains two extra rows whose keys are outside the final schedule. The new script restricts the join to exact scheduled task-condition-repeat keys and asserts that each of the 276 entries has exactly one coding record. It does not modify the frozen primary analysis. The schedule boundary and failure descriptions come from `DEVIATIONS.md`, items 2, 3, and 6. These checks verify committed outputs; they are not an independent recoding of the unavailable raw traces.

