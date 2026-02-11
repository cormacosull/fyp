import { playVisemes } from './viseme_logic.js';
import { meshesWithMorphs } from './three_js.js';

export function getAudioMode() {
    return document.querySelector('input[name="audioMode"]:checked').value;
}

export function updateAudioModeUI() {
    const mode = document.querySelector('input[name="audioMode"]:checked').value;
    document.getElementById('wavInputs').style.display = mode === 'wav' ? 'block' : 'none';
    document.getElementById('ttsInputs').style.display = mode === 'tts' ? 'block' : 'none';
}

export async function submitText() {
    const mode = getAudioMode();
    const resultBox = document.getElementById('resultOutput');
    resultBox.value = '';

    //if wav
    if (mode === 'wav') {
        const fileInput = document.getElementById('wavInput');
        const file = fileInput.files[0];

        if (!file) {
            alert('Roghnaigh comhad WAV.');
            return;
        }

        resultBox.value = 'Ag próiseáil WAV...';
        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("mode", "wav");

            const response = await fetch('http://127.0.0.1:5000/timing', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            resultBox.value = data.phonemes
                .map(v => `${v.viseme} @ ${v.end.toFixed(2)}s`)
                .join('\n');

            const audioEl = document.getElementById('ttsAudio');
            audioEl.src = URL.createObjectURL(file);
            audioEl.load();

            audioEl.oncanplay = async () => {
                audioEl.play();
                playVisemes(data.phonemes, meshesWithMorphs)
            };
        } catch (err) {
            console.error(err);
            resultBox.value = `Earráid: ${err.message}`;
        }
        return;
    }

    const text = document.getElementById('sentenceInput').value.trim();

    //else
    //if no text send an error
    if (!text) {
        alert('Cuir isteach abairt ar dtús.');
        return;
    }

    resultBox.value = 'Ag seoladh...';

    try {
        //send text to backend
        const response = await fetch('http://127.0.0.1:5000/timing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        //recieve answer
        const data = await response.json();
        const phonemes = data.phonemes;
        console.log("phonemes", phonemes)

        if (phonemes.length === 0) {
            resultBox.value = 'Gan toradh ó Abair.';
            return;
        }

        //show in box
        resultBox.value = phonemes
            .map(p => `${p.symbol} → ${p.viseme} @ ${p.end.toFixed(2)}s`)
            .join('\n');

        const audioEl = document.getElementById('ttsAudio');
        audioEl.src = data.audioUrl;
        audioEl.load();

        audioEl.oncanplay = () => {
            audioEl.play();
            playVisemes(phonemes, meshesWithMorphs);
        };

    } catch (err) {
        console.error(err);
        resultBox.value = `Earráid: ${err.message}`;
    }
}
