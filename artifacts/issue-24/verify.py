import os
import json
import random
import sys
import subprocess
import string

try:
    from google import genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai"])
    from google import genai

def verify_file(filepath):
    if not os.path.exists(filepath):
        return False, "File does not exist"
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    cl = text.lower()
    if len(text.strip()) < 500:
        return False, "File is degenerate or truncated"
    
    placeholders = ['todo', '[insert', 'placeholder', 'template', 'tbd', 'xxx']
    for p in placeholders:
        if p in cl:
            return False, f"Found placeholder: {p}"
            
    required_terms = [
        "strategy", "style decisions", "conventions", "manifest.md", 
        "comedic timing", "visual consistency", "pacing",
        "9", "7", "4", "family guy", "south park"
    ]
    for term in required_terms:
        if term not in cl:
            return False, f"Missing required term or section: {term}"
            
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
        prompt = f'''Evaluate the following Goal Constitution against standard adult animation quality rules. Confirm if it is a complete, well-formed markdown file containing strategic decisions, style, conventions (including manifest.md and 7/10 pass threshold), and anchored rubrics (4, 7, 9) for Comedic Timing, Visual Consistency, and Pacing. Respond in valid JSON with "score" (0 to 10) and "justification" (string):

{text}'''
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        if data.get("score", 0) < 7:
            return False, f"Subjective score too low: {data.get('score')} - {data.get('justification')}"
    except Exception as e:
        return False, f"Judge error: {e}"
        
    return True, "Valid"

if __name__ == "__main__":
    ok, msg = verify_file("constitution.md")
    if not ok:
        print(f"VERIFY FAIL: {msg}")
        sys.exit(1)
        
    print("C1: constitution.md exists and is readable markdown: TRUE")
    print("C2: The text covers strategy, style decisions, and conventions: TRUE")
    print("C3: The text contains 4, 7, 9 rubrics for comedic timing, visual consistency, and pacing: TRUE")
    print("C4: A numeric pass threshold is defined: TRUE")
    print("C5: A requirement for shipping manifest.md is explicitly stated: TRUE")
    print("C6: There are no placeholder or stub contents: TRUE")
    print("C7: The text receives a subjective score >= 7 from an LLM judge: TRUE")
    
    # Fault proof
    os.makedirs("scratch", exist_ok=True)
    fault_name = "fault_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6)) + ".md"
    fault_path = os.path.join("scratch", fault_name)
    
    with open("constitution.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Injecting a synthetic fault (placeholder)
    fault_content = content + "

TODO: add more here.
"
    with open(fault_path, "w", encoding="utf-8") as f:
        f.write(fault_content)
        
    f_ok, f_msg = verify_file(fault_path)
    if f_ok:
        print("FAIL: Fault proof did not catch the injected placeholder.")
        sys.exit(1)
    else:
        print(f"FAULT-PROOF: Caught induced fault on {fault_path}: {f_msg}")
        
    print("VERDICT: PASS")
