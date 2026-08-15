# owner.py - OWNER ONLY: turn one big goal into GitHub issues that workers will trust.
#
# There is no secret code here - anyone could copy this file. The authority is your
# GITHUB_TOKEN: issues it creates are authored by the repo OWNER's account, and
# worker.py only ever believes issues authored by the owner. A malicious person
# running this exact file would just create issues from THEIR account - which every
# worker ignores. Identity lives in tokens; enforcement lives on GitHub's servers.
#
# WHAT IT DOES: sends your goal to the smart model, gets back 3-7 subtasks with
# dependencies, shows you the plan, and creates the issues only after you type yes -
# you are the approval gate between the model's plan and the swarm.
#
# RUN:  python owner.py "spread appreciation for great teachers on Teachers' Day"
#       python owner.py --watch "<the same goal>"    (v5/D12: the runtime ARBITER -
#       reviews PROPOSE-TASK / QUESTION comments from workers, creates only what
#       earns its place, and answers questions; run it beside worker.py)

import os, sys, json, time
import requests
from google import genai

API = "https://api.github.com"
SMART_MODEL = "gemini-3.1-pro-preview"   # same smart model seed.py uses

PLAN_PROMPT = """
You are decomposing a goal into tasks for a swarm of autonomous coding agents.
Each task will be handed, alone and without any other context, to one agent that can
write and run Python, use the internet, generate and perceive media through its model
API, and must end with a concrete, checkable deliverable.

Rules:
- 3 to 7 tasks, each small enough for one agent session.
- Every task's instructions must be fully self-contained (the agent sees nothing else)
  and describe a deliverable that code could verify (a file with specific contents).
- Each task names ONE main output file in "produces" (e.g. plan.md, poster.html).
- "depends_on" lists the numbers of earlier tasks whose output files this task needs -
  only real needs, and only tasks that appear EARLIER in your list.
- Tasks are numbered 1..N: the FIRST task in your list is 1. depends_on uses these
  1-based numbers - never 0.
- Prefer WIDTH over chains: make tasks independent wherever possible so different
  agents can run them in parallel; a dependency exists only when this task must READ
  that exact file.
- Every task's instructions carry the SHARED SPEC verbatim: the quality bar, the
  conventions, and the style decisions all tasks must obey to fit together -
  remember, each agent sees nothing but its own task.
- Task 1 is ALWAYS the GOAL CONSTITUTION, producing constitution.md: a goal-specialized
  philosophy for THIS goal (strategy, style decisions, conventions, quality bar) plus
  the scoring rubric every judged deliverable will face - anchored descriptors of what
  a 4, a 7, and a 9 concretely look like, with a numeric pass threshold per
  deliverable. If success depends on human reception (engaging, beautiful, funny,
  persuasive), those anchors are distilled from several real, current exemplars of
  excellence in that exact medium, studied first - never from imagination. Every later
  task depends on task 1 via artifacts_needed and must obey its constitution.
- If the goal produces a composite or perceptual artifact (video, app, site, or any
  deliverable assembled from parts), the task AFTER the constitution is a TRACER SLICE: one
  task that first PROBES for the strongest generation tools and models the API key
  can actually reach (images, speech, video - primitive fallbacks like hand-drawn
  shapes are forbidden unless the probe proves no better tier is reachable) and
  records the findings in capabilities.md, then builds a TINY but COMPLETE end-to-end
  version of the final deliverable (for a video: ~10 seconds, one scene, one voiced
  line, one cut, assembled exactly the way the final task will assemble) and judges
  it against the exemplars. Its artifacts - the slice, capabilities.md, and any
  tools - define the file naming, formats, quality floor, and assembly method for
  the whole board: every later task depends on the slice via artifacts_needed and
  must match or beat what it established.
- HARDEST FIRST: identify the plan's riskiest assumption - the one most likely to sink
  the goal - and order tasks so the cheapest possible probe of that assumption runs as
  early as possible; state the assumption explicitly in the task that tests it.
- INTEGRATION CONTRACTS: every task whose output another task consumes must ALSO ship
  manifest.md next to its deliverable - exact filenames, formats, and one tiny sample
  proving the format - and every task that consumes another task's artifacts must OPEN
  and VALIDATE them against that manifest FIRST, before building anything on them; a
  consumer that builds on unvalidated inputs has failed its own task, and a consumer
  that finds a rotten or placeholder input must INPUT-REJECT it through its swarm
  channel rather than build on it or regenerate someone else's artifact.
- Each task's instructions END by stating how the deliverable will be JUDGED, in two
  lanes: mechanical facts (exists, decodes, counts, durations) as binary checks;
  subjective or perceptual quality as a 0-10 score against the constitution's anchored
  rubric with the numeric pass threshold stated RIGHT HERE in the task. State also that
  verify.py must consume the deliverable the way its audience will - decode and sample
  its ACTUAL content, failing degenerate output (blank, silent, empty, uniform,
  truncated) regardless of metadata - and for perceptual deliverables must include one
  cheap model-perception call confirming the sampled content actually depicts what the
  task requires. Placeholder or stub content anywhere in the deliverable is an
  automatic FAIL at any threshold - state that too.
- Order the list so dependencies always come before the tasks that need them.
- The FINAL task must depend on every earlier task and combine their outputs into ONE
  final deliverable that fulfills the whole goal by itself.
  Its instructions must direct the agent to assemble a complete ROUGH version of the
  deliverable early, then spend all remaining budget in judge-guided improvement
  passes on the whole artifact.

THE GOAL:
{goal}
"""

