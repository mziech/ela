# ELA

A quick & dirty solution to play simple text-to-speech messages on a PA system.

This is using the excellent [Piper](https://github.com/OHF-Voice/piper1-gpl) library for speech synthesis.

## Configuration
The app can be configured using the following environment variables:
| Variable | Description |
|----------|-------------|
| VOICE    | The TTS voice to use, see https://rhasspy.github.io/piper-samples/ for examples, default de_DE-pavoque-low |
| VOICES_DIR | Directory to store the downloaded voice models, default /voices |
| CHIME | Path to a chime to play before each announcement, default [chime.ogg](chime.ogg) |
| OUTPUT_FORMAT | The file format to pass to the output command, can be wav/ogg/mp3, default wav |
| OUTPUT_COMMAND | A shell command to execute to play the announcement, `$FILE` is an env variable containing the temp audio file with the announcement, default `play "$FILE"` |

## Running

With local audio playback (quite fragile):
```shell
docker run -p 8000:8000 --device /dev/snd ghcr.io/mziech/ela
```

With audio playback via [ROC](https://roc-streaming.org/) (installed in the image)
```shell
docker run -ti -p 8000:8000 -e OUTPUT_COMMAND='roc-send -s rtp://pa-host:10000 -i "file://$FILE"' ghcr.io/mziech/ela
```
