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

## Agent configuration (recorded 2026-10-07)

- Agent: Claude Code 2.1.292 (commit 37832d0b7cad), native linux-x64 binary mounted read-only into each task container; auto-updates disabled.
- Model: claude-sonnet-5-5 (full ID passed, not the alias).
- Auth: long-lived token from claude setup-token, passed as CLAUDE_CODE_OAUTH_TOKEN (never committed).
- Flags: -p, --strict-mcp-config, --disallowedTools "mcp__*,WebSearch,WebFetch", --tools and --allowedTools "Bash,Read,Edit,Write,Glob,Grep", --permission-mode acceptEdits, --no-session-persistence, --max-turns 150, --output-format stream-json --verbose.
- Never use --bare: it skips CLAUDE.md, which is the manipulated variable.
- Container preparation: delete /home/fix.patch, /home/test.patch and helper scripts; install CLAUDE.md if the condition has one; replace .git with a single fresh commit.
- Delivery check: canary instruction in CLAUDE.md was followed (final message ended with the canary phrase) under these exact flags.
- Smoke test on vuejs/core PR 11813, no guidance: resolved in 33 s, 8 turns, estimated cost about $0.09.
- Network rule: any run whose trace shows the agent fetching from the network is invalid.
