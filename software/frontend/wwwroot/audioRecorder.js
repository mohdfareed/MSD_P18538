const CHUNK_SIZE = 100; // milliseconds
let mediaRecorder = null;
let mediaStream = null;

async function startRecording(dotNetReference, callback, configCallback) {
    // enable microphone and ask for permission
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(mediaStream);

    // send config to C# code as a JSON object
    config = mediaStream.getAudioTracks()[0].getSettings()
    dotNetReference.invokeMethodAsync(configCallback, config);

    // send audio data to C# code
    mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
            let arrayBuffer = await event.data.arrayBuffer();
            let audioData = new Uint8Array(arrayBuffer); // audio bytes
            dotNetReference.invokeMethodAsync(callback, audioData)
        }
    };
    // record in chunks of time (milliseconds)
    mediaRecorder.start(CHUNK_SIZE);
}

async function stopRecording() {
    mediaRecorder?.stop();
    mediaStream?.getTracks().forEach(track => track.stop());
}
