import urllib.parse
import requests
import time
from pydub import AudioSegment
from pydub.playback import play
import threading
import os

# Constants similar to the JavaScript version
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
    # Construct the URL
    url = (
        f"{ABAIR_TIMING_INFO['BASE_TIMING_URL']}"
        f"{urllib.parse.quote(text)}"
        f"{ABAIR_TIMING_INFO['URL_END']}"
    )
    return url

def play_audio(audio_file_path):
    # Load and play the audio file
    audio = AudioSegment.from_file(audio_file_path)
    play(audio)

# Example usage
text = input("Cuir isteach abairt as gaelainn\n")
url = get_abair_tts_url(text)
timing = get_abair_timing_url(text)

# Fetching the timing data from the API endpoint
response = requests.get(timing)
data = response.json()

# Download the audio file
audio_response = requests.get(url)
audio_file_path = "output.mp3"

with open(audio_file_path, 'wb') as audio_file:
    audio_file.write(audio_response.content)

# Start playing the audio in a separate thread
audio_thread = threading.Thread(target=play_audio, args=(audio_file_path,))
audio_thread.start()

# Print phonemes in time with the audio
previous_end = 0
timing = data['timing']
for entry in timing:
    for phone in entry['phones']:
        # Calculate the wait time
        wait_time = phone['end'] - previous_end
        time.sleep(wait_time)  # Wait for the specified time
        print(phone['symbol'], end=' ')  # Print the phoneme with a space
        previous_end = phone['end']  # Update the previous end time
    print()  # Print a newline at the end

# Wait for the audio to finish playing
audio_thread.join()

# Clean up the audio file if needed
os.remove(audio_file_path)
