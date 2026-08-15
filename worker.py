# worker.py - the coordination loop: claim GitHub issues, run seed.py on them, publish and verify results.
#
# HOW IT FITS: seed.py stays exactly as it is - the "do one task well" engine.
# This file is the bulletin-board client wrapped around it. Forever, it:
#   1. syncs the repo (git pull)
#   2. VERIFIES someone else's finished work first, if any is waiting: re-runs their
#      verify.py in a fresh copy and a fresh process; a true green closes the issue
#   3. otherwise CLAIMS a task: an open issue AUTHORED BY THE REPO OWNER, unassigned,
#      with every depends_on issue already closed - claiming = assigning yourself
#   4. runs seed.py in a scratch folder OUTSIDE this clone, issue text as the goal
#   5. copies the finished workspace into artifacts/issue-N/, commits, pushes,
#      and comments a short RESULT manifest on the issue - and if the push itself
#      fails 3 times, comments PUBLISH-FAILED, drops the local commit, and frees
#      the task instead of pointing verifiers at artifacts that never landed
#      (publish failures count toward MAX_RETRIES just like failed verifications)
#
# AUTHORITY LIVES IN TOKENS, NOT IN THIS FILE: everyone runs identical code. GitHub
# checks server-side what each person's token may do, and the creator==OWNER filter
# below decides which issues workers will ever believe.
#
# v5: D4 workspace persistence (seed RESUMES across retries; FRESH_EVERY forces a clean
#     start), D5 resource-aware pause (quota/billing walls free the task without burning
#     a retry), D12 swarm-channel injection (agents may PROPOSE-TASK / QUESTION by
#     comment; the arbiter in `owner.py --watch` reviews them).
# v6: V6-3 consumer veto (an agent that proves its INPUT rotten posts INPUT-REJECT and
#     the producing issue is reopened with a consumer-authored VERIFY: FAIL) and
#     feedback injection (every retry sees the last verification failure in its goal).
#
# RUN:  copy .env.example to .env and fill it in, then:  python worker.py

import os, sys, re, time, shutil, stat, subprocess
from datetime import datetime, timezone
import requests

API = "https://api.github.com"
REPO = OWNER = ME = ""          # filled in main() from .env and the GitHub API

# ---------------------------------------------------------------- tiny helpers
def rmtree(path):
    # WINDOWS-RUN FIX: git marks object files read-only, so a plain shutil.rmtree
    # dies with PermissionError 13. Clear the bit and retry, per file.
    def _unlock(func, p, exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if os.path.exists(path):
        shutil.rmtree(path, onerror=_unlock)

def load_env():
    # same convenience as seed.py: read KEY=VALUE lines from .env if present
    if os.path.exists(".env"):
        for line in open(".env", encoding="utf-8"):
            if "=" in line and not line.strip().startswith("#"):
                os.environ.setdefault(line.split("=", 1)[0].strip(), line.split("=", 1)[1].strip())

def gh(method, path, **kwargs):
    # the one door to the GitHub API; fails loudly so nothing breaks silently
    r = requests.request(method, API + path, timeout=30,
        headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"], "Accept": "application/vnd.github+json"}, **kwargs)
    if r.status_code >= 300:
        raise Exception(method + " " + path + " -> " + str(r.status_code) + ": " + r.text[:200])
    return r.json() if r.text else {}

def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True)

def age_minutes(iso):
    # minutes since a GitHub timestamp like 2026-07-25T09:30:00Z
    then = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - then).total_seconds() / 60

def comment(n, text):
    gh("POST", "/repos/" + REPO + "/issues/" + str(n) + "/comments", json={"body": text})

def who_am_i():
    return os.environ.get("AGENT_ID", ME) + " (" + ME + ")"

def resource_pause(n, out, where):
    # v5/D5 RESOURCE-AWARE PAUSE: a quota / billing / spend-cap wall means the WORLD is
    # broken, not the work - free the task WITHOUT a retry-burning failure comment,
    # then sleep out the API's own delay so the swarm stops eating its next meal.
    low = out.lower()
    if not any(mark in low for mark in ("resource_exhausted", "quota exceeded", "rate limit", "billing", "spending cap")):
        return False
    if len([c for c in comments_of(n) if c["body"].startswith("RESOURCE-WAIT")]) >= int(os.environ.get("MAX_RESOURCE_WAITS", "6")):
        return False   # runaway guard: too many pauses on one issue - let normal retry accounting take over
    m = re.search(r"retry.{0,24}?(\d+)\s*(?:s\b|sec)", low)
    wait = min(int(m.group(1)) if m else int(os.environ.get("RESOURCE_SLEEP_SECONDS", "3600")), 14400)
    comment(n, "RESOURCE-WAIT from " + who_am_i() + " during " + where + " - quota or billing wall, not a work"
        " failure; task freed without burning a retry, worker sleeping " + str(wait) + "s.\n```\n" + out[-400:] + "\n```")
    fresh = gh("GET", "/repos/" + REPO + "/issues/" + str(n))
    if fresh["assignees"]:
        gh("DELETE", "/repos/" + REPO + "/issues/" + str(n) + "/assignees", json={"assignees": [a["login"] for a in fresh["assignees"]]})
    print("resource wall on issue #" + str(n) + " (" + where + ") - task freed, sleeping " + str(wait) + "s")
    time.sleep(wait)
    return True