PLAN_SCHEMA = {"type": "OBJECT", "required": ["tasks"], "properties": {"tasks": {"type": "ARRAY", "items": {
    "type": "OBJECT", "required": ["title", "instructions", "produces", "depends_on"], "properties": {
        "title": {"type": "STRING"}, "instructions": {"type": "STRING"}, "produces": {"type": "STRING"},
        "depends_on": {"type": "ARRAY", "items": {"type": "INTEGER"}}}}}}}

# v5/D12 - the runtime arbiter: workers PROPOSE, the owner's token DISPOSES.
ARBITER_PROMPT = """
You are the owner-side ARBITER of a swarm task board. Workers may post PROPOSE-TASK
comments (work they believe the plan is missing) or QUESTION comments (one irreversible,
genuinely ambiguous choice). You decide, guarding the owner's goal and budget: a proposal
is accepted ONLY if it clearly unblocks or improves a named existing deliverable and is
not already covered by any task on the board.

THE GOAL:
{goal}

THE BOARD (number | state | title | body head):
{board}

SPAWN BUDGET: {spawned} of {cap} runtime tasks already created.

THE COMMENT under review (posted on issue #{n}):
{comment}

For a QUESTION: decision="answer"; put a short, decisive answer in reply (title and body
stay empty).
For a PROPOSE-TASK: decision="create" only if it earns its place and budget remains,
else decision="reject" with the honest reason in reply. When creating, write the title
and a FULLY self-contained body in the board's conventions: first lines
"depends_on: [real issue numbers]" and "artifacts_needed: [artifacts/issue-N/<file>]"
(only files that really exist on the board), then complete instructions for an agent
that sees nothing else, ENDING with how the deliverable will be JUDGED (native-medium
verification, degenerate-output rejection, and - for subjective quality - a 0-10 score
against the board's constitution with a numeric threshold) and the line
"Save the main deliverable as <file>."
"""

ARBITER_SCHEMA = {"type": "OBJECT", "required": ["decision", "title", "body", "reply"], "properties": {
    "decision": {"type": "STRING", "enum": ["create", "reject", "answer"]}, "title": {"type": "STRING"},
    "body": {"type": "STRING"}, "reply": {"type": "STRING"}}}

# ---------------------------------------------------------------- tiny helpers
def load_env():
    # same convenience as seed.py: read KEY=VALUE lines from .env if present
    if os.path.exists(".env"):
        for line in open(".env", encoding="utf-8"):
            if "=" in line and not line.strip().startswith("#"):
                os.environ.setdefault(line.split("=", 1)[0].strip(), line.split("=", 1)[1].strip())

