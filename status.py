# status.py - read-only dashboard: one line per task, then totals. Safe to run anytime.
#
# States: done | awaiting verification | in progress | blocked | retrying |
#         needs owner (too many failures - verify or publish) | open
#
# RUN:  python status.py

import os, re
import requests

API = "https://api.github.com"

# ---------------------------------------------------------------- tiny helpers
def load_env():
    if os.path.exists(".env"):
        for line in open(".env", encoding="utf-8"):
            if "=" in line and not line.strip().startswith("#"):
                os.environ.setdefault(line.split("=", 1)[0].strip(), line.split("=", 1)[1].strip())

def gh(path, params):
    r = requests.get(API + path, params=params, timeout=30,
        headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"], "Accept": "application/vnd.github+json"})
    if r.status_code >= 300:
        raise Exception("GET " + path + " -> " + str(r.status_code) + ": " + r.text[:200])
    return r.json()

def depends_on(body):
    m = re.search(r"depends_on:\s*\[([0-9,\s]*)\]", body or "")
    return [int(x) for x in m.group(1).split(",") if x.strip()] if m else []

# ------------------------------------------------------------- classification
def classify(it, open_numbers, repo):
    if it["state"] == "closed":
        return "done", ""
    cs = gh("/repos/" + repo + "/issues/" + str(it["number"]) + "/comments", {"per_page": 100})
    results = [c for c in cs if c["body"].startswith("RESULT from")]
    fails = [c for c in cs if c["body"].startswith(("VERIFY: FAIL", "PUBLISH-FAILED"))]
    if results != []:
        last = results[-1]
        if not any(c["body"].startswith("VERIFY: FAIL") and c["created_at"] > last["created_at"] for c in cs):
            return "awaiting verification", "result by " + last["user"]["login"]
    if len(fails) >= int(os.environ.get("MAX_RETRIES", "2")):
        return "needs owner", "failed x" + str(len(fails))
    if it["assignees"]:
        return "in progress", ", ".join(a["login"] for a in it["assignees"])
    blocked = [d for d in depends_on(it.get("body")) if d in open_numbers]
    if blocked != []:
        return "blocked", "waiting on #" + ", #".join(str(b) for b in blocked)
    if fails != []:
        return "retrying", "failed x" + str(len(fails))
    return "open", ""

# ------------------------------------------------------------------ the table
def main():
    load_env()
    repo, owner = os.environ["REPO"], os.environ["REPO"].split("/")[0]
    issues = [it for it in gh("/repos/" + repo + "/issues", {"state": "all", "creator": owner, "per_page": 100})
              if "pull_request" not in it]
    issues.sort(key=lambda it: it["number"])
    if issues == []:
        print("no tasks yet - run owner.py to create some")
        return
    open_numbers = {it["number"] for it in issues if it["state"] == "open"}
    counts = {}
    print("")
    for it in issues:
        state, detail = classify(it, open_numbers, repo)
        counts[state] = counts.get(state, 0) + 1
        extra = ("  [" + detail + "]") if detail != "" else ""
        print("  #" + str(it["number"]).ljust(4) + state.upper().ljust(24) + it["title"][:55] + extra)
    print("\n  " + " | ".join(k + ": " + str(v) for k, v in sorted(counts.items())) + "\n")

if __name__ == "__main__":
    main()
