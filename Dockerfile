FROM python:3.14-trixie

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libavcodec-extra libasound2-dev portaudio19-dev roc-toolkit-tools sox
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ADD . /app
ADD .devcontainer/asound.conf /etc/asound.conf
VOLUME /voices
ENV VOICES_DIR=/voices

RUN useradd app && usermod -aG audio app && mkdir -p /voices && chown app /app /voices

USER app
EXPOSE 8000
CMD ["fastapi", "run", "main.py", "--port", "8000"]
