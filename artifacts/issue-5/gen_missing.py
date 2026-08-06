
import asyncio
import edge_tts
import os

dialogues = [
    (14, 'DAVE', 'Look, Zalgor, buddy. What do I have to do? Blood sacrifice? Firstborn child?'),
    (15, 'ZALGOR', "We stopped doing blood sacrifices in '98. Too messy. HR hated it. We just need a verbal agreement."),
    (16, 'DAVE', 'Okay, I verbally agree to cancel.'),
    (17, 'ZALGOR', "No, to the terms and conditions. The ones you didn't read in 2014 when you clicked 'Accept'."),
    (18, 'DAVE', 'Fine! I agree! Whatever it is, I agree! Take everything!'),
    (19, 'ZALGOR', 'Excellent. Your soul is now legally property of the cable company. And your service is... wait for it...'),
    (20, 'ZALGOR', 'Cancelled.'),
    (21, 'DAVE', 'Finally! ...Wait, my soul?'),
    (22, 'ZALGOR', 'Yep. The retention department will collect it on Tuesday between 8 AM and Never. Have a hellish day!')
]

async def gen():
    for i, speaker, text in dialogues:
        voice = 'en-US-GuyNeural' if speaker == 'DAVE' else 'en-GB-RyanNeural'
        pitch = '+0Hz' if speaker == 'DAVE' else '-20Hz'
        communicate = edge_tts.Communicate(text, voice, pitch=pitch)
        out_path = f'audio_out/dialogue_{i}.mp3'
        if not os.path.exists(out_path):
            await communicate.save(out_path)

asyncio.run(gen())
