import * as THREE from 'three';
import { meshesWithMorphs } from './three_js.js';

function parsePhonemeTiming(data) {
  const phonemeToViseme = {
    'sil': 'viseme_sil',

    'b': 'viseme_PP',
    'bj': 'viseme_PP',
    'p_j': 'viseme_PP',
    'p': 'viseme_PP',
    'mj': 'viseme_PP',
    'm_d': 'viseme_PP',
    'm': 'viseme_PP',

    'f': 'viseme_FF',
    'fj': 'viseme_FF',
    'v': 'viseme_FF',
    'vj': 'viseme_FF',

    'dj': 'viseme_DD',
    'd': 'viseme_DD',
    't': 'viseme_DD',
    'tj': 'viseme_DD',

    'gj': 'viseme_kk',
    'g': 'viseme_kk',
    'k': 'viseme_kk',
    'kj': 'viseme_kk',
    'cj': 'viseme_kk',

    'djzj': 'viseme_CH',
    'sj': 'viseme_CH',

    'zj': 'viseme_SS',
    'z': 'viseme_SS',
    's': 'viseme_SS',

    'l': 'viseme_NN',
    'llj': 'viseme_NN',
    'll': 'viseme_NN',
    'lj_d': 'viseme_NN',
    'll_d': 'viseme_NN',
    'lj': 'viseme_NN',
    'ngj': 'viseme_NN',
    'nn': 'viseme_NN',
    'nnj': 'viseme_NN',
    'n': 'viseme_NN',
    'nj': 'viseme_NN',
    'nn_d': 'viseme_NN',
    'nj_d': 'viseme_NN',
    'ng': 'viseme_NN',
    'llj_d': 'viseme_NN',

    'r_d': 'viseme_RR',
    'rj_d': 'viseme_RR',
    'rj': 'viseme_RR',
    'r': 'viseme_RR',
    'gfj': 'viseme_RR',

    'a': 'viseme_aa',
    'ea': 'viseme_aa',
    'aa': 'viseme_aa',
    'ai': 'viseme_aa',
    'au': 'viseme_aa',

    '@': 'viseme_E',
    'e': 'viseme_E',
    'ee': 'viseme_E',
    'ei': 'viseme_E',

    'gf': 'viseme_I',
    'x': 'viseme_I',
    'xj': 'viseme_I',
    'i': 'viseme_I',
    'ii': 'viseme_I',
    'i@': 'viseme_I',

    'h': 'viseme_O',
    'oo': 'viseme_O',
    'o': 'viseme_O',

    'u': 'viseme_U',
    'u@': 'viseme_U',
    'uu': 'viseme_U',
  };

  const result = [];
  for (const word of data.timing || []) {
    for (const phone of word.phones || []) {
      const symbol = phone.symbol;
      result.push({
        symbol,
        end: phone.end,
        viseme: phonemeToViseme[symbol] || 'mouthOpen'
      });
    }
  }
  return result;
}

function playVisemes(phonemes) {
  if (phonemes.length === 0) return;

  const VIS_OFFSET = -0.075;
  const MAX_BLEND_DURATION = 0.15;

  let startTime = performance.now();
  let currentIndex = 0;

  function update() {
    const now = performance.now();
    const elapsed = (now - startTime) / 1000;

    while (
      currentIndex < phonemes.length - 1 &&
      (phonemes[currentIndex + 1].end + VIS_OFFSET) < elapsed
    ) {
      currentIndex++;
    }

    const current = phonemes[currentIndex];
    const next = phonemes[currentIndex + 1];

    let t = 0;

    if (next) {
      const visemeStart = current.end + VIS_OFFSET;
      const actualDuration = next.end - current.end;
      const blendDuration = Math.min(actualDuration, MAX_BLEND_DURATION);
      const timeIntoBlend = elapsed - visemeStart;
      t = timeIntoBlend / blendDuration;
      t = THREE.MathUtils.clamp(t, 0, 1);
    }

    meshesWithMorphs.forEach(mesh => {
      const inf = mesh.morphTargetInfluences;
      if (!inf) return;
      for (let i = 0; i < inf.length; i++) inf[i] = 0;

      const currentIdx = mesh.morphTargetDictionary[current.viseme];
      if (currentIdx !== undefined) inf[currentIdx] = 1 - t;

      if (next) {
        const nextIdx = mesh.morphTargetDictionary[next.viseme];
        if (nextIdx !== undefined) inf[nextIdx] = t;
      }
    });

    if (currentIndex < phonemes.length - 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}
export {parsePhonemeTiming, playVisemes}