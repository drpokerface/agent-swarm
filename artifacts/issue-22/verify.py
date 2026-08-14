import os, zipfile, sys, wave, random, shutil
from google import genai
from PIL import Image

def fail(msg):
    print(msg)
    sys.exit(1)

def check_all(zip_path):
    if not os.path.exists(zip_path):
        return False, "C1: Failed - no zip"
    
    ext_dir = "scratch/ext_" + str(random.randint(1000,9999))
    os.makedirs(ext_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(ext_dir)
    except:
        return False, "C2: Failed - unzip error"
    
    if not os.path.exists(os.path.join(ext_dir, "manifest.md")):
        return False, "C3: Failed - manifest missing"

    files = os.listdir(ext_dir)
    wavs = [f for f in files if f.endswith('.wav')]
    jpgs = [f for f in files if f.endswith('.jpg')]
    if not wavs or not jpgs:
        return False, "C4: Failed - missing media"

    for j in jpgs:
        try:
            img = Image.open(os.path.join(ext_dir, j))
            img.verify()
        except:
            return False, "C4: Failed - invalid image"

    for w in wavs:
        try:
            with wave.open(os.path.join(ext_dir, w), 'rb') as wv:
                frames = wv.readframes(wv.getnframes())
                if not frames or all(b == 0 for b in frames):
                    return False, "C5: Failed - silent/empty wav"
        except:
            return False, "C5: Failed - bad wav"
            
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    sample_img = os.path.join(ext_dir, random.choice(jpgs))
    handle = client.files.upload(file=sample_img)
    res = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=["Does this image contain the word 'Scene' or depict animation content? YES or NO.", handle]
    )
    if "YES" not in res.text.upper():
        return False, "C6: Failed - perception check failed"
        
    return True, "Pass"

ok, msg = check_all("assets.zip")
if not ok:
    fail(msg)

print("C1: Pass")
print("C2: Pass")
print("C3: Pass")
print("C4: Pass")
print("C5: Pass")
print("C6: Pass")

shutil.copy("assets.zip", "scratch/fault.zip")
with zipfile.ZipFile("scratch/fault.zip", "a") as zf:
    zf.writestr("bad.wav", b"")
ok, msg = check_all("scratch/fault.zip")
if not ok:
    print(f"FAULT-PROOF: Caught corrupted artifact: {msg}")
else:
    fail("FAULT-PROOF: Failed to catch corruption")

print("VERDICT: PASS")
sys.exit(0)
