import requests
import os
import logging
from pydub import AudioSegment
import io

# ElevenLabs API key should be set as an environment variable
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')

# You can choose a voice ID from ElevenLabs' available voices
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Example voice ID (Rachel)

def generate_audio(text, output_filename):
    try:
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

        # Headers for the API request
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }

        # Data for the API request
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        # Make the API request
        response = requests.post(url, json=data, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Convert the MP3 content to WAV
            audio = AudioSegment.from_mp3(io.BytesIO(response.content))
            
            # Export as WAV
            wav_filename = output_filename.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_filename, format="wav")

            logging.info(f"Audio generated successfully: {wav_filename}")
            return wav_filename
        else:
            logging.error(f"Error generating audio: {response.status_code} - {response.text}")
            raise Exception(f"API request failed with status code {response.status_code}")

    except Exception as e:
        logging.error(f"Error generating audio: {str(e)}")
        raise

    return output_filename
