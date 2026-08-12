# verify.py - Rollup verification of visual assets
import os
import zipfile
import sys
from PIL import Image

def verify(zip_path="visuals.zip"):
    print("Verifying C1: visuals.zip exists")
    if not os.path.exists(zip_path):
        print(f"C1 FAILED: {zip_path} not found")
        return False
    print("C1: PASS")
    
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            namelist = z.namelist()
            
            print("Verifying C2: 4 backgrounds, 1280x720")
            for i in range(1, 5):
                name = f"bg_{i}.png"
                if name not in namelist:
                    print(f"C2 FAILED: Missing {name}")
                    return False
                with z.open(name) as f:
                    try:
                        img = Image.open(f)
                        if img.size != (1280, 720):
                            print(f"C2 FAILED: {name} is {img.size}, expected (1280, 720)")
                            return False
                    except Exception as e:
                        print(f"C2 FAILED: Could not open {name} as image")
                        return False
            print("C2: PASS")
            
            print("Verifying C3: 19 sprites, transparent PNGs")
            for i in range(1, 20):
                name = f"sprite_{i}.png"
                if name not in namelist:
                    print(f"C3 FAILED: Missing {name}")
                    return False
                with z.open(name) as f:
                    try:
                        img = Image.open(f)
                        img = img.convert('RGBA')
                        alpha = img.split()[3]
                        if not any(p < 255 for p in alpha.getdata()):
                            print(f"C3 FAILED: {name} has no transparent pixels")
                            return False
                    except Exception as e:
                        print(f"C3 FAILED: Could not check transparency for {name}: {e}")
                        return False
            print("C3: PASS")
            
    except zipfile.BadZipFile:
        print(f"FAILED: {zip_path} is not a valid zip file")
        return False
        
    return True

if __name__ == "__main__":
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "Pillow"])
    
    print("Running fault proof on a missing zip...")
    if verify("scratch/nonexistent_fault.zip"):
        print("FAULT-PROOF FAILED: verify passed a nonexistent file")
        sys.exit(1)
    else:
        print("FAULT-PROOF: verify correctly failed when zip is missing")
    
    if verify():
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)