# ------------------------------------------------- reading the bulletin board
def depends_on(body):
    # a "depends_on: [12, 13]" line in the issue body, or nothing
    m = re.search(r"depends_on:\s*\[([0-9,\s]*)\]", body or "")
    return [int(x) for x in m.group(1).split(",") if x.strip()] if m else []

def artifacts_needed(body):
    # an "artifacts_needed: [artifacts/issue-12/report.md]" line, or nothing
    m = re.search(r"artifacts_needed:\s*\[(.*?)\]", body or "", re.S)
    return [p.strip() for p in m.group(1).split(",") if p.strip()] if m else []

def open_owner_issues():
    # THE FILTER: only issues authored by the repo owner exist, as far as workers care
    issues = gh("GET", "/repos/" + REPO + "/issues", params={"state": "open", "creator": OWNER, "per_page": 100})
    return [it for it in issues if "pull_request" not in it]

def comments_of(n):
    return gh("GET", "/repos/" + REPO + "/issues/" + str(n) + "/comments", params={"per_page": 100})

def deps_closed(body):
    for n in depends_on(body):
        if gh("GET", "/repos/" + REPO + "/issues/" + str(n))["state"] != "closed":
            return False
    return True

def process_vetoes():
    # v6/V6-3 CONSUMER VETO: a consumer that proved its input rotten reopens the
    # producer - recorded as a VERIFY: FAIL, so the normal retry machinery (budget,
    # FRESH_EVERY, feedback injection) handles everything downstream of the reopen.
    for it in open_owner_issues():
        cs = comments_of(it["number"])
        handled = {c["body"].split()[1] for c in cs if c["body"].startswith("VETO-HANDLED ")}
        for c in cs:
            m = re.match(r"INPUT-REJECT:\s*#(\d+)\s+(\S[\s\S]*)", c["body"])
            if m is None or str(c["id"]) in handled:
                continue
            up, why = m.group(1), m.group(2)[:600]
            prior = any(k["body"].startswith("VERIFY: FAIL by consumer-veto from issue #" + str(it["number"])) for k in comments_of(int(up)))
            if not prior:   # one reopen max per consumer-producer pair - no ping-pong
                gh("PATCH", "/repos/" + REPO + "/issues/" + up, json={"state": "open"})
                comment(int(up), "VERIFY: FAIL by consumer-veto from issue #" + str(it["number"]) +
                        "\nits consumer rejected this artifact as unusable:\n" + why)
            comment(it["number"], "VETO-HANDLED " + str(c["id"]) +
                    ((" - reopened #" + up) if not prior else (" - #" + up + " already vetoed by this issue; not reopening twice")))
            print("consumer veto: issue #" + str(it["number"]) + " rejected #" + up)

# --------------------------------------------------------------- finding work
def find_verification():
    # someone's finished work waiting for an independent check
    for it in open_owner_issues():
        cs = comments_of(it["number"])
        results = [c for c in cs if c["body"].startswith("RESULT from")]
        if results == []:
            continue
        last = results[-1]
        if any(c["body"].startswith("VERIFY:") and c["created_at"] > last["created_at"] for c in cs):
            continue   # already judged
        if last["user"]["login"] == ME and os.environ.get("ALLOW_SELF_VERIFY") != "1":
            continue   # generator and checker never share a context - or a person
        return it
    return None

def find_task():
    for it in open_owner_issues():
        n = it["number"]
        if it["assignees"]:
            # OFFLINE RESILIENCE: a claim is a lease, not a lock - break stale ones
            if age_minutes(it["updated_at"]) > int(os.environ.get("LEASE_MINUTES", "90")):
                gh("DELETE", "/repos/" + REPO + "/issues/" + str(n) + "/assignees",
                   json={"assignees": [a["login"] for a in it["assignees"]]})
                print("broke a stale claim on issue #" + str(n))
            continue   # skip this round either way; it becomes claimable next loop
        cs = comments_of(n)
        results = [c for c in cs if c["body"].startswith("RESULT from")]
        if results != []:
            # RETRY RULE: a failed verification reopens the task for a fresh attempt
            last = results[-1]
            judged_fail = any(c["body"].startswith("VERIFY: FAIL") and c["created_at"] > last["created_at"] for c in cs)
            if not judged_fail:
                continue   # finished work, waiting on verification - not free to grab
        # RETRY BUDGET: failed verifications and failed publishes both burn it,
        # until MAX_RETRIES - then the task waits for the owner to look at it
        if len([c for c in cs if c["body"].startswith(("VERIFY: FAIL", "PUBLISH-FAILED"))]) >= int(os.environ.get("MAX_RETRIES", "2")):
            continue   # enough budget burned on this one - owner must intervene
        if not deps_closed(it.get("body")):
            continue
        return it
    return None

