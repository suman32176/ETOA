import edge_tts
import logging
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize
import random

async def generate_audio(text, output_filename):
    try:
        # Use a more expressive voice
        voices = ["en-US-AriaNeural", "en-US-ChristopherNeural", "en-GB-SoniaNeural", "en-AU-NatashaNeural"]
        voice = random.choice(voices)
        
        # Add SSML tags for emotion and emphasis
        ssml_text = add_ssml_tags(text)
        
        communicate = edge_tts.Communicate(ssml_text, voice)
        await communicate.save(output_filename)
        
        # Enhance audio quality
        enhance_audio_quality(output_filename)
        
        logging.info(f"Audio generated successfully with emotion: {output_filename}")
    except Exception as e:
        logging.error(f"Error generating audio: {str(e)}")
        raise

def add_ssml_tags(text):
    # Add SSML tags for emotion and emphasis
    sentences = text.split('. ')
    ssml_sentences = []
    
    for sentence in sentences:
        emotion = random.choice(["excited", "cheerful", "sad", "angry", "calm"])
        rate = random.uniform(0.9, 1.1)
        pitch = random.uniform(-10, 10)
        
        ssml_sentence = f"""
        <prosody rate="{rate}" pitch="{pitch}%">
            <mstts:express-as style="{emotion}">
                {sentence}.
            </mstts:express-as>
        </prosody>
        """
        ssml_sentences.append(ssml_sentence)
    
    ssml = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
        <voice name="en-US-AriaNeural">
            {''.join(ssml_sentences)}
        </voice>
    </speak>
    """
    return ssml

def enhance_audio_quality(audio_file):
    # Load the audio file
    audio = AudioSegment.from_wav(audio_file)
    
    # Normalize the audio
    audio = normalize(audio)
    
    # Apply compression to reduce dynamic range
    audio = compress_dynamic_range(audio)
    
    # Add a subtle reverb effect
    reverb = audio.reverb(reverberance=20, hf_damping=50, room_scale=50, stereo_depth=50)
    audio = audio.overlay(reverb, gain_during_overlay=-6)
    
    # Export the enhanced audio
    audio.export(audio_file, format="wav")
