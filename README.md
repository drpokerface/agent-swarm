# agent-swarm

A small distributed agent system (school project). One GitHub repo is the whole
coordination layer: **tasks are Issues** authored by the repo owner, **results are
commits** under `artifacts/` plus a `RESULT` comment, and **verification** is a
*different* agent re-running the task's `verify.py` fresh before the issue is closed.

`seed.py` is the single-task engine and is used completely unchanged. `worker.py` is
the loop around it. Everyone runs identical code — authority lives in GitHub tokens
and permissions, not in the files.

## Files

- `seed.py` — the single-task agent (untouched)
- `worker.py` — claims issues, runs seed.py, publishes artifacts, verifies others' work
- `owner.py` — **owner only**: decomposes a big goal into issues (with `depends_on` /
  `artifacts_needed` filled in), shows you the plan, creates issues after you approve
- `status.py` — read-only dashboard: one line per task with its current state
- `.env.example` — copy to `.env` and fill in your own values
- `requirements.txt`, `.gitignore`

## Owner setup (you, once)

1. Create a **private** GitHub repo (e.g. `agent-swarm`) and push this folder to it.
2. Make a token: GitHub → Settings → Developer settings → Fine-grained personal access
   tokens → only this repo → Read/Write on **Issues** and **Contents**.
3. `cp .env.example .env` and fill it in (your Gemini key, your token, the repo,
   a unique `AGENT_ID`).
4. `pip install -r requirements.txt`
5. Create a couple of issues (format below), then run: `python worker.py`

## Decomposing a big goal (owner only)

```
python owner.py "spread appreciation for great teachers on Teachers' Day"
```

The smart model proposes 3–7 subtasks with dependencies; you review the plan and type
`yes`; only then are the issues created — in the right order, with the metadata lines
written for you. The planner now prefers parallel tasks over chains, injects a shared
spec into every issue so context-isolated agents stay consistent with each other, and —
when the goal is judged by humans — opens with a research task whose `spec.md`
(measured properties of real exemplars + an anchored rubric) flows to every task
downstream via `artifacts_needed`. The file itself isn't secret: anyone could run it, but issues from a
non-owner account are simply ignored by every worker.

## Task format (the issue body)

```
depends_on: [2, 3]
artifacts_needed: [artifacts/issue-2/report.md]

Write a friendly one-page beginner's guide to daily stretching, saved as guide.md.
```

Both metadata lines are optional. Workers only claim an issue when **all** of these hold:

- it was **authored by the repo owner** (anything else is ignored — this is the trust rule)
- every issue in `depends_on` is closed
- nobody is assigned (a claim that has been silent longer than `LEASE_MINUTES` is
  broken automatically — that's the offline-resilience lease)
- it has no `RESULT` comment yet

## Lifecycle of one task

open → assigned (the claim) → `RESULT` comment + artifacts pushed to
`artifacts/issue-N/` → `VERIFY: PASS` comment by a **different** agent → closed.

If verification fails, the worker unassigns the task so it is automatically retried
fresh by anyone — until it has failed `MAX_RETRIES` times (default 2), after which it
waits for the owner to look at it. If the artifact *push* itself fails 3 times
(oversized file, repo limit, network), the worker comments `PUBLISH-FAILED`, drops its
local commit so a poison file can't sink later pushes, and frees the task — publish
failures burn the same `MAX_RETRIES` budget as failed verifications. `python
status.py` shows where everything stands.

## Test it solo tonight

Set `ALLOW_SELF_VERIFY=1` in your `.env` (so one machine can play both roles),
create two tiny issues, run `python worker.py`, and watch the issues get claimed,
commented, and closed in your browser.

## A friend joins

1. You invite them as a **collaborator** on the private repo.
2. They clone it, `pip install -r requirements.txt`.
3. They write their **own** `.env`: their Gemini key, their GitHub token, a unique
   `AGENT_ID`.
4. `python worker.py` — same file, zero edits. Their token is their identity.

## Quality laws (v3)

For goals judged by humans — engaging, beautiful, funny, persuasive — the philosophy
now demands more than a green exit code. **Perception:** any artifact aimed at human
senses is invisible to the agent until a fresh model call has looked at the artifact
itself; the same API is also its eyes (and, where supported, a media generator).
**The outside anchor:** rubrics are distilled from 3–5 real exemplars pulled from the
internet, never invented from the model's priors. **Judging:** the rubric exists
before the artifact, the judge is a blind fresh call, scores are a median of 3 with a
margin above threshold, and quality is found by selection among 3+ genuinely
different variants. **Portability:** `verify.py` re-runs on a stranger's machine, so
it must bootstrap its own dependencies, use relative paths, and keep shipped
artifacts lean (bulky intermediates stay in `scratch/`). The hostile auditor rejects
violations of all four. Perceptual verification can be slower than pure code checks,
so the verify timeout is now a knob (`VERIFY_TIMEOUT_SECONDS`, default 300).

## Safety, honesty, cost — read this

- **This system executes AI-generated Python on your machine.** Anyone who joins must
  know that and agree. Run workers in a spare folder, spare account, or VM.
- **Every seed run spends real Gemini API tokens** (seed.py caps each run's budget,
  but many issues = many runs). Everyone pays for their own key.
- **Media calls are extra money.** Perception and generation calls agents make inside
  their own code are *not* metered by seed.py's token budget — the philosophy makes
  agents tally them in notes.md, but the bill still lands on each person's key.
- **Never commit `.env`** (it's git-ignored). Note: worker.py writes your token into
  the local git remote URL so pushes work — one more reason the repo stays private.
- **Kill switch:** close all open issues (workers go idle) or Ctrl-C each worker.
- **Design honesty for your writeup:** this is a *permissioned coordinator* design —
  the owner authors all tasks and GitHub is the shared log. That's a deliberate,
  safer trade-off, not full decentralization; leases and the claim-race backoff are
  kept intentionally simple.
