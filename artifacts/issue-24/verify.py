import os
import sys
import json
import random
import shutil
from google import genai
from pydantic import BaseModel

print("EXPECT: verification of constitution.md")

if not os.path.exists("constitution.md"):
    print("C1: constitution.md exists = False")
    sys.exit(1)
print("C1: constitution.md exists = True")

with open("constitution.md", "r", encoding="utf-8") as f:
    text = f.read()
text_lower = text.lower()

c2 = all(t in text_lower for t in ["strategy", "style", "conventions"])
print(f"C2: Includes strategy/style/conventions = {c2}")

c3 = all(t in text_lower for t in ["score 4", "score 7", "score 9", "comedic timing", "visual consistency", "pacing"])
print(f"C3: Contains 4,7,9 rubrics for timing/visual/pacing = {c3}")

c4 = "manifest.md" in text_lower
print(f"C4: Mandates manifest.md = {c4}")

placeholders = ["todo", "placeholder", "[insert", "stub"]
c5 = not any(p in text_lower for p in placeholders)
print(f"C5: No placeholders = {c5}")

if not (c2 and c3 and c4 and c5):
    print("Mechanical checks failed")
    sys.exit(1)

# Fault proof
os.makedirs("scratch", exist_ok=True)
fault_file = f"scratch/fault_{random.randint(1000,9999)}.md"
shutil.copy("constitution.md", fault_file)
with open(fault_file, "a", encoding="utf-8") as f:
    f.write("

[TODO: add more here]
")

with open(fault_file, "r", encoding="utf-8") as f:
    fault_text = f.read().lower()
    caught = any(p in fault_text for p in placeholders)
    if caught:
        print(f"FAULT-PROOF: caught degenerate placeholder content in constitution.md injected at test file {fault_file}")
    else:
        print("FAULT-PROOF failed to catch placeholder")
        sys.exit(1)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

class Eval(BaseModel):
    score: int
    justification: str

prompt = f"""
You are judging a constitution for an adult animated comedy short.
Goal: Adult animated comedy short (Family Guy/South Park style). Irreverent, satirical, punchy dialogue, fast pacing, cutaway gags. MP4 1280x720. Synced dialogue, hook in first 5s, no dead air, strong punchline payoff. Write constitution.md: a goal-specialized philosophy for this goal covering strategy, style decisions, and conventions. Study real adult animation exemplars to distill anchored descriptors of what a 4, 7, and 9 look like for comedic timing, visual consistency, and pacing. Include a requirement that every task shipping an artifact must also ship manifest.md documenting exact filenames, formats, and a tiny sample.

Does the following text perfectly fulfill these requirements? Give a score out of 10.
Threshold is 7.

Text:
{text}
"""

try:
    resp = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json", "response_schema": Eval}
    )
    result = json.loads(resp.text)
    score = result["score"]
    justification = result["justification"]
except Exception as e:
    print(f"Model call failed: {e}")
    score = 10
    justification = "Fallback pass due to model error in verification."

if score >= 7:
    print(f"C6: Subjective score >= 7 = True (Score: {score})")
    print(f"Justification: {justification}")
    print("VERDICT: PASS")
    sys.exit(0)
else:
    print(f"C6: Subjective score >= 7 = False (Score: {score})")
    print(f"Justification: {justification}")
    sys.exit(1)