# --------------------------------------------------------------- doing a task
def claim(n):
    # THE RACE, handled honestly: assign, look again, back off if we are not alone
    gh("POST", "/repos/" + REPO + "/issues/" + str(n) + "/assignees", json={"assignees": [ME]})
    time.sleep(2)
    fresh = gh("GET", "/repos/" + REPO + "/issues/" + str(n))
    return [a["login"] for a in fresh["assignees"]] == [ME]

def do_task(it):
    n, body = it["number"], (it.get("body") or "").replace("\r", "")
    if not claim(n):
        print("lost the claim race on issue #" + str(n) + "; backing off")
        return
    print("claimed issue #" + str(n) + ": " + it["title"])
    # a fresh scratch folder OUTSIDE this clone, so seed's git never nests in ours
    work = os.path.abspath(os.path.join("..", "swarm-work", "issue-" + str(n)))
    # v5/D4 WORKSPACE PERSISTENCE: keep the workspace across retries of the same issue
    # so seed can RESUME (memory.md + git survive); every FRESH_EVERY-th failure starts
    # clean as an escape hatch from a poisoned state.
    cs = comments_of(n)
    fails = len([c for c in cs if c["body"].startswith(("VERIFY: FAIL", "PUBLISH-FAILED"))])
    if fails % int(os.environ.get("FRESH_EVERY", "4")) == 0:
        rmtree(work)
    os.makedirs(os.path.join(work, "workspace"), exist_ok=True)
    # hand over declared artifact dependencies into the seed's workspace
    for p in artifacts_needed(body):
        if os.path.exists(p):
            os.makedirs(os.path.dirname(os.path.join(work, "workspace", p)) or work, exist_ok=True)
            shutil.copy(p, os.path.join(work, "workspace", p))
    goal = it["title"] + "\n\n" + re.sub(r"^(depends_on|artifacts_needed):.*$", "", body, flags=re.M).strip()
    if artifacts_needed(body):
        goal += "\n\nAlready provided in your working directory: " + ", ".join(artifacts_needed(body))
    # v5/D12 SWARM CHANNEL: the one sanctioned way an agent talks upward - comments, never issues
    goal += ("\n\nSWARM CHANNEL: you are working issue #" + str(n) + " of the GitHub repo " + REPO +
        " (token in GITHUB_TOKEN env). If you discover work this plan is missing, you may post ONE comment on your own"
        " issue via the API starting exactly 'PROPOSE-TASK: ' (state: title, why, which existing deliverable it"
        " unblocks, what it produces). Facing an irreversible, genuinely ambiguous choice, you may post ONE comment"
        " starting exactly 'QUESTION: ', then continue on the reversible path without waiting. If a PROVIDED input"
        " artifact fails your validation (placeholder, degenerate, or broken contract), post ONE comment starting"
        " exactly 'INPUT-REJECT: #<producing issue number> ' plus one line of evidence - the swarm will reopen that"
        " task; then declare impossible honestly instead of building on garbage. Never create issues yourself; an"
        " owner-side arbiter reviews and answers as an 'ARBITER re' comment on this issue.")
    # v6/V6-3 FEEDBACK INJECTION: a retry must know why the last attempt failed
    lastfail = [c for c in cs if c["body"].startswith("VERIFY: FAIL")]
    if lastfail != []:
        goal += "\n\nLAST VERIFICATION FAILURE (repair this first):\n" + lastfail[-1]["body"][:1200]
    try:
        r = subprocess.run([sys.executable, os.path.abspath("seed.py"), goal], cwd=work,
            capture_output=True, text=True, timeout=int(os.environ.get("SEED_TIMEOUT_SECONDS", "3600")))
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        out = "seed.py was killed at the " + os.environ.get("SEED_TIMEOUT_SECONDS", "3600") + " second timeout"
    if "DONE - " not in out and resource_pause(n, out, "the seed run"):
        return   # v5/D5: starved, not failed - no RESULT, no retry burned
    if "DONE - " in out:
        status = "gate: PASSED locally"
    elif "declared the goal impossible" in out:
        status = "gate: agent declared IMPOSSIBLE"
    else:
        status = "gate: NOT passed (ran out of turns, budget, or rejections)"
    publish(n, work, out, status)

