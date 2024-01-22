const CHUNK_SIZE = 1000; // milliseconds
let mediaRecorder = null;
let mediaStream = null;
var config = { // REVIEW: must match MicConfig model class
    sample_rate: 48000,
    sample_width: 16,
    num_channels: 1,
};

async function startRecording(dotNetReference, callback, configCallback) {

    // enable microphone and ask for permission
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(mediaStream);
    settings = mediaStream.getAudioTracks()[0].getSettings();

    // config.sample_rate = settings.sampleRate;
    // config.sample_width = settings.sampleSize;
    // config.num_channels = settings.channelCount;

    // send audio config to C# code
    console.log(mediaStream.getAudioTracks()[0].getSettings());
    console.log(config);
    let json_config = JSON.stringify(config);
    dotNetReference.invokeMethodAsync(configCallback, json_config);

    // send audio data to C# code
    mediaRecorder.ondataavailable = async (event) => {
        const blob = event.data;
        console.log(blob);

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
    mediaRecorder = null;
    mediaStream = null;
}
