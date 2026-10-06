# Setup notes

Recorded 2026-10-06 while reproducing one Multi-SWE-bench task (vuejs/core PR 11813).

| Item | Finding |
|---|---|
| Platform | Windows with WSL2 Ubuntu; project kept in the Linux home folder |
| Python | 3.12 works; 3.14 fails with a type-annotation error in the harness |
| Docker | Works from Ubuntu without sudo; images run natively (amd64) |
| Dataset | Multi-SWE-bench mini: 50 TypeScript and 50 JavaScript tasks across 7 repositories |
| One-time image build (Vue) | About 5 minutes 20 seconds |
| Test run per evaluation (Vue) | About 1 to 2 minutes |
| Result caching | The harness reuses results per working folder; every run needs a fresh workdir |

## Checks completed

- Reference fix scored as resolved.
- Do-nothing patch scored as unresolved (with a fresh workdir).

## Gotchas

- Clone on a case-sensitive file system; the Windows drive causes path collisions.
- Create the Python 3.12 environment with: uv venv --python 3.12 --seed .venv
- Avoid "!" inside double-quoted bash strings; it triggers history expansion.
