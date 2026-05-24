const $mic = document.getElementById("mic");
const $form = document.getElementById("form");

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  console.log("getUserMedia supported.");
  $mic.style.display = "inline-block";
} else {
  console.log("getUserMedia not supported on your browser!");
}

function getFormValues() {
    return {
        text: $form.querySelector("[name=text]").value,
        repeat: $form.querySelector("[name=repeat]").checked,
        no_chime: $form.querySelector("[name=no_chime]").checked,
    };
}

function onFormSubmit() {
    var body = getFormValues();
    fetch("say", {
        url: "say",
        method: "POST",
        body: JSON.stringify(body),
        headers: {
            "content-type": "application/json",
        }
    }).catch(err => console.error("POST failed"));
    return false;
}

let mediaRecorder = null;
let playRecording = false;
function onRecord() {
    navigator.mediaDevices.getUserMedia({audio: true})
    .then((stream) => {
        $mic.className = "recording";
        mediaRecorder = new MediaRecorder(stream, {mimeType: "audio/ogg; codecs=opus"});
        mediaRecorder.start();
        console.log("recorder started: ", mediaRecorder.state);
        console.log("tracks: ", stream.getTracks().map(track => track.label))

        let chunks = [];

        mediaRecorder.ondataavailable = (e) => {
            chunks.push(e.data);
        };

        mediaRecorder.onstop = (e) => {
            console.log("recorder stopped");
            $mic.className = "";
            if (playRecording) {
                const blob = new Blob(chunks, { type: "audio/ogg; codecs=opus" });
                const body = new FormData($form);
                body.append("file", blob, "recording.ogg");
                fetch("play", {
                    method: "POST",
                    body,
                });
            }
            chunks = [];
            stream.getTracks().forEach(track => track.stop());
        };
    })
    .catch((err) => {
      console.error(`The following getUserMedia error occurred: ${err}`);
    });
}

function onRecordEnd(playIt) {
    playRecording = playIt;
    mediaRecorder.stop();
}

const $uploadFile = document.getElementById("upload-file");
$uploadFile.onchange = onFileUpload;
function onFileUpload() {
    const file = $uploadFile.files[0];
    const body = new FormData($form);
    body.append("file", file);
    fetch("play", {
        method: "POST",
        body
    });
}
