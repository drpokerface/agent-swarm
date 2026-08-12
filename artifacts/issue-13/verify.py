# VERIFIER
import os, sys, random, json, shutil, re

try:
    from google import genai
    from google.genai import types
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'google-genai', 'pydantic'])
    from google import genai
    from google.genai import types

def evaluate_spec(content: str) -> dict:
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    prompt = f'''Evaluate the following specification document for an animated comedy.
    
DOCUMENT:
{content}

Evaluate it against these criteria:
c2: Does it analyze ALL of the following: pacing, joke structure, cutaway mechanics, and visual shorthand?
c3: Does it explicitly state that it targets "adult animated comedy" (or cite examples like South Park, Family Guy) AND mention the context of a "~2 minute" comedy short?
c4: Does it contain a scoring rubric with a 1-5 scale for ALL four of these categories: 'comedic timing', 'hook strength', 'sync quality', and 'visual coherence'?
c5: Does the rubric use strictly concrete, measurable anchored descriptors (e.g., exact times like '0.5s', exact frame counts, exact WPM) for its scoring levels, rather than subjective fluff (like 'good', 'bad', 'fast', 'slow' without numbers)?
'''
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "c2": {"type": "boolean"},
                "c3": {"type": "boolean"},
                "c4": {"type": "boolean"},
                "c5": {"type": "boolean"}
            },
            "required": ["c2", "c3", "c4", "c5"]
        }
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=config
        )
        return json.loads(response.text)
    except Exception as e:
        print(f'Evaluation error: {e}')
        return {"c2": False, "c3": False, "c4": False, "c5": False}

def verify():
    if not os.path.exists('spec.md'):
        print('C1 (Exists): False')
        return False
    else:
        print('C1 (Exists): True')
        
    with open('spec.md', 'r', encoding='utf-8') as f:
        real_content = f.read()
        
    eval_real = evaluate_spec(real_content)
    print(f"C2 (analysis): {eval_real.get('c2', False)}")
    print(f"C3 (adult/2min context): {eval_real.get('c3', False)}")
    print(f"C4 (1-5 scales): {eval_real.get('c4', False)}")
    print(f"C5 (concrete descriptors): {eval_real.get('c5', False)}")
    
    if not all([eval_real.get('c2', False), eval_real.get('c3', False), eval_real.get('c4', False), eval_real.get('c5', False)]):
        print('VERDICT: FAIL - Does not meet all criteria')
        return False

    # Fault proof
    os.makedirs('scratch', exist_ok=True)
    bad_id = random.randint(1000, 9999)
    bad_file = f'scratch/spec_corrupted_{bad_id}.md'
    
    match = re.search(r'#+\s*.*Rubric', real_content, re.IGNORECASE)
    if match:
        rubric_idx = match.start()
        bad_content = real_content[:rubric_idx] + """## Scoring Rubric

### 1. Comedic Timing
* 1: Terrible timing
* 2: Poor pacing
* 3: Acceptable timing
* 4: Good pacing
* 5: Excellent comedic timing

### 2. Hook Strength
* 1: No hook
* 2: Weak hook
* 3: Moderate hook
* 4: Strong hook
* 5: Incredible hook

### 3. Sync Quality
* 1: Completely desynced
* 2: Bad sync
* 3: Mostly synced
* 4: Well synced
* 5: Perfect sync

### 4. Visual Coherence
* 1: Very glitchy
* 2: Some glitches
* 3: Average visuals
* 4: Good visuals
* 5: Flawless visuals
"""
    else:
        bad_content = re.sub(r'\b\d+(\.\d+)?\s*(s|seconds|frames|WPM|ms|wpm|fps)\b', 'some', real_content)
    
    with open(bad_file, 'w', encoding='utf-8') as f:
        f.write(bad_content)
        
    eval_bad = evaluate_spec(bad_content)
    if eval_bad.get('c5', False) is True:
        print(f'FAULT-PROOF FAILED: Did not catch subjective rubric in {bad_file}. C5 was True.')
        return False
    else:
        print(f'FAULT-PROOF: Caught subjective rubric under {bad_file}. Reason: C5=False')
        
    print('VERDICT: PASS')
    return True

if __name__ == '__main__':
    if not verify():
        sys.exit(1)
