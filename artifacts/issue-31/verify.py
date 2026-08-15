import os, sys, subprocess, zipfile, random, shutil, json, time

# FIRST-LINE LAW: verify.py -> verify.py - verification suite for Tracer Slice and Capabilities Probe

def bootstrap():
    try:
        import imageio
        from google import genai
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "imageio", "imageio-ffmpeg"])

bootstrap()
import imageio
from google import genai

def run_checks(zip_path, run_perceptual=True):
    results = {"C1": False, "C2": False, "C3": False, "C4": False, "C5": False}
    reasons = []
    
    if not os.path.exists(zip_path):
        return results, "missing zip"
        
    temp_dir = "scratch/verify_temp_run"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # C1: Zip Integrity
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            names = set(z.namelist())
            expected = {"manifest.md", "capabilities.md", "slice.mp4"}
            if names != expected:
                reasons.append(f"C1 Failed: files in zip {names} != {expected}")
            else:
                results["C1"] = True
                z.extractall(temp_dir)
    except Exception as e:
        reasons.append(f"C1 Failed: zip error {e}")
        return results, "; ".join(reasons)
        
    # C2: Mechanical Video/Audio
    mp4_path = os.path.join(temp_dir, "slice.mp4")
    if os.path.exists(mp4_path):
        try:
            reader = imageio.get_reader(mp4_path)
            meta = reader.get_meta_data()
            size = meta.get('size', (0,0))
            duration = meta.get('duration', 0)
            reader.close()
            if size == (1280, 720) and 8 <= duration <= 12:
                results["C2"] = True
            else:
                reasons.append(f"C2 Failed: size={size} (expected 1280x720), duration={duration} (expected 8-12s)")
        except Exception as e:
            reasons.append(f"C2 Failed: imageio error {e}")
    else:
        reasons.append("C2 Failed: slice.mp4 missing")
        
    # C3: No Placeholders
    manifest_path = os.path.join(temp_dir, "manifest.md")
    capabilities_path = os.path.join(temp_dir, "capabilities.md")
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            man = f.read()
        with open(capabilities_path, 'r', encoding='utf-8') as f:
            cap = f.read()
            
        man_ok = len(man) > 50 and "placeholder" not in man.lower() and "todo" not in man.lower()
        cap_ok = len(cap) > 100 and "placeholder" not in cap.lower() and "todo" not in cap.lower()
        if man_ok and cap_ok:
            results["C3"] = True
        else:
            reasons.append(f"C3 Failed: man_len={len(man)}, cap_len={len(cap)}, placeholders checked")
    except Exception as e:
        reasons.append(f"C3 Failed: read error {e}")
        
    # C4 & C5: Perceptual checks via Gemini
    if run_perceptual and 'GEMINI_API_KEY' in os.environ and results["C2"]:
        try:
            client = genai.Client()
            # Upload to gemini
            video_file = client.files.upload(file=mp4_path)
            
            # Wait for video processing
            state = "PROCESSING"
            for _ in range(30):
                file_info = client.files.get(name=video_file.name)
                state = file_info.state.name
                if state in ["ACTIVE", "FAILED"]:
                    break
                time.sleep(2)
                
            if state == "ACTIVE":
                prompt = """
                Evaluate this 10-second adult-animation comedy slice against these criteria:
                1. Does it depict an animated character with a voiced line (lip sync/voice audio)? (C4 claim)
                2. Is there exactly 1 scene, 1 cut, and 1 voiced line? (C4 claim)
                3. Rate the overall humor, pacing, visual cohesion, and execution from 0 to 10 based on standard adult animation comedy (like South Park or Family Guy) where >=7 is good, professional, non-placeholder, and actually funny/absurd. (C5 claim)
                
                Return your evaluation as a JSON object with this exact schema:
                {
                    "c4_pass": boolean,
                    "c4_reason": string,
                    "c5_score": number (0.0 to 10.0),
                    "c5_reason": string
                }
                """
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[video_file, prompt],
                    config={"response_mime_type": "application/json"}
                )
                try:
                    data = json.loads(response.text)
                    if data.get("c4_pass"):
                        results["C4"] = True
                    else:
                        reasons.append(f"C4 Failed: {data.get('c4_reason')}")
                        
                    score = data.get("c5_score", 0.0)
                    if score >= 7.0:
                        results["C5"] = True
                    else:
                        reasons.append(f"C5 Failed: score={score} reason={data.get('c5_reason')}")
                except Exception as e:
                    reasons.append(f"Perceptual response parsing failed: {e}. Raw: {response.text}")
            else:
                reasons.append(f"Video upload state remained {state}")
        except Exception as e:
            reasons.append(f"Perceptual API error: {e}")
    else:
        if not run_perceptual:
            reasons.append("Perceptual checks skipped by request")
        else:
            reasons.append("Perceptual checks skipped: API key or mechanical preconditions missing")
            
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    return results, "; ".join(reasons)

def test_fault_proof(real_zip_path):
    # Induce a fault by corrupting a scratch copy and verify it gets caught
    os.makedirs("scratch", exist_ok=True)
    scratch_zip = "scratch/fault_test.zip"
    
    # Case A: corrupting the zip entries
    try:
        if os.path.exists(real_zip_path):
            shutil.copy(real_zip_path, scratch_zip)
            # Modify zip to violate files list
            with zipfile.ZipFile(scratch_zip, 'w') as z:
                z.writestr("manifest.md", "# Manifest\nplaceholder placeholder placeholder placeholder placeholder")
            res, reason = run_checks(scratch_zip, run_perceptual=False)
            if not res["C1"] or not res["C3"]:
                return f"Successfully caught induced C1/C3 fault! Result: {res}"
        else:
            # No zip exists yet - make a fake faulty zip
            with zipfile.ZipFile(scratch_zip, 'w') as z:
                z.writestr("manifest.md", "bad stuff")
            res, reason = run_checks(scratch_zip, run_perceptual=False)
            if not res["C1"] or not res["C2"] or not res["C3"]:
                return f"Successfully caught induced fault on mock zip! Result: {res}"
    except Exception as e:
        return f"Fault proof error: {e}"
    finally:
        if os.path.exists(scratch_zip):
            os.remove(scratch_zip)
    return "FAILED to catch induced fault!"

if __name__ == "__main__":
    print("EXPECT: verify.py executes C1-C5 checks and confirms validity")
    zip_path = "tracer_bundle.zip"
    
    # Run fault proof first
    fault_evidence = test_fault_proof(zip_path)
    print(f"FAULT-PROOF: {fault_evidence}")
    
    results, reason = run_checks(zip_path, run_perceptual=True)
    for c, val in sorted(results.items()):
        print(f"{c}: {val}")
        
    if reason:
        print(f"Details: {reason}")
        
    if all(results.values()):
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)
