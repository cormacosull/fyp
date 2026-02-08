import json
import subprocess
import tempfile
import os
from viseme_mapping import RHUBARB_TO_OCULUS

def run_rhubarb(wav_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        json_path = tmp.name

    subprocess.run(
        ["rhubarb", "-f", "json", "-o", json_path, wav_path],
        check=True
    )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.remove(json_path)
    return data

def convert_to_visemes(rhubarb_json):
    visemes = []

    for cue in rhubarb_json.get("mouthCues", []):
        visemes.append({
            "start": cue["start"],
            "end": cue["end"],
            "viseme": RHUBARB_TO_OCULUS.get(cue["value"], "sil")
        })

    return visemes
