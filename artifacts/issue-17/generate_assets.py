import json
import re
import os
import io
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from google import genai
from google.genai import types

def sanitize(text):
    return re.sub(r'[^a-z0-9]', '_', text.lower())[:50].strip('_')

def get_required_assets(script_path):
    with open(script_path, 'r') as f:
        script = json.load(f)
    bgs = set()
    chars = set()
    for scene in script:
        bg = scene.get('background', '')
        if bg: bgs.add(bg)
        c_state = scene.get('character_state', '')
        if c_state and ':' in c_state:
            name, pose = c_state.split(':', 1)
            chars.add((name.strip(), pose.strip()))
    return bgs, chars

def remove_green_background(img):
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        if item[1] > 120 and item[0] < item[1] * 0.8 and item[2] < item[1] * 0.8:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def generate_image_with_retry(client, prompt, aspect_ratio="16:9", max_retries=2):
    for model_name in ['imagen-3.0-generate-002', 'imagen-3.0-generate-001']:
        for attempt in range(max_retries):
            try:
                result = client.models.generate_images(
                    model=model_name,
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio=aspect_ratio,
                    )
                )
                return result.generated_images[0].image.image_bytes
            except Exception as e:
                err_str = str(e).lower()
                if "not found" in err_str or "unsupported" in err_str:
                    break
                if "429" in err_str or "quota" in err_str:
                    time.sleep(2 ** attempt)
                else:
                    time.sleep(1)
    return None

def main():
    os.makedirs('backgrounds', exist_ok=True)
    os.makedirs('characters', exist_ok=True)
    
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    bgs, chars = get_required_assets('artifacts/issue-15/script.json')
    
    def make_bg(bg):
        filename = f"backgrounds/{sanitize(bg)}.png"
        if os.path.exists(filename): return
        prompt = f"2D animated background, adult animated comedy style, flat colors, clear outlines. {bg}"
        img_bytes = generate_image_with_retry(client, prompt, "16:9")
        if img_bytes:
            try:
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                img = img.resize((1280, 720))
                img.save(filename)
                print(f"Generated {filename}")
                return
            except Exception as e:
                pass
        print(f"Fallback to dummy for {filename}")
        img = Image.new('RGB', (1280, 720), color='lightblue')
        img.save(filename)

    def make_char(name, pose, mouth_state):
        char_dir = f"characters/{sanitize(name)}"
        os.makedirs(char_dir, exist_ok=True)
        filename = f"{char_dir}/{sanitize(pose)}_{mouth_state}.png"
        if os.path.exists(filename): return
        
        mouth_desc = "mouth is closed" if mouth_state == "closed" else "mouth is wide open speaking"
        prompt = f"2D animated character cutout, adult animated comedy style, flat colors, solid bright green background #00FF00. Character {name}, {pose}. {mouth_desc}."
        
        img_bytes = generate_image_with_retry(client, prompt, "1:1")
        if img_bytes:
            try:
                img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
                img = remove_green_background(img)
                img.save(filename)
                print(f"Generated {filename}")
                return
            except Exception as e:
                pass
        print(f"Fallback to dummy for {filename}")
        img = Image.new('RGBA', (512, 512), color=(255, 0, 0, 0))
        img.save(filename)

    tasks = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for bg in bgs:
            tasks.append(executor.submit(make_bg, bg))
        for name, pose in chars:
            tasks.append(executor.submit(make_char, name, pose, "closed"))
            tasks.append(executor.submit(make_char, name, pose, "open"))
            
        for future in as_completed(tasks):
            pass

    with zipfile.ZipFile('visuals.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('backgrounds'):
            for f in files:
                zf.write(os.path.join(root, f))
        for root, dirs, files in os.walk('characters'):
            for f in files:
                zf.write(os.path.join(root, f))

if __name__ == '__main__':
    main()
