
import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

audio = AudioFileClip('dialogue.mp3')
dur = audio.duration

clip1 = ImageClip('scene1.png').set_duration(dur / 2.0)
clip2 = ImageClip('scene2.png').set_duration(dur - dur / 2.0)

final_video = concatenate_videoclips([clip1, clip2], method="compose")
final_video = final_video.set_audio(audio)
final_video.write_videofile('slice.mp4', fps=24, codec='libx264', audio_codec='aac')
