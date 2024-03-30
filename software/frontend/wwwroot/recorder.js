let mediaRecorder = null;

async function record(dotNetReference, callback) {
    // enable microphone and ask for permission
    await navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const audioTracks = stream.getAudioTracks();
            const trackSettings = audioTracks[0].getSettings();
            console.log('Microphone settings:', trackSettings);

            // const mp4 = { mimeType: 'audio/mp4' };
            // const webm = { mimeType: 'audio/webm' };
            // if (MediaRecorder.isTypeSupported(mp4.mimeType)) {
            //     console.log('Using ' + mp4.mimeType + ' as mimeType');
            //     mediaRecorder = new MediaRecorder(stream, mp4);
            // }
            // else if (MediaRecorder.isTypeSupported(webm.mimeType)) {
            //     console.log('Using ' + webm.mimeType + ' as mimeType');
            //     mediaRecorder = new MediaRecorder(stream, webm);
            // }
            // else {
            //     console.error('No supported mimeType found');
            //     return;
            // }
            mediaRecorder = new MediaRecorder(stream);
            console.log('mimeType:', mediaRecorder);

            mediaRecorder.start(500); // Time slice in milliseconds
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
