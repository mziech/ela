import os
import subprocess
from tempfile import mkstemp

from typing import Annotated
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.staticfiles import StaticFiles
from piper import download_voices, PiperVoice
from pathlib import Path
from pydantic import BaseModel, Field
from pydub import AudioSegment
import logging


def load_voice():
    voice_name = os.getenv("VOICE", "de_DE-pavoque-low")
    voices_dir = Path(os.getenv("VOICES_DIR", "./voices"))
    logger.info("Loading voice '%s' to %s", voice_name, voices_dir)
    voices_dir.mkdir(parents=True, exist_ok=True)
    download_voices.download_voice(voice_name, voices_dir, False)
    voice = PiperVoice.load(voices_dir / ("%s.onnx" % voice_name))
    return voice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
voice = load_voice()
app = FastAPI()

def load_chime(no_chime: bool) -> AudioSegment:
    if no_chime:
        return AudioSegment.silent()
    chime_file = os.getenv("CHIME", "chime.ogg")
    if chime_file == "":
        return AudioSegment.empty()
    return AudioSegment.from_file(chime_file) + AudioSegment.silent(500)

class CommonRequest(BaseModel):
    repeat: bool = Field(default=False)
    no_chime: bool = Field(default=False)

class SayRequest(CommonRequest):
    text: str

class PlayRequest(CommonRequest):
    file: UploadFile

@app.post("/say")
def say(body: SayRequest):
    tts = AudioSegment.empty()
    logger.info("Saying: %s" % body.text)
    for chunk in voice.synthesize(body.text):
        tts += AudioSegment(data=chunk.audio_int16_bytes, sample_width=2, channels=1, frame_rate=chunk.sample_rate)

    return handle_common(tts, body)

@app.post("/play")
def play(data: Annotated[PlayRequest, Form(media_type="multipart/form-data")]):
    logger.info("Playing: %s" % data.file.filename)
    return handle_common(AudioSegment.from_file(file=data.file.file), data)

def handle_common(announcement: AudioSegment, options: SayRequest):
    output = load_chime(options.no_chime) + (announcement + AudioSegment.silent(750) + announcement if options.repeat else announcement)
    (fd, tmp) = mkstemp()
    output.export(tmp, os.getenv("OUTPUT_FORMAT", "wav"))
    proc = subprocess.run(os.getenv("OUTPUT_COMMAND", 'play "$FILE"'), capture_output=True, shell=True, env={"FILE": tmp})
    os.unlink(tmp)
    if proc.returncode == 0:
        return {"success": True}
    else:
        logger.error("Playback failed with exit code %d:\nstdout:\n%s\nstderr:\n%s", proc.returncode, proc.stdout, proc.stderr)
        return {"success": False, "error": "Play command failed"}

app.mount("/", StaticFiles(directory=Path(".", "static"), html=True), name="static")
