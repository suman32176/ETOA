import os
import asyncio
import argparse
import logging
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_script_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        logging.error(f"Script file not found: {file_path}")
        raise
    except IOError:
        logging.error(f"Error reading script file: {file_path}")
        raise

async def main(script_file, video_type):
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"

    try:
        # Read the script from the file
        script = read_script_from_file(script_file)
        logging.info(f"Script read from file: {script[:50]}...")

        # Generate audio from the script with improved quality and emotion
        await generate_audio(script, SAMPLE_FILE_NAME)
        logging.info(f"Audio generated with improved quality and emotion: {SAMPLE_FILE_NAME}")

        # Generate timed captions
        timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
        logging.info(f"Timed captions generated: {len(timed_captions)} captions")

        # Generate search terms for background videos
        search_terms = getVideoSearchQueriesTimed(script, timed_captions)
        logging.info(f"Search terms generated: {len(search_terms) if search_terms else 0} terms")

        # Generate background video URLs
        background_video_urls = None
        if search_terms is not None:
            background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
            logging.info(f"Background video URLs generated: {len(background_video_urls) if background_video_urls else 0} URLs")
        else:
            logging.warning("No background video search terms generated")

        # Merge empty intervals in background video URLs
        background_video_urls = merge_empty_intervals(background_video_urls)

        # Generate the final video with subtitles at the bottom
        if background_video_urls is not None:
            video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
            logging.info(f"Output video generated with improved audio and subtitles at the bottom: {video}")
        else:
            logging.warning("No video generated due to lack of background videos")

    except Exception as e:
        logging.error(f"An error occurred during video generation: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a script file with improved audio and subtitles.")
    parser.add_argument("script_file", type=str, help="Path to the script file (script.txt)")
    parser.add_argument("--video_type", type=str, choices=['short', 'long'], default='short', help="Type of video to generate")

    args = parser.parse_args()

    try:
        asyncio.run(main(args.script_file, args.video_type))
    except Exception as e:
        logging.error(f"Video generation failed: {str(e)}")
