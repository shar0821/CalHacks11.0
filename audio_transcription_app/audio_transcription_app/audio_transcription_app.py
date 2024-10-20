"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import requests
from rxconfig import config
import os
import pyaudio
from pydub import AudioSegment
import io 
from fastapi import UploadFile
from lib.DeepgramAdapter import DeepgramAdapter
from lib.GeminiAdapter import get_email_summary_and_jira_action_items
from lib.JiraAdapter import extract_issues_and_create_tasks
from lib.emailclient import send_email

async def play_audio(file_path: str):
    chunk = 1024
    # Load the MP3 file
    print(file_path)
    audio = AudioSegment.from_mp3(file_path)
    
    # Convert to raw PCM audio data
    raw_data = audio.raw_data
    
    # Play the audio
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(audio.sample_width),
                    channels=audio.channels,
                    rate=audio.frame_rate,
                    output=True)

    chunk_size = 1024
    data = io.BytesIO(raw_data)
    while True:
        chunk = data.read(chunk_size)
        if not chunk:
            break
        stream.write(chunk)
    
    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()


# @app.api.api_route("/upload_audio", methods=["POST"])
async def upload_audio(file: UploadFile):
    file_path = f"./uploads/{file.filename}"
    # print(file_path)
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    await play_audio(file_path)
    return {"message": "Audio played successfully"}

def generate_transcript(file_path: str):
    # Call the Deepgram API to transcribe the audio file
    # print(file_path)
    transcript = DeepgramAdapter(file_path)
    print('transcript: ', transcript)
    return transcript

def generate_jira_tickets(file_path: str):
    transcript = generate_transcript(file_path)
    summary,output=get_email_summary_and_jira_action_items(transcript)
    generate_sample_code(summary)
    extract_issues_and_create_tasks(output)
    
def generate_sample_code():
    pass

def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )


app = rx.App()
app.add_page(index)
app.api.add_api_route("/upload_audio", upload_audio,methods=["POST"])
app.api.add_api_route("/generate_transcript", generate_transcript,methods=["POST"])