def gh(method, path, **kwargs):
    r = requests.request(method, API + path, timeout=30,
        headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"], "Accept": "application/vnd.github+json"}, **kwargs)
    if r.status_code >= 300:
        raise Exception(method + " " + path + " -> " + str(r.status_code) + ": " + r.text[:200])
    return r.json() if r.text else {}

def comment_on(repo, n, text):
    gh("POST", "/repos/" + repo + "/issues/" + str(n) + "/comments", json={"body": text})

# ------------------------------------------------------------------- the flow
def main():
    load_env()
    repo, owner = os.environ["REPO"], os.environ["REPO"].split("/")[0]
    me = gh("GET", "/user")["login"]
    if me != owner:
        print("WARNING: your token belongs to " + me + " but the repo owner is " + owner + ".")
        print("Workers only trust issues authored by the owner, so these issues would be ignored.")
    goal = " ".join(sys.argv[1:]).strip() or input("What is the big goal? ")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    print("asking the smart model for a task breakdown...")
    reply = client.models.generate_content(model=SMART_MODEL, contents=PLAN_PROMPT.replace("{goal}", goal),
        config={"response_mime_type": "application/json", "response_schema": PLAN_SCHEMA})
    tasks = json.loads(reply.text)["tasks"]
    # WINDOWS-RUN FIX: some plans number dependencies 0-based; the issue map below
    # is 1-based. If any dep is 0, the whole plan is 0-based - shift it by +1.
    if any(0 in t["depends_on"] for t in tasks):
        for t in tasks:
            t["depends_on"] = [d + 1 for d in t["depends_on"]]

    # show the whole plan BEFORE touching GitHub - you are the approval step
    for i, t in enumerate(tasks, 1):
        deps = ", ".join(str(d) for d in t["depends_on"]) or "none"
        print("\n[" + str(i) + "] " + t["title"] + "   (needs: " + deps + " | produces: " + t["produces"] + ")")
        print("    " + t["instructions"][:300].replace("\n", "\n    "))
    if input("\nCreate these " + str(len(tasks)) + " issues on " + repo + "? (yes/no) ").strip().lower() not in ("y", "yes"):
        print("cancelled - nothing was created")
        return

    real = {}   # plan number -> real GitHub issue number
    for i, t in enumerate(tasks, 1):
        bad = [d for d in t["depends_on"] if d not in real]
        if bad != []:
            print("skipping [" + str(i) + "] - it depends on " + str(bad) + ", which were not created earlier")
            continue
        needed = ["artifacts/issue-" + str(real[d]) + "/" + tasks[d - 1]["produces"] for d in t["depends_on"]]
        body = ("depends_on: [" + ", ".join(str(real[d]) for d in t["depends_on"]) + "]\n"
                + "artifacts_needed: [" + ", ".join(needed) + "]\n\n"
                + t["instructions"].strip()
                + "\n\nSave the main deliverable as " + t["produces"] + ".")
        made = gh("POST", "/repos/" + repo + "/issues", json={"title": t["title"], "body": body})
        real[i] = made["number"]
        print("created issue #" + str(made["number"]) + ": " + t["title"])
    print("\ndone - workers will now pick these up in dependency order")

# ------------------------------------------------------- v5/D12: the arbiter
def arbiter(goal):
    # Guardrails, enforced here in code: a hard spawn cap; depth limit 1 (a task the
    # arbiter created may not propose more); the final task is reopened when a new
    # runtime task must still be integrated. All real issues stay OWNER-authored.
    load_env()
    repo, owner = os.environ["REPO"], os.environ["REPO"].split("/")[0]
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    cap = int(os.environ.get("ARBITER_MAX_SPAWNS", "3"))
    goal = goal or "(no goal text given - infer the goal from the board below)"
    print("arbiter up on " + repo + " - reviewing PROPOSE-TASK / QUESTION comments; ctrl-c to stop")
    while True:
        try:
            issues = [it for it in gh("GET", "/repos/" + repo + "/issues", params={"state": "all", "creator": owner, "per_page": 100}) if "pull_request" not in it]
            spawned = [it for it in issues if "spawned-by: arbiter" in (it.get("body") or "")]
            final = max((it["number"] for it in issues if "spawned-by: arbiter" not in (it.get("body") or "")), default=0)
            board = "\n".join(str(it["number"]) + " | " + it["state"] + " | " + it["title"] + " | " + (it.get("body") or "").replace("\n", " ")[:200] for it in sorted(issues, key=lambda x: x["number"]))
            for it in issues:
                cs = gh("GET", "/repos/" + repo + "/issues/" + str(it["number"]) + "/comments", params={"per_page": 100})
                answered = {c["body"].split()[2].rstrip(":") for c in cs if c["body"].startswith("ARBITER re ")}
                for c in cs:
                    if not c["body"].startswith(("PROPOSE-TASK:", "QUESTION:")) or str(c["id"]) in answered:
                        continue
                    if c["body"].startswith("PROPOSE-TASK:") and "spawned-by: arbiter" in (it.get("body") or ""):
                        verdict = {"decision": "reject", "title": "", "body": "", "reply": "depth limit: a task created at runtime may not propose further tasks"}
                    elif c["body"].startswith("PROPOSE-TASK:") and len(spawned) >= cap:
                        verdict = {"decision": "reject", "title": "", "body": "", "reply": "spawn budget exhausted (" + str(cap) + " runtime tasks already created)"}
                    else:
                        prompt = (ARBITER_PROMPT.replace("{goal}", goal).replace("{board}", board).replace("{spawned}", str(len(spawned)))
                                  .replace("{cap}", str(cap)).replace("{n}", str(it["number"])).replace("{comment}", c["body"][:3000]))
                        reply = client.models.generate_content(model=SMART_MODEL, contents=prompt,
                            config={"response_mime_type": "application/json", "response_schema": ARBITER_SCHEMA})
                        verdict = json.loads(reply.text)
                    if verdict["decision"] == "create":
                        made = gh("POST", "/repos/" + repo + "/issues", json={"title": verdict["title"],
                            "body": "spawned-by: arbiter (proposed in #" + str(it["number"]) + ")\n" + verdict["body"]})
                        spawned.append(made)
                        outcome = "created issue #" + str(made["number"])
                        if final and gh("GET", "/repos/" + repo + "/issues/" + str(final))["state"] == "closed":
                            gh("PATCH", "/repos/" + repo + "/issues/" + str(final), json={"state": "open"})
                            comment_on(repo, final, "ARBITER reopened this final task: runtime task #" + str(made["number"]) + " must be integrated before the goal is complete.")
                            outcome += "; reopened final task #" + str(final)
                    else:
                        outcome = verdict["reply"][:400]
                    comment_on(repo, it["number"], "ARBITER re " + str(c["id"]) + ": " + verdict["decision"].upper() + " - " + outcome)
                    print("arbiter: issue #" + str(it["number"]) + " comment " + str(c["id"]) + " -> " + verdict["decision"])
        except Exception as error:
            print("arbiter error (will retry): " + repr(error))
        time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        arbiter(" ".join(sys.argv[2:]).strip())
    else:
        main()
