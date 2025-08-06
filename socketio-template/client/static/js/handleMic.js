var recordAudio = undefined;
var is_recording = false;
// var onAudioDataAvailable = undefined;

function onStreamAvailable(stream) {
    recordAudio = RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/wav',
        sampleRate: 44100,
        // sampleRate : 96000,
        timeSlice: 1000,
        // used by StereoAudioRecorder
        // the range 22050 to 96000.
        // let us force 16khz recording:
        // desiredSampRate: 16000,
        bufferSize : 512, //1024
        // MediaStreamRecorder, StereoAudioRecorder, WebAssemblyRecorder
        // CanvasRecorder, GifRecorder, WhammyRecorder
        recorderType: StereoAudioRecorder,
        // Dialogflow / STT requires mono audio
        numberOfAudioChannels: 1,
        ondataavailable: onAudioDataAvailable
    });
    
    recordAudio.startRecording();
}

function errorGettingStream(error) {
    console.error(JSON.stringify(error));
}

var userMediaConfig = {
    audio: true
}

function startRecording() {
    is_recording = true;
    navigator.getUserMedia(userMediaConfig, onStreamAvailable, errorGettingStream);
};

stopRecording.onclick = function() {
    // recording stopped
    is_recording = false;
    recordAudio.stopRecording();
};