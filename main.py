import requests
import urllib.parse

# Constants similar to the JavaScript version
ABAIR_TTS_VOICES = {
    "BASE_API_URL": "https://synthesis.abair.ie/api/",
    "PIPER": {
        "CONNACHT": "ga_CO_snc_piper"
    }
}

def get_abair_tts_url(text, speed=1, pitch=1, voice=ABAIR_TTS_VOICES["PIPER"]["CONNACHT"]):
    # Construct the URL
    url = (
        f"{ABAIR_TTS_VOICES['BASE_API_URL']}synthesise?"
        f"voice={voice}&input={urllib.parse.quote(text)}&outputType=AUDIO&"
        f"audioEncoding=MP3&cutSilence=true&speed={speed}&ps=0.0&pa={pitch}"
    )
    return url

# Example usage
text = "ta me go maith"
url = get_abair_tts_url(text)
print(url)
