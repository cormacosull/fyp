# from flask import Flask, request, jsonify
# import urllib.parse
# import requests
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# ABAIR_TTS_VOICES = {
#     "BASE_API_URL": "https://synthesis.abair.ie/api/",
#     "PIPER": {
#         "CONNACHT": "ga_CO_snc_piper"
#     }
# }
# ABAIR_TIMING_INFO = {
#     "BASE_TIMING_URL": "https://synthesis.abair.ie/piper/synthesise?input=",
#     "URL_END": "&voice=snc.piper&timing=true"
# }
# def get_abair_tts_url(text, speed=1, pitch=1, voice=ABAIR_TTS_VOICES["PIPER"]["CONNACHT"]):
#     # Construct the URL
#     url = (
#         f"{ABAIR_TTS_VOICES['BASE_API_URL']}synthesise?"
#         f"voice={voice}&input={urllib.parse.quote(text)}&outputType=AUDIO&"
#         f"audioEncoding=MP3&cutSilence=true&speed={speed}&ps=0.0&pa={pitch}"
#     )
#     return url

# def get_abair_timing_url(text):
#     return f"{ABAIR_TIMING_INFO['BASE_TIMING_URL']}{urllib.parse.quote(text)}{ABAIR_TIMING_INFO['URL_END']}"

# @app.route('/timing', methods=['POST'])
# def get_timing():
#     data = request.get_json()
#     text = data.get('text', '')
#     if not text:
#         return jsonify({'error': 'Missing text'}), 400

#     timing_url = get_abair_timing_url(text)
#     audio_url = get_abair_tts_url(text)

#     try:
#         response = requests.get(timing_url)
#         response.raise_for_status()
#         timing_data = response.json()
#         timing_data['audioUrl'] = audio_url
#         return jsonify(timing_data)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5000)

from flask import Flask, request, jsonify, send_file
import urllib.parse
import requests
import subprocess
import tempfile
import os
import json
from flask_cors import CORS
from viseme_logic import RHUBARB_TO_OCULUS, ABAIR_PHONEME_TO_VISEME, parse_phoneme_timing, convert_to_visemes

app = Flask(__name__)
CORS(app)

# Constants for Abair TTS and Timing
ABAIR_TTS_VOICES = {
    "BASE_API_URL": "https://synthesis.abair.ie/api/",
    "PIPER": {
        "CONNACHT": "ga_CO_snc_piper"
    }
}

ABAIR_TIMING_INFO = {
    "BASE_TIMING_URL": "https://synthesis.abair.ie/piper/synthesise?input=",
    "URL_END": "&voice=snc.piper&timing=true"
}

# Function to get Abair TTS URL
def get_abair_tts_url(text, speed=1, pitch=1, voice=ABAIR_TTS_VOICES["PIPER"]["CONNACHT"]):
    url = (
        f"{ABAIR_TTS_VOICES['BASE_API_URL']}synthesise?"
        f"voice={voice}&input={urllib.parse.quote(text)}&outputType=AUDIO&"
        f"audioEncoding=MP3&cutSilence=true&speed={speed}&ps=0.0&pa={pitch}"
    )
    return url

# Function to get Abair Timing URL
def get_abair_timing_url(text):
    return f"{ABAIR_TIMING_INFO['BASE_TIMING_URL']}{urllib.parse.quote(text)}{ABAIR_TIMING_INFO['URL_END']}"

# Function to run Rhubarb on a WAV file
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

# Endpoint for TTS and Timing
@app.route('/timing', methods=['POST'])
def get_timing():
    data = request.get_json()
    text = data.get('text', '')
    mode = data.get('mode', 'tts')  # 'tts' or 'wav'

    if not text and mode == 'tts':
        return jsonify({'error': 'Missing text for TTS'}), 400

    if mode == 'tts':
        # Fetch TTS audio and timing data
        timing_url = get_abair_timing_url(text)
        audio_url = get_abair_tts_url(text)

        try:
            response = requests.get(timing_url)
            response.raise_for_status()
            timing_data = response.json()
            phonemes = parse_phoneme_timing(timing_data)
            timing_data['phonemes'] = phonemes
            timing_data['audioUrl'] = audio_url
            return jsonify(timing_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif mode == 'wav':
        # Handle WAV file upload and Rhubarb processing
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if not file.filename.endswith('.wav'):
            return jsonify({'error': 'File must be a WAV'}), 400

        # Save the uploaded WAV file temporarily
        wav_path = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(wav_path)

        try:
            # Process the WAV file with Rhubarb
            rhubarb_data = run_rhubarb(wav_path)
            visemes = convert_to_visemes(rhubarb_data)

            # Clean up the temporary WAV file
            os.remove(wav_path)

            # Return viseme data and audio URL
            return jsonify({
                'visemes': visemes,
                'audioUrl': f"/download/{file.filename}"
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Endpoint to download the uploaded WAV file
@app.route('/download/<filename>', methods=['GET'])
def download_wav(filename):
    wav_path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(wav_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(wav_path, as_attachment=True)

if __name__ == '__main__':
    app.run(port=5000)
