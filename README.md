# Stale Repository Instructions Study

A preregistered experiment on how out-of-date repository guidance affects an AI coding agent.

**Question:** how much does task-relevant stale guidance (a `CLAUDE.md` that points to a file's pre-rename path) change a coding agent's issue-resolution effort and success, compared with accurate guidance and no guidance?

**Short answer** (23 TypeScript/JavaScript tasks, 3 repositories, Claude Code with `claude-sonnet-5-5`, 276 valid runs):

- Stale guidance was associated with about 0.76 more tool calls per run than accurate guidance (9.30 vs 8.54; 95% bootstrap interval [+0.07, +1.49]; sign-flip p = 0.056). This is borderline evidence of a small effort cost.
- No effect on task success was detected (12-task success set; difference −8.3 points, interval [−27.1, +8.3]). The comparison is underpowered, so this is not evidence of no harm.
- The agent went to the stale path first in 21 of 92 stale-condition runs (23%).
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

The preregistration is the commit tagged `prereg-v1` (`57dc567`).

## Design in brief

- **Tasks:** real fixed issues from Multi-SWE-bench (Zan et al., 2025) whose fix changes one source file that was renamed earlier in repository history.
- **Conditions:** accurate `CLAUDE.md`, stale `CLAUDE.md` (exactly one line differs), no `CLAUDE.md`.
- **Runs:** 23 tasks × 3 conditions × 4 repeats, conditions shuffled within each task and repeat (seed 20261013).
- **Primary measures:** tool calls per run (all 23 tasks) and task success (the 12 tasks solved in one or two of three no-guidance screening runs).

## Reproducing the analysis

`analysis/primary_analysis.py` takes a run folder as its argument. It reads `results.tsv` there and re-codes tool calls from the raw per-run traces with `scripts/code_traces.py`. The raw traces are not committed, so the committed `results/confirmatory/` folder (which holds the outputs: `analysis.txt`, `results.tsv`, `trace_coding.tsv`, `cost.txt`, `schedule.tsv`) is not enough to rerun the analysis. With the run folder:

```bash
python3 analysis/primary_analysis.py <run folder>
```

Rerunning it on the original confirmatory run folder reproduces `results/confirmatory/analysis.txt` exactly.

Running new agent runs needs Docker, Python 3.12, the [Multi-SWE-bench harness](https://github.com/multi-swe-bench/multi-swe-bench) and a Claude Code installation. The scripts are:

```bash
scripts/run_batch.sh <ids.txt> <repeats> <outroot> <seed>
scripts/score_batch.sh <outroot>
python3 scripts/code_traces.py <outroot>
```

Benchmark data and container images come from Multi-SWE-bench and are not redistributed here. Check the license of each upstream repository before reusing the tasks.

## Citation

Garlapati, R. R. (2026). *Do Stale Repository Instructions Mislead AI Coding Agents?* Preregistered study, tag `prereg-v1`.
