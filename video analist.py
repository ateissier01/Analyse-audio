from moviepy import VideoFileClip
import whisper
import os
from rapidfuzz import fuzz
from pathlib import Path

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    
    return f"{h:02d}:{m:02d}:{s:02d}"

def sort(filepath,words,seuil) :
    base, ext = os.path.splitext(filepath)
    O_path = base + ".wav"

    video = VideoFileClip(filepath)
    video.audio.write_audiofile(O_path)

    model = whisper.load_model("base")

    result = model.transcribe(O_path)
    matches = []

    for segment in result["segments"]:
        text = segment["text"].lower()

        for word in words:
            score = fuzz.partial_ratio(word.lower(), text)

            if score > seuil :
                matches.append({"word": word,"start": segment["start"],"end": segment["end"]})
    
    clipass=Path(base)
    clipass.mkdir(parents=True, exist_ok=True)
    
    # ===== 4. EXTRACTION DES CLIPS =====
    for i, match in enumerate(matches):
        start = max(0, match["start"] - 1)  # marge avant
        end = match["end"] + 1              # marge après

        clip = video.subclipped(start, end)

        T=format_time(match["start"]).replace(":", "_")
        output_path = os.path.join(
            base,
            f"{match['word']}_{T}.mp4"
        )

        clip.write_videofile(output_path)



current_dir = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(current_dir, 'vid_totreat')

keywords_file = os.path.join(current_dir, 'mots_clef analise.txt')
with open(keywords_file, "r", encoding="utf-8") as f:
    keywords = [ligne.rstrip() for ligne in f]

for fichier in os.listdir(output_folder):
    if fichier.endswith(".mp4"):
        chemin_complet = os.path.join(output_folder, fichier)
        sort(chemin_complet,keywords,80)
