import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re
import logging

logger = logging.getLogger(__name__)

def generate_timed_captions(audio_filename: str, model_size: str = "base") -> list:
    """Generate timed captions from an audio file."""
    try:
        whisper_model = load_model(model_size)
        transcription = transcribe_timestamped(whisper_model, audio_filename, verbose=False, fp16=False)
        return get_captions_with_time(transcription)
    except Exception as e:
        logger.error(f"Error generating timed captions: {str(e)}")
        return None

def split_words_by_size(words: list, max_caption_size: int) -> list:
    """Split words into captions of a maximum size."""
    half_caption_size = max_caption_size / 2
    captions = []
    current_caption = []
    current_length = 0

    for word in words:
        word_length = len(word)
        if current_length + word_length + 1 <= max_caption_size:
            current_caption.append(word)
            current_length += word_length + 1
        else:
            if current_length >= half_caption_size or not captions:
                captions.append(' '.join(current_caption))
                current_caption = [word]
                current_length = word_length
            else:
                current_caption.append(word)
                captions.append(' '.join(current_caption))
                current_caption = []
                current_length = 0

    if current_caption:
        captions.append(' '.join(current_caption))

    return captions

def get_timestamp_mapping(whisper_analysis: dict) -> dict:
    """Create a mapping of word positions to timestamps."""
    location_to_timestamp = {}
    index = 0
    for segment in whisper_analysis['segments']:
        for word in segment['words']:
            new_index = index + len(word['text']) + 1
            location_to_timestamp[(index, new_index)] = word['end']
            index = new_index
    return location_to_timestamp

def clean_word(word: str) -> str:
    """Remove non-alphanumeric characters from a word."""
    return re.sub(r'[^\w\s\-_"\'\']', '', word)

def interpolate_time_from_dict(word_position: int, d: dict) -> float:
    """Interpolate the time for a given word position."""
    for key, value in d.items():
        if key[0] <= word_position <= key[1]:
            return value
    return None

def get_captions_with_time(whisper_analysis: dict, max_caption_size: int = 15, consider_punctuation: bool = False) -> list:
    """Generate timed captions from Whisper analysis."""
    try:
        word_location_to_time = get_timestamp_mapping(whisper_analysis)
        position = 0
        start_time = 0
        captions_pairs = []
        text = whisper_analysis['text']
        
        if consider_punctuation:
            sentences = re.split(r'(?<=[.!?]) +', text)
            words = [word for sentence in sentences for word in split_words_by_size(sentence.split(), max_caption_size)]
        else:
            words = text.split()
            words = [clean_word(word) for word in split_words_by_size(words, max_caption_size)]
        
        for word in words:
            position += len(word) + 1
            end_time = interpolate_time_from_dict(position, word_location_to_time)
            if end_time and word:
                captions_pairs.append(((start_time, end_time), word))
                start_time = end_time

        return captions_pairs
    except Exception as e:
        logger.error(f"Error processing captions: {str(e)}")
        return None
