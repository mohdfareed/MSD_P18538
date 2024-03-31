const CHUNK_SIZE = 500; // milliseconds
const CONFIG = {
    audio: {
        sampleRate: 48000,
        sampleSize: 16,
        channelCount: 1
    }
};

let mediaRecorder = null;
let mediaStream = null;

async function record(dotNetReference, callback, configCallback) {
    mediaStream = await navigator.mediaDevices.getUserMedia(CONFIG)
        .then(stream => {
            // log active configuration
            const settings = stream.getAudioTracks()[0].getSettings();
            console.log(settings);

            // send configuration to backend
            dotNetReference.invokeMethodAsync(configCallback,
                settings.sampleRate ?? CONFIG.audio.sampleRate,
                settings.sampleSize ?? CONFIG.audio.sampleSize,
                settings.channelCount ?? CONFIG.audio.channelCount,
            );

            // start recording
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start(CHUNK_SIZE);
            mediaRecorder.ondataavailable = async (e) => {
                const audioData = new Uint8Array(await e.data.arrayBuffer());
                dotNetReference.invokeMethodAsync(callback, audioData);
            };
            console.log("Recording started");
        });
}

function stopRecording() {
    mediaRecorder?.stop();
    mediaRecorder = null;

    mediaStream?.getTracks().forEach(track => track.stop());
    mediaStream = null;

    console.log("Recording stopped");
}
