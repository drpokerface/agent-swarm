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

import os, sys, json
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
- Prefer WIDTH over chains: make tasks independent wherever possible so different
  agents can run them in parallel; a dependency exists only when this task must READ
  that exact file.
- Every task's instructions carry the SHARED SPEC verbatim: the quality bar, the
  conventions, and the style decisions all tasks must obey to fit together -
  remember, each agent sees nothing but its own task.
- If success depends on human reception (engaging, beautiful, funny, persuasive),
  task 1 is RESEARCH: study several real, current exemplars of excellence in that
  exact medium and produce spec.md - the measurable properties of the winners plus a
  scoring rubric with anchored descriptors. Every later task depends on it via
  artifacts_needed and must satisfy it.
- Each task's instructions END by stating how the deliverable will be JUDGED - the
  concrete checks and, for subjective quality, the rubric and pass threshold - so the
  agent's own criteria match your intent instead of its guess.
- Order the list so dependencies always come before the tasks that need them.
- The FINAL task must depend on every earlier task and combine their outputs into ONE
  final deliverable that fulfills the whole goal by itself.

THE GOAL:
{goal}
"""

PLAN_SCHEMA = {"type": "OBJECT", "required": ["tasks"], "properties": {"tasks": {"type": "ARRAY", "items": {
    "type": "OBJECT", "required": ["title", "instructions", "produces", "depends_on"], "properties": {
        "title": {"type": "STRING"}, "instructions": {"type": "STRING"}, "produces": {"type": "STRING"},
        "depends_on": {"type": "ARRAY", "items": {"type": "INTEGER"}}}}}}}

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

if __name__ == "__main__":
    main()
