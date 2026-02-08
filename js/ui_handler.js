import { playVisemes, parsePhonemeTiming } from './viseme_logic.js';
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

    if (mode === 'wav') {
        const fileInput = document.getElementById('wavInput');
        const file = fileInput.files[0];

        if (!file) {
            alert('Roghnaigh comhad WAV.');
            return;
        }

        resultBox.value = 'Ag próiseáil WAV...';

        const audioEl = document.getElementById('ttsAudio');
        audioEl.src = URL.createObjectURL(file);
        audioEl.load();

        audioEl.oncanplay = async () => {
            audioEl.play();
        };
        return;
    }

    const text = document.getElementById('sentenceInput').value.trim();

    if (!text) {
        alert('Cuir isteach abairt ar dtús.');
        return;
    }

    resultBox.value = 'Ag seoladh...';

    try {
        const response = await fetch('http://127.0.0.1:5000/timing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        const phonemes = parsePhonemeTiming(data);

        if (phonemes.length === 0) {
            resultBox.value = 'Gan toradh ó Abair.';
            return;
        }

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
