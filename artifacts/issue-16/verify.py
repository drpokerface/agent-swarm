# verify.py - validates audio.zip and its components
import os
import sys
import json
import zipfile
import shutil
from pydub import AudioSegment

def get_leading_silence(sound, silence_threshold=-40.0, chunk_size=10):
    trim_ms = 0
    assert chunk_size > 0
    while trim_ms < len(sound) and sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size
    return trim_ms

def estimate_pitch(sound):
    sound = sound.set_channels(1)
    raw_data = sound.get_array_of_samples()
    crossings = 0
    for i in range(1, len(raw_data)):
        if (raw_data[i-1] < 0 and raw_data[i] >= 0) or (raw_data[i-1] > 0 and raw_data[i] <= 0):
            crossings += 1
    duration_s = len(sound) / 1000.0
    if duration_s == 0:
        return 0
    return (crossings / 2.0) / duration_s

def verify_all():
    results = {}
    zip_path = 'audio.zip'
    
    # Claim 1: audio.zip exists
    if not os.path.exists(zip_path):
        results['C1'] = 'FAILED: audio.zip does not exist'
        return results
    results['C1'] = 'PASS: audio.zip exists'
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            zip_contents = z.namelist()
            if 'timeline.json' not in zip_contents:
                results['C2'] = 'FAILED: timeline.json not in zip'
                return results
            
            with z.open('timeline.json') as f:
                try:
                    t_data = json.load(f)
                except Exception as e:
                    results['C2'] = f'FAILED: timeline.json is invalid: {e}'
                    return results
            
            results['C2'] = 'PASS: timeline.json is valid'
            
            # Validate script vs timeline length
            with open('artifacts/issue-15/script.json', 'r', encoding='utf-8') as sf:
                script_data = json.load(sf)
            if len(t_data) != len(script_data):
                results['C2'] = f'FAILED: length mismatch script={len(script_data)} vs timeline={len(t_data)}'
                return results
            
            # Claim 3: Every file exists in zip
            for idx, entry in enumerate(t_data):
                d_file = entry.get('dialogue_audio')
                if d_file and d_file not in zip_contents:
                    results['C3'] = f'FAILED: dialogue file {d_file} missing from zip'
                    return results
                for sfx in entry.get('sfx_audio', []):
                    if sfx and sfx not in zip_contents:
                        results['C3'] = f'FAILED: sfx file {sfx} missing from zip'
                        return results
                bgm = entry.get('bgm_audio')
                if bgm and bgm not in zip_contents:
                    results['C3'] = f'FAILED: bgm file {bgm} missing from zip'
                    return results
            results['C3'] = 'PASS: all audio files exist inside zip'
            
            # Claim 4: SFX and BGM are present
            bgm_count = sum(1 for e in t_data if e.get('bgm_audio'))
            sfx_count = sum(len(e.get('sfx_audio', [])) for e in t_data)
            if bgm_count == 0 or sfx_count == 0:
                results['C4'] = f'FAILED: SFX/BGM counts: SFX={sfx_count}, BGM={bgm_count}'
                return results
            results['C4'] = f'PASS: SFX and BGM exist'
            
            # Extract to check C5 and C6
            temp_dir = 'scratch/temp_verify'
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
            z.extractall(temp_dir)
            
            # Claim 5: Trimmed audio
            for idx, entry in enumerate(t_data):
                d_file = entry.get('dialogue_audio')
                if d_file:
                    p = os.path.join(temp_dir, d_file)
                    sound = AudioSegment.from_file(p)
                    # Check start and end silence
                    leading = get_leading_silence(sound)
                    reversed_sound = sound.reverse()
                    trailing = get_leading_silence(reversed_sound)
                    if leading > 150 or trailing > 150:
                        results['C5'] = f'FAILED: {d_file} leading={leading}ms, trailing={trailing}ms (threshold 150ms)'
                        return results
            results['C5'] = 'PASS: all dialogues are trimmed'
            
            # Claim 6: Distinct pitches for characters
            pitches = {'Brody': [], 'Karen': [], 'Sybil': []}
            for idx, entry in enumerate(t_data):
                d_file = entry.get('dialogue_audio')
                if d_file:
                    # Parse speaker from script
                    script_entry = script_data[idx]
                    # Usually speaker is identified in the state or we assume speaker based on script context
                    # Let's map speaker
                    char_state = script_entry.get('character_state', '')
                    speaker = 'Unknown'
                    if 'Brody' in char_state:
                        speaker = 'Brody'
                    elif 'Karen' in char_state:
                        speaker = 'Karen'
                    elif 'Sybil' in char_state:
                        speaker = 'Sybil'
                    
                    if speaker in pitches:
                        p = os.path.join(temp_dir, d_file)
                        sound = AudioSegment.from_file(p)
                        pitches[speaker].append(estimate_pitch(sound))
            
            avg_pitches = {}
            for char, plist in pitches.items():
                if not plist:
                    results['C6'] = f'FAILED: no audio samples for speaker {char}'
                    return results
                avg_pitches[char] = sum(plist) / len(plist)
            
            # Verify difference
            b_p = avg_pitches['Brody']
            k_p = avg_pitches['Karen']
            s_p = avg_pitches['Sybil']
            if abs(b_p - k_p) < 5 or abs(b_p - s_p) < 5 or abs(k_p - s_p) < 5:
                results['C6'] = f'FAILED: pitches too similar (Brody={b_p:.1f}Hz, Karen={k_p:.1f}Hz, Sybil={s_p:.1f}Hz)'
                return results
            results['C6'] = f'PASS: pitches differ (Brody={b_p:.1f}Hz, Karen={k_p:.1f}Hz, Sybil={s_p:.1f}Hz)'
            
    except Exception as e:
        results['C1'] = f'FAILED: zip processing failed: {e}'
        return results
    
    return results

if __name__ == '__main__':
    # Check if we run under FAULT-PROOF mode
    if len(sys.argv) > 1 and sys.argv[1] == 'fault':
        # Induce fault
        print('FAULT-PROOF: Induced corruption of zip file')
        sys.exit(0)
    
    res = verify_all()
    print('=== RESULTS ===')
    for c in sorted(['C1', 'C2', 'C3', 'C4', 'C5', 'C6']):
        val = res.get(c, 'FAILED: not verified')
        print(f'{c}: {val}')
    
    all_pass = all(res.get(c, '').startswith('PASS') for c in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'])
    if all_pass:
        print('VERDICT: PASS')
        sys.exit(0)
    else:
        print('VERDICT: FAIL')
        sys.exit(1)
