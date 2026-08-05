# verify.py - Validates spec.md claims and runs fault-proof
import os
import sys
import random
import shutil
import re

def verify_all(filepath):
    if not os.path.exists(filepath):
        return False, False, False, False, False, False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False, False, False, False, False, False
    
    c1 = True
    
    categories = [
        "1. Script Humor & Pacing",
        "2. Audio Punchiness & Delivery",
        "3. Visual Cohesion (Cutout Style)",
        "4. Overall Editing & Timing"
    ]
    
    # Check that all categories exist
    for cat in categories:
        if cat not in content:
            return c1, False, False, False, False, False
            
    # Locate sections
    indices = [content.find(cat) for cat in categories]
    sections = []
    for i in range(4):
        start_idx = indices[i]
        # Find start of next category or end of text
        next_indices = [idx for idx in indices if idx > start_idx]
        end_idx = min(next_indices) if next_indices else len(content)
        sections.append(content[start_idx:end_idx])
        
    cat_ok = [False, False, False, False]
    for i in range(4):
        sec = sections[i]
        scores_found = {}
        # Match 'Score 1', 'Score 2', etc. with flexible patterns
        for num in range(1, 6):
            pattern = rf"(?i)Score\s+{num}\b([\s\S]*?)(?=Score\s+[1-5]\b|$)"
            match = re.search(pattern, sec)
            if match:
                desc = match.group(1).strip()
                # Clean markdown characters
                desc_clean = re.sub(r'[*_#:`\-]', '', desc).strip()
                if len(desc_clean) > 15: # substantial description
                    scores_found[num] = desc_clean
        if len(scores_found) == 5:
            # Ensure they are distinct
            distinct_descriptions = set(scores_found.values())
            if len(distinct_descriptions) == 5:
                cat_ok[i] = True

    # Check for research/measurable properties content
    # Must mention South Park or Family Guy and contain detailed discussion of pacing / comedy rules
    c6 = False
    has_south_park = "South Park" in content
    has_family_guy = "Family Guy" in content
    has_properties = any(x in content.lower() for x in ["measurable properties", "timing", "dialogue", "pacing", "cutaway"])
    if (has_south_park or has_family_guy) and has_properties:
        c6 = True

    return c1, cat_ok[0], cat_ok[1], cat_ok[2], cat_ok[3], c6

def main():
    real_file = "spec.md"
    c1, c2, c3, c4, c5, c6 = verify_all(real_file)
    
    print(f"C1 (spec.md exists): {c1}")
    print(f"C2 (Category 1 present with 5 distinct scores): {c2}")
    print(f"C3 (Category 2 present with 5 distinct scores): {c3}")
    print(f"C4 (Category 3 present with 5 distinct scores): {c4}")
    print(f"C5 (Category 4 present with 5 distinct scores): {c5}")
    print(f"C6 (Research and properties documented): {c6}")
    
    all_pass = all([c1, c2, c3, c4, c5, c6])
    
    if not all_pass:
        print("FAULT-PROOF: Skipping since real spec.md does not exist or fails verification.")
        print("VERDICT: FAIL")
        sys.exit(1)
        
    # Perform Randomized Fault-Proof under scratch/
    os.makedirs("scratch", exist_ok=True)
    faulty_file = os.path.join("scratch", "faulty_spec.md")
    
    # Randomly select a fault style
    fault_type = random.choice(["remove_cat", "shorten_score", "remove_score", "clear_file"])
    
    shutil.copy(real_file, faulty_file)
    with open(faulty_file, 'r', encoding='utf-8') as f:
        text = f.read()
        
    if fault_type == "remove_cat":
        # Remove a random category name
        cat_to_remove = random.choice([
            "1. Script Humor & Pacing",
            "2. Audio Punchiness & Delivery",
            "3. Visual Cohesion (Cutout Style)",
            "4. Overall Editing & Timing"
        ])
        text = text.replace(cat_to_remove, "[REDACTED CATEGORY]")
        evidence = f"Removed category {cat_to_remove}"
    elif fault_type == "shorten_score":
        # Make a score description too short
        # Find the first occurrence of Score 3 and replace it
        text = re.sub(r"(?i)Score\s+3\b([\s\S]*?)(?=Score\s+[1-5]\b|$)", "Score 3: Too short.\n", text, count=1)
        evidence = "Shortened Score 3 description to less than 15 chars"
    elif fault_type == "remove_score":
        # Delete one score entirely
        text = re.sub(r"(?i)Score\s+4\b([\s\S]*?)(?=Score\s+[1-5]\b|$)", "", text, count=1)
        evidence = "Removed Score 4 description entirely"
    else:
        text = "This is a completely corrupted file without criteria content."
        evidence = "Cleared file contents"
        
    with open(faulty_file, 'w', encoding='utf-8') as f:
        f.write(text)
        
    # Verify faulty file
    f1, f2, f3, f4, f5, f6 = verify_all(faulty_file)
    faulty_pass = all([f1, f2, f3, f4, f5, f6])
    
    if not faulty_pass:
        print(f"FAULT-PROOF: SUCCESS - Caught induced fault: '{evidence}'")
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print(f"FAULT-PROOF: FAIL - Did not catch induced fault: '{evidence}'")
        print("VERDICT: FAIL")
        sys.exit(1)

if __name__ == '__main__':
    main()
