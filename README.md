# Stale Repository Instructions Study

A pre-specified experiment on how out-of-date repository guidance affects an AI coding agent. Technical report, not peer reviewed.

**Question:** how much does task-relevant stale guidance (a `CLAUDE.md` that points to a file's pre-rename path) change a coding agent's issue-resolution effort and success, compared with accurate guidance and no guidance?

**Short answer** (23 TypeScript/JavaScript tasks, 3 repositories, Claude Code 2.1.292 with recorded model identifier `claude-sonnet-5-5`, 276 analyzed scheduled runs after documented reruns):

- Stale guidance was associated with about 0.76 more tool calls per run than accurate guidance (9.30 vs 8.54; 95% bootstrap interval [+0.07, +1.49]; sign-flip p = 0.056). The effort evidence is suggestive: the bootstrap interval excludes zero, while the sign-flip test does not meet the .05 threshold.
- No effect on task success was detected (12-task success set; difference −8.3 points, interval [−27.1, +8.3]). The comparison is underpowered, so this is not evidence of no harm.
- In 21 of 92 stale-condition runs, tool inputs referenced the stale path before, or without, referencing the correct path.
- Accurate guidance showed no detectable benefit over no guidance.

These results apply only to this agent, model, staleness type (a renamed file path) and set of repositories. Read [REPORT.md](REPORT.md) for the method, limitations and deviations.

## Where things are

| Path | Contents |
|---|---|
| `REPORT.md` | The write-up: method, results, deviations, limitations |
| `PROTOCOL.md` | Preregistered protocol and Amendments 1.1 to 1.3 |
| `DEVIATIONS.md` | Deviations after the preregistration freeze |
| `preregistration/` | Task-selection rubric, written before any agent run |
| `manifests/` | Task sets (screening, effort, success), condition records |
| `guides/` | The accurate and stale `CLAUDE.md` for each pool task |
| `scripts/` | Task selection, guide generation, run, batch, scoring, trace coding |
| `analysis/primary_analysis.py` | The frozen primary analysis |
| `results/confirmatory/` | Per-run results, schedule, trace coding, cost, analysis output |

The protocol and primary analysis were frozen at the commit tagged `prereg-v1` (`57dc567`); this was not registration in a third-party registry.

## Design in brief

- **Tasks:** real fixed issues from Multi-SWE-bench (Zan et al., 2025) whose fix changes one source file that was renamed earlier in repository history.
- **Conditions:** accurate `CLAUDE.md`, stale `CLAUDE.md` (exactly one line differs), no `CLAUDE.md`.
- **Runs:** 23 tasks × 3 conditions × 4 repeats, conditions shuffled within each task and repeat (seed 20261013).
- **Primary measures:** tool calls per run (all 23 tasks) and task success (the 12 tasks solved in one or two of three no-guidance screening runs).

## Interruptions and exploratory checks

The deviation log records 167 initial session-limit failures before a successful model call: 56/92 accurate, 56/92 stale, and 55/92 no-guidance attempts. Failed attempts and interrupted comparison blocks were rerun under the documented schedule. Similar counts across conditions do not rule out schedule or restart-time effects.

Post hoc checks chosen on October 26, 2026 reproduced the primary effort estimate from committed outputs and found larger differences on complete pre-interruption comparisons: +1.13 tool calls/run on 108 runs and +3.48 on the first complete repeat (69 runs). These exploratory estimates do not replace the primary result or establish that restarting had no effect. See [RERUN_SENSITIVITY.md](RERUN_SENSITIVITY.md).

## Reproducing the analysis

`analysis/primary_analysis.py` takes a run folder as its argument. It reads `results.tsv` there and re-codes tool calls from the raw per-run traces with `scripts/code_traces.py`. The raw traces are not committed, so the committed `results/confirmatory/` folder (which holds the outputs: `analysis.txt`, `results.tsv`, `trace_coding.tsv`, `cost.txt`, `schedule.tsv`) is not enough to rerun the analysis. With the run folder:

```bash
python3 analysis/primary_analysis.py <run folder>
```

Rerunning it on the original confirmatory run folder reproduces `results/confirmatory/analysis.txt` exactly.

A separate post hoc diagnostic can be run from the public summaries without raw traces:

```bash
python3 analysis/rerun_sensitivity.py
```

It joins only the 276 scheduled entries, reproduces summary-based task-level contrasts, and prints the interruption checks. It is not an independent recoding of raw behavior and does not modify the frozen primary analysis. The path-use statement above is a behavioral indicator, not proof of a correctness failure.

Running new agent runs needs Docker, Python 3.12, the [Multi-SWE-bench harness](https://github.com/multi-swe-bench/multi-swe-bench) and a Claude Code installation. The scripts are:

```bash
scripts/run_batch.sh <ids.txt> <repeats> <outroot> <seed>
scripts/score_batch.sh <outroot>
python3 scripts/code_traces.py <outroot>
```

Benchmark data and container images come from Multi-SWE-bench and are not redistributed here. Check the license of each upstream repository before reusing the tasks.

## Citation

Garlapati, R. R. (2026). *Do Stale Repository Instructions Mislead AI Coding Agents?* Technical report, not peer reviewed. Protocol and analysis frozen at tag `prereg-v1`.
