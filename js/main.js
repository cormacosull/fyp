import { init, animate } from './three_js.js';
import { submitText, updateAudioModeUI } from './ui_handler.js';

// Initialize Three.js
init();
animate();

// Initialize UI event listeners
document.querySelectorAll('input[name="audioMode"]').forEach(radio => {
    radio.addEventListener('change', updateAudioModeUI);
});

// Ensure correct state on load
updateAudioModeUI();

// Expose submitText to the global scope for the button onclick
window.submitText = submitText;
