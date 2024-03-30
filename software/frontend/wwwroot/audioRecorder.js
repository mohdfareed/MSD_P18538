const CHUNK_SIZE = 500; // milliseconds
let mediaRecorder = null;

async function record(dotNetReference, callback) {
    await navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start(CHUNK_SIZE);
            mediaRecorder.ondataavailable = async (e) => {
                const audioData = new Uint8Array(await e.data.arrayBuffer());
                dotNetReference.invokeMethodAsync(callback, audioData);
            };
        });
}

function stopRecording() {
    mediaRecorder?.stop();
    mediaRecorder = null;
}
