import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const MODEL_URL = 'https://models.readyplayer.me/6910af3648062250a47e49c1.glb?morphTargets=Oculus%20Visemes';

let scene, camera, renderer, controls;
let meshesWithMorphs = [];
let visemeNames = [];

function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x00AACC);

    camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 0, 1);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(document.getElementById('viewer').clientWidth, window.innerHeight);
    document.getElementById('viewer').appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0, 0);
    controls.update();

    scene.add(new THREE.HemisphereLight(0xffffff, 0x000000, 1.2));
    const loader = new GLTFLoader();
    loader.load(MODEL_URL, (gltf) => {
        const model = gltf.scene;
        scene.add(model);
        model.position.set(0, -0.5, 0);

        gltf.scene.traverse((child) => {
            if ((child.isMesh || child.isSkinnedMesh) && child.morphTargetDictionary) {
                meshesWithMorphs.push(child);
                console.log(`Found mesh with morphs: ${child.name}`);
            }
        });

        if (meshesWithMorphs.length === 0) {
            console.error('No morph-capable meshes found.');
            return;
        }

        const allVisemes = new Set();
        meshesWithMorphs.forEach(mesh => {
            Object.keys(mesh.morphTargetDictionary).forEach(name => allVisemes.add(name));
        });

        visemeNames = Array.from(allVisemes);
        console.log('Viseme names:', visemeNames);
    },
    undefined,
    (err) => console.error('Model load error:', err));

 window.addEventListener('resize', () => {
    camera.aspect = document.getElementById('viewer').clientWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(document.getElementById('viewer').clientWidth, window.innerHeight);
});

}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

export { animate, init, meshesWithMorphs, visemeNames };
