import urllib.parse
import requests

# Constants similar to the JavaScript version
ABAIR_TTS_VOICES = {
    "BASE_API_URL": "https://synthesis.abair.ie/api/",
    "PIPER": {
        "CONNACHT": "ga_CO_snc_piper"
    }
}
ABAIR_TIMING_INFO = {
    "BASE_TIMING_URL" : "https://synthesis.abair.ie/piper/synthesise?input=",
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
    # Construct the URL
    url = (
        f"{ABAIR_TIMING_INFO['BASE_TIMING_URL']}"
        f"{urllib.parse.quote(text)}"
        f"{ABAIR_TIMING_INFO['URL_END']}"
    )
    return url

# Example usage
text = "ta me go maith"
url = get_abair_tts_url(text)
timing = get_abair_timing_url(text)
print(url)
print(timing)


# Example: Fetching the data from an API endpoint
response = requests.get(timing)
data = response.json()


timing = data['timing']
print("Timing:", timing)

