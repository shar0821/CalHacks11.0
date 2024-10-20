
import os
from dotenv import load_dotenv
import logging
from deepgram.utils import verboselogs
from datetime import datetime
import httpx

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    PrerecordedOptions,
    FileSource,
)

load_dotenv()

# AUDIO_FILE = "test.mp3"
API_KEY = os.getenv("DG_API_KEY")


def DeepgramAdapter(AUDIO_FILE):
    try:
        # STEP 1 Create a Deepgram client using the API key in the environment variables
        config: DeepgramClientOptions = DeepgramClientOptions(
            verbose=verboselogs.SPAM,
        )
        deepgram: DeepgramClient = DeepgramClient(API_KEY, config)
        # OR use defaults
        # deepgram: DeepgramClient = DeepgramClient()

        # STEP 2 Call the transcribe_file method on the rest class
        current_path = os.getcwd()
        print("Current working directory:", current_path)

        with open(f"{os.getcwd()}/uploads/{AUDIO_FILE}", "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }
        options: PrerecordedOptions = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            utterances=True,
            punctuate=True,
            diarize=True,
        )

        before = datetime.now()
        response = deepgram.listen.rest.v("1").transcribe_file(
            payload, options, timeout=httpx.Timeout(300.0, connect=10.0)
        )
        after = datetime.now()

        # STEP 3 Print the response
        print(response.text)
        print(response.to_json(indent=4))
        print("")
        difference = after - before
        print(f"time: {difference.seconds}")

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    DeepgramAdapter('test.mp3')

