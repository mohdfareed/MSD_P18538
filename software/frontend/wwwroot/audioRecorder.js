const CHUNK_SIZE = 500; // milliseconds
const CONFIG = {
    audio: {
        sampleRate: 48000,
        sampleSize: 16,
        channelCount: 1
    }
};
let mediaRecorder = null;

async function record(dotNetReference, callback) {
    await navigator.mediaDevices.getUserMedia(CONFIG)
        .then(stream => {
            // log active configuration
            console.log(stream.getAudioTracks()[0].getSettings());

            // start recording
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