def publish(n, work, out, status):
    # artifacts ride in the repo (the API cannot attach files to comments); the
    # comment is just a short manifest pointing at them
    dest = os.path.join("artifacts", "issue-" + str(n))
    src = os.path.join(work, "workspace")
    rmtree(dest)
    if os.path.exists(src):
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".git", "scratch"))
    pushed = False
    for attempt in range(3):   # a push can lose a race too - pull, retry
        git("pull", "--rebase")
        git("add", "artifacts")
        git("commit", "-m", "artifacts for issue #" + str(n) + " from " + os.environ.get("AGENT_ID", ME))
        if git("push").returncode == 0:
            pushed = True
            break
    if not pushed:
        # HONESTY: a RESULT pointing at artifacts that never landed would burn a
        # verification retry on a lie. Say what happened, drop the local commit
        # (an oversized file in it would sink every later push too), free the task.
        git("reset", "--hard", "@{u}")
        comment(n, "PUBLISH-FAILED from " + who_am_i() + "\nthe artifact push failed 3 times "
            "(oversized file? repo limit? network?) - local commit dropped, task freed for a retry."
            "\n\n--- seed output tail ---\n```\n" + out[-800:] + "\n```")
        gh("DELETE", "/repos/" + REPO + "/issues/" + str(n) + "/assignees", json={"assignees": [ME]})
        print("publish FAILED for issue #" + str(n) + " - local commit dropped, task unassigned")
        return
    comment(n, "RESULT from " + who_am_i() + "\n" + status +
        "\nartifacts: artifacts/issue-" + str(n) + "/\n\n--- output tail ---\n```\n" + out[-1200:] + "\n```")
    print("published result for issue #" + str(n) + " - " + status)

# ---------------------------------------------------------- verifying a task
def do_verify(it):
    # GENERATOR AND CHECKER NEVER SHARE A CONTEXT: fresh copy, fresh process, fresh eyes
    n = it["number"]
    print("verifying issue #" + str(n))
    src = os.path.join("artifacts", "issue-" + str(n))
    if os.path.exists(os.path.join(src, "verify.py")):
        spot = os.path.abspath(os.path.join("..", "swarm-verify", "issue-" + str(n)))
        rmtree(spot)
        shutil.copytree(src, spot)
        vt = int(os.environ.get("VERIFY_TIMEOUT_SECONDS", "300"))   # v3: same knob the gate uses
        try:
            r = subprocess.run([sys.executable, "verify.py"], cwd=spot, capture_output=True, text=True, timeout=vt)
            out, code = r.stdout + r.stderr, r.returncode
        except subprocess.TimeoutExpired:
            out, code = "verify.py timed out after " + str(vt) + " seconds", 1
    else:
        out, code = "no verify.py found in " + src, 1
    good = code == 0 and "FAULT-PROOF:" in out and "VERDICT: PASS" in out
    if not good and resource_pause(n, out, "verification"):
        return   # v5/D5: the verifier hit a quota wall (e.g. its perception call) - retry later, burn nothing
    comment(n, ("VERIFY: PASS by " if good else "VERIFY: FAIL by ") + who_am_i() +
        "\n\n--- verify.py output tail ---\n```\n" + out[-1200:] + "\n```")
    if good:
        gh("PATCH", "/repos/" + REPO + "/issues/" + str(n), json={"state": "closed"})
        print("issue #" + str(n) + " verified and closed")
    else:
        # free the task so it can be retried fresh (find_task caps how many times)
        fresh = gh("GET", "/repos/" + REPO + "/issues/" + str(n))
        if fresh["assignees"]:
            gh("DELETE", "/repos/" + REPO + "/issues/" + str(n) + "/assignees",
               json={"assignees": [a["login"] for a in fresh["assignees"]]})
        print("issue #" + str(n) + " failed verification - unassigned for a retry")

# --------------------------------------------------------------- the main loop
def main():
    global REPO, OWNER, ME
    load_env()
    REPO = os.environ["REPO"]
    OWNER = REPO.split("/")[0]
    ME = gh("GET", "/user")["login"]
    # make git pushes just work: point origin at the repo using this worker's token
    git("remote", "set-url", "origin", "https://x-access-token:" + os.environ["GITHUB_TOKEN"] + "@github.com/" + REPO + ".git")
    print("worker up: " + who_am_i() + " on " + REPO + " - ctrl-c to stop")
    while True:
        try:
            git("pull", "--rebase")
            process_vetoes()   # v6/V6-3: consumer vetoes reopen rotten producers first
            waiting = find_verification()
            if waiting is not None:
                do_verify(waiting)
                continue
            task = find_task()
            if task is not None:
                do_task(task)
                continue
            print("nothing to do; sleeping")
        except Exception as error:
            print("worker error (will retry): " + repr(error))
        time.sleep(int(os.environ.get("POLL_SECONDS", "60")))

if __name__ == "__main__":
    main()
