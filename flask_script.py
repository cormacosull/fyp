from flask import Flask, request, jsonify
import urllib.parse
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
def get_abair_tts_url(text, speed=1, pitch=1, voice=ABAIR_TTS_VOICES["PIPER"]["CONNACHT"]):
    # Construct the URL
    url = (
        f"{ABAIR_TTS_VOICES['BASE_API_URL']}synthesise?"
        f"voice={voice}&input={urllib.parse.quote(text)}&outputType=AUDIO&"
        f"audioEncoding=MP3&cutSilence=true&speed={speed}&ps=0.0&pa={pitch}"
    )
    return url

def get_abair_timing_url(text):
    return f"{ABAIR_TIMING_INFO['BASE_TIMING_URL']}{urllib.parse.quote(text)}{ABAIR_TIMING_INFO['URL_END']}"

@app.route('/timing', methods=['POST'])
def get_timing():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'Missing text'}), 400

    timing_url = get_abair_timing_url(text)
    audio_url = get_abair_tts_url(text)

    try:
        response = requests.get(timing_url)
        response.raise_for_status()
        timing_data = response.json()
        timing_data['audioUrl'] = audio_url
        return jsonify(timing_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
