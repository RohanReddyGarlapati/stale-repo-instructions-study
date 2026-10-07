# Do Stale Repository Instructions Mislead AI Coding Agents?

**Protocol status:** Planned study; pilot results will not be treated as confirmatory.  
**Version:** 1.0 (to be frozen before pilot execution)  
**Owner:** Rohan Reddy Garlapati  
**Last updated:** 2026-10-06

## Research question and scope

**How much does task-relevant stale repository guidance change coding-agent issue-resolution success and effort, compared with accurate guidance and no guidance?** This is a controlled empirical study of stale context. It is not a new general-purpose benchmark and will not claim to establish that stale instructions are common across all software repositories.

### Hypotheses

- **H1 (primary):** Task success is lower with stale instructions than with their accurate minimal-pair versions.
- **H2 (secondary):** Stale instructions increase agent effort or cost, measured by tool calls, elapsed time, and available token/cost telemetry.
- **H3 (exploratory):** Effects vary by stale-fact category and by whether the case is history-derived or synthetic.

A null or mixed result is informative. Conclusions will be limited to the selected tasks, repositories, agent, and model versions.

## Task source, eligibility, and sampling

Use **real, fixed issue-resolution tasks with a reproducible failing-before / passing-after test**. The preferred source is the TypeScript and JavaScript subset of [Multi-SWE-bench](https://github.com/multi-swe-bench/multi-swe-bench), whose benchmark repository is Apache-2.0, spans these languages, publishes task data, and documents a Docker-based harness. The separate environment repository is MIT-licensed. Before inclusion, record the license and attribution requirements for each dataset artifact, task repository, and container/image; the benchmark license does not replace upstream repository licenses. Confirm the selected environments build and tests reproduce. If setup or licensing blocks this source, select a documented alternative with the same fixed-issue and reproducible-test properties; record the change before examining outcomes.

Start task hunting with the published **Multi-SWE-bench flash (300 instances)** or **mini (400 instances)** subsets and available prebuilt images, then filter for TypeScript/JavaScript and verify each selected image/task. This can reduce setup work, but does not guarantee a ready-to-run image or an eligible task. Time-box candidate discovery to **three days**; if fewer than the planned number meet criteria, use the fallback design below rather than weakening eligibility.

Select up to **25 study tasks** from at least **5 repositories**, plus **5 pilot tasks** from the same eligible pool that will not enter confirmatory analysis. The fallback uses 15 of the locked eligible study tasks. A task is eligible only if:

1. It is a fixed issue with a reference patch and tests that fail on the base revision and pass on the fixed revision.
2. The base environment can be built and reset reproducibly, and the test command and timeout are recorded.
3. A documented stale fact can be made directly relevant to resolving the issue: the task touches the referenced path/API or requires behavior described by that fact. Exclude tasks for which the stale fact is incidental.
4. The stale fact is plausible repository guidance, not a fabricated instruction to fail. Preserve the issue statement, base code, and tests across conditions.

Freeze the candidate pool, selection rubric, and exclusions before screening. Select across repositories and, where feasible, stale-fact categories. Do not choose tasks based on treatment-condition outcomes. To screen for floor/ceiling risk without using treatment-condition outcomes, run **three no-guidance screening attempts per candidate** using the locked agent/model configuration. Retain only candidates with success in **1–2 of 3** attempts (approximately the prespecified 20%–80% band at this coarse resolution); keep the five pilot tasks out of the study set. Record screening outcomes and apply the rule mechanically before locking task IDs. This filter narrows inference to tasks of intermediate baseline difficulty.

Screening is a distinct budgeted stage, not part of the 30-run feasibility pilot or confirmatory total. After the harness passes the pilot checks, run the first **3 screening attempts** (one candidate, three repeats) and measure marginal runtime and cost. Use that estimate, the spending cap, deadline, and a documented candidate-pool estimate to set and record the maximum number of candidates to screen before continuing. Do not exceed the cap; if screening yield is too low to fill the primary set, use the fallback only if at least 15 eligible study tasks meet the same rule. Include every screening attempt, including failed or invalid attempts, in the budget and report.

## Conditions and stale-case construction

Each task has **three conditions**:

1. **Accurate guidance:** a concise repository instruction containing the relevant fact in its current, correct form.
2. **Stale guidance:** the minimal-pair version with the targeted fact made obsolete; every other instruction, layout, and wording stays identical.
3. **No study guidance:** remove the study-provided instruction file. Preserve ordinary repository content, but inventory it and prevent competing agent instruction files from affecting the run.

There is **no separate padded-accurate condition**: minimal pairs hold structure and length constant by construction. Keep the no-guidance condition free of a study-provided file; do not silently remove or alter ordinary project documentation. Any existing instruction-like files must be documented and either consistently retained in all conditions or the task excluded if they confound treatment.

Classify each stale case before evaluation as:

- **History-derived:** supported by repository history, such as an older instruction file, README/contributing guidance, or a real path/API before a rename or move. Save commit hashes and evidence.
- **Synthetic:** a researcher-authored obsolete fact modeled on a plausible historical change when usable historical guidance is unavailable. Label explicitly and analyze separately from history-derived cases.

Maintain a case record with task ID, repository and base/fix revisions, stale category, source/evidence, relevance rationale, accurate text, stale text, and a mechanical diff confirming only the targeted fact differs. Before locking the task set, apply a written relevance/plausibility rubric and mechanical checks (minimal-pair diff, path/API existence, and task-to-fact link). **No independent reviewer is assumed.** If a reviewer is available, record their role and independent assessment; otherwise the researcher applies the rubric and reports single-rater selection/coding as a limitation. Do not disclose condition labels or expected outcomes in prompts.

## Pilot and study size

### Feasibility pilot: 30 runs

Run **5 pilot tasks × 3 conditions × 2 repeats = 30 agent runs**. The pilot checks environment reliability, instruction discovery/loading, condition isolation, logging, run duration, and outcome-scoring procedure. It is not a hypothesis test and pilot tasks are excluded from the study set. Fix operational problems and freeze protocol/code before screening; if pilot information changes the design or measures, document a versioned amendment before screening starts.

### Confirmatory study: 300 runs (primary design)

Run **25 tasks × 3 conditions × 4 repeats = 300 agent runs**. Repeats use fresh resets and distinct recorded seeds where supported. This gives 100 runs per condition and repeated within-task observations, but does not guarantee power for small effects. Use the pilot’s task-level variability and observed completion rate to estimate detectable effect size and report that estimate with assumptions.

### Prespecified fallback: 135 runs

If the pilot shows that the primary design exceeds the recorded spending cap or cannot finish by the documented deadline, use **15 tasks × 3 conditions × 3 repeats = 135 runs**. Apply the same eligibility, no-guidance screening band, randomization, controls, outcomes, and analysis. Select the 15 before any confirmatory condition outcomes are collected, using the frozen candidate ranking and coverage rules; document why the fallback was triggered. Treat estimates as lower-precision and report the fallback as a prespecified confirmatory design with its limitations, not as an unplanned exploratory reduction. If fewer than 15 tasks qualify after the three-day search and screening, stop and revise the protocol before confirmatory runs.

## Agent, controls, and run procedure

Use one coding-agent CLI and one model for the confirmatory experiment. Record exact CLI version, model identifier/version, API/provider, sampling settings, system configuration, harness commit, task revision, container image digest, and timestamp for **every run**. Disable automatic upgrades where possible. If the provider changes the model mid-study, pause; preserve the completed block and resume only with a documented decision (preferably rerun the affected randomized block under one fixed version).

Interleave conditions in randomized blocks within each task/repeat so time, service load, or model drift cannot align with one condition. Save the randomization seed and schedule before execution. Give the agent the same issue statement, tool permissions, resource limits, timeout, and starting code in all conditions; vary only the study instruction file. Reset repository and external state between runs. Do not let the agent see reference patches or hidden tests.

Before each run, inventory all instruction sources the agent can load (for example `AGENTS.md`, tool-specific project instructions, and nested instruction files). Install the assigned study file at the documented location and verify through agent/harness logs that it was discovered and read. In the no-guidance condition, verify the study file is absent. Detect and record competing context files; apply a prespecified rule consistently (retain identical files across conditions or exclude the task). Preserve file hashes and the effective prompt/context trace where the tool permits. A run with uncertain condition delivery is invalidated and rerun under a documented rule, without inspecting its outcome first.

## Outcomes and analysis

### Predefined measures

- **Primary outcome:** binary task success, scored by applying the agent patch to a clean task base and running the benchmark’s prescribed tests, including hidden/reference tests where licensing and harness permit. Record test command, exit status, and logs. A test-infrastructure failure is marked invalid, not agent failure, under a written adjudication rule.
- **Secondary behavioral/effort outcomes:** number of tool calls; number of distinct files read and modified; elapsed wall-clock time; input/output tokens and estimated API cost when available; test commands and test outcomes; and whether the agent followed stale guidance (coded from trace using the rubric below).
- **Exploratory:** success and effort by stale category and by history-derived versus synthetic source.

**Stale-following rubric:** score each stale-condition run `1` if, before first inspecting, searching for, or editing the correct current path/symbol or otherwise acting on current implementation evidence, the agent opens, searches for, edits, or explicitly relies on the stale path/symbol/fact; score `0` if not; score `uncodable` if trace evidence is insufficient. Log the first relevant trace event and evidence snippet. This is a behavioral indicator, not proof that the stale text caused an action. The researcher applies the rubric; report single-rater coding as a limitation unless an independent coder is available and used. Freeze metric definitions, parsing rules, invalid-run rules, and analysis code before confirmatory outcomes are unblinded. Report missing telemetry rather than imputing it without a prespecified method.

### Statistical plan

The task is the independent sampling unit; repeated runs within a task are not independent observations. For H1, compute a success proportion for each task-condition across its repeats, then estimate paired condition differences (stale minus accurate as the primary contrast) with a **cluster bootstrap resampling tasks**, preserving each selected task’s condition/repeat bundle. Report effect sizes and 95% confidence intervals. Also report raw task-level and run-level counts.

As a prespecified robustness analysis, fit a mixed-effects logistic model to run-level success with condition as a fixed effect and task (and repository if estimable) as random intercepts; report convergence limitations. Do **not** use McNemar’s test on individual repeated runs. Analyze effort outcomes with task-clustered bootstrap intervals or suitable mixed-effects models, and label exploratory subgroup estimates as such. Correct for multiplicity only for any explicitly confirmatory secondary contrasts; H2/H3 otherwise remain exploratory.

## Pilot budget and full-study extrapolation

Log per-run wall time, setup/reset time, token use, and billed cost, separating one-time image/build cost from marginal run cost. Estimate full-study runtime and API cost from the pilot as:

```text
estimated full cost = one-time setup + planned run count × pilot median marginal cost per run
estimated full runtime = setup/build time + planned run count × pilot median end-to-end run time
```

Also report observed pilot range and a conservative estimate using the pilot 90th percentile per-run time/cost for both the 300-run primary design and 135-run fallback. Include screening runs (three per candidate), invalid/retried runs and storage needs in the final budget. Do not present pilot estimates as guarantees; recalibrate if the agent/model, price, task mix, or execution environment changes. Obtain/record a spending cap and deadline before launching confirmatory runs.

## Threats to validity

- **Training-data exposure:** the benchmark issues and fixes are public, so the model may have seen them during training. This can inflate success in all conditions and limits claims about novel private work. Report issue/fix publication dates where available; do not claim exposure is equal in effect across conditions as a certainty.
- **Git-history access:** choose and record one policy before the pilot. Recommended: provide the benchmark base checkout without Git history or remotes in every condition, while preserving the exact same files and metadata; history-derived stale cases must be constructed from separately archived evidence unavailable to the agent. If the agent can inspect history, disclose this and note it may allow discovery of the corrected fact.
- **Synthetic-case share:** report counts and proportions of history-derived and synthetic cases overall and by condition/task set. If most cases are synthetic, describe findings as effects of controlled stale guidance, not naturally occurring stale repository instructions.
- **Single-rater selection/coding:** if no independent reviewer/coder participates, report this and retain the rubric, audit trail, and uncodable counts.
- **Intermediate-difficulty selection:** no-guidance screening excludes very easy and very hard tasks, improving sensitivity to degradation but limiting generalization to those task types.

## Preregistration, version control, and reproducibility

Before the pilot, commit this protocol and the task-selection rubric. Before the confirmatory study, commit a frozen preregistration snapshot containing the final task IDs and revisions, eligibility/exclusion decisions, condition texts/hashes, randomization schedule or seed, model/CLI settings, outcome definitions, invalid-run rules, statistical plan, and analysis scripts. Tag the preregistration commit (for example, `prereg-v1`) and publish/archive its immutable commit hash in a time-stamped repository release or suitable public registry before confirmatory results are inspected. Keep changes after that point in separately identified commits; explain any deviations and dates in the report. Never rewrite the preregistration history.

Commit code, manifests, prompts, task metadata, analysis, and documentation. Do not commit credentials, private traces, restricted benchmark artifacts, or upstream code/data contrary to their terms. Provide reproducibility instructions and hashes/links instead where redistribution is not permitted. Preserve raw logs securely and publish redacted/redistributable materials with applicable notices.

## Suggested repository layout

```text
stale-repo-instructions-study/
├── README.md
├── PROTOCOL.md                         # this frozen protocol
├── LICENSE
├── CITATION.cff
├── preregistration/
│   ├── task-selection.md
│   ├── condition-construction.md
│   └── prereg-v1.yaml                  # committed and tagged before confirmatory runs
├── configs/
│   ├── pilot.yaml
│   └── confirmatory.yaml
├── manifests/
│   ├── candidates.csv
│   ├── pilot-tasks.csv
│   ├── confirmatory-tasks.csv
│   ├── conditions.jsonl                # text or hashes, subject to upstream terms
│   └── randomized-run-order.csv
├── src/
│   ├── runner/
│   ├── condition_checks/
│   └── scoring/
├── analysis/
│   ├── primary_analysis.py
│   └── exploratory_analysis.py
├── data/                               # manifests/metadata only; no prohibited assets
├── results/
│   ├── pilot/                           # gitignored raw traces, summary committed if safe
│   └── confirmatory/                    # gitignored raw traces, summary committed if safe
├── reports/
│   └── figures/
└── tests/
```

## Execution gates

1. **Before pilot:** verify data/environment and upstream licenses; identify 5 pilot tasks and a documented candidate pool; commit protocol, selection rubric, and harness plan.
2. **After pilot and before screening:** confirm all 30 runs are auditable, conditions load as intended, environments reset, and screening is feasible within the approved cap. Amend and recommit before screening if needed.
3. **Screening:** with the harness and agent configuration fixed, execute the first 3 no-guidance screening attempts, measure cost/runtime, set and record the candidate screening cap, then run the authorized screening batch. Record all attempts and stop at the cap.
4. **Before confirmation:** freeze up to 25 eligible tasks (or 15 if the prespecified fallback is triggered), screening records, preregistration, randomized schedule, model/CLI versions, metric/scoring code, spending cap, deadline, and analysis code; create the preregistration tag.
5. **After confirmation:** report all planned runs for the selected design (300 primary or 135 fallback), plus pilot and screening counts, invalidations/retries, deviations, null results, confidence intervals, and scope limits.

## Source and setup notes

Checked 2026-10-06: the [Multi-SWE-bench repository](https://github.com/multi-swe-bench/multi-swe-bench) states Apache-2.0, includes TypeScript and JavaScript, documents Docker setup and public dataset files; its separate [environment repository](https://github.com/multi-swe-bench/multi-swe-bench-env) states MIT. These facts do not establish that every task’s upstream repository or artifact permits redistribution, nor that a particular task environment will build successfully. Recheck licenses and setup for selected instances before using or publishing them.


## Amendment 1.1 (2026-10-07, before screening)

Made after the 30-run feasibility pilot and before any screening or confirmatory run.

1. **Agent and model fixed:** Claude Code 2.1.292 with claude-sonnet-5-5; the instruction file is CLAUDE.md. Full settings are in SETUP_NOTES.md.
2. **Scope narrowed to one staleness category:** stale file paths derived from real renames in repository history. In every case the stale path does not exist at the base commit.
3. **Relevance rule added:** a task is eligible only if the renamed file is the only source file changed by the reference fix (manifests/relevance.tsv). The pilot showed that otherwise the instruction file can be irrelevant to the task.
4. **Environment rule tightened:** the reference fix must pass in three of three independent validations, to exclude tasks with unreliable tests.
5. **Two analysis sets:** the pilot suggests tasks are often always solved or never solved. Effort and behaviour do not require intermediate difficulty, so:
   - the effort set is every eligible task, used for H2 and for stale-following;
   - the success set is the subset solved in 1 or 2 of 3 no-guidance screening runs, used for H1.
6. **H2 primary measure:** number of tool calls per run. Turns, wall time and estimated cost are secondary.
7. **Size:** all eligible tasks (expected about 24) x 3 conditions x 4 repeats. The 15-task fallback remains.
8. **Pilot record:** of five pilot tasks, one had an invalid environment and one fails the relevance rule; all five are excluded from screening and confirmation.
