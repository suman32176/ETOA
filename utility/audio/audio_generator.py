import edge_tts
import logging
import asyncio
from pydub import AudioSegment
import io
import random

logger = logging.getLogger(__name__)

async def generate_audio(text: str, output_filename: str) -> None:
    """Generate audio from text using edge-tts with enhanced naturalness."""
    try:
        voices = [
            ("en-US-AriaNeural", "cheerful"),
            ("en-US-ChristopherNeural", "friendly"),
            ("en-GB-SoniaNeural", "empathetic"),
            ("en-AU-NatashaNeural", "excited"),
            ("en-CA-ClaraNeural", "calm")
        ]

        voice, style = random.choice(voices)
        sentences = text.split('. ')
        audio_segments = []

        for sentence in sentences:
            rate = random.uniform(0.9, 1.1)
            pitch = random.uniform(-2, 2)

            communicate = edge_tts.Communicate(sentence, voice)
            
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="{voice}">
                    <prosody rate="{rate}" pitch="{pitch}st" style="{style}">
                        {sentence}
                    </prosody>
                </voice>
            </speak>
            """
            
            audio_data = await communicate.synthesize_ssml(ssml)
            audio_segment = AudioSegment.from_wav(io.BytesIO(audio_data))
            audio_segments.append(audio_segment)

        final_audio = sum(audio_segments)
        final_audio.export(output_filename, format="wav")

        logger.info(f"Audio generated successfully with enhanced naturalness: {output_filename}")
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise
