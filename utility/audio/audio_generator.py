import edge_tts
import logging
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize

async def generate_audio(text, output_filename):
    try:
        # Use a more expressive voice
        voice = "en-US-AriaNeural"
        
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
    ssml = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-AriaNeural">
            <prosody rate="0.9" pitch="+10%">
                {add_emphasis_and_breaks(text)}
            </prosody>
        </voice>
    </speak>
    """
    return ssml

def add_emphasis_and_breaks(text):
    # Add emphasis to important words and natural breaks
    words = text.split()
    emphasized_text = []
    for i, word in enumerate(words):
        if len(word) > 5 or i % 10 == 0:  # Emphasize longer words or every 10th word
            emphasized_text.append(f'<emphasis level="moderate">{word}</emphasis>')
        else:
            emphasized_text.append(word)
        
        if i % 5 == 4:  # Add a short break every 5 words
            emphasized_text.append('<break time="300ms"/>')
    
    return ' '.join(emphasized_text)

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
