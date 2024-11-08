import os
import asyncio
import argparse
import logging
from pathlib import Path
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
from utility.script.script_generator import process_script

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_script_from_file(file_path: str) -> str:
    """Read and return the content of the script file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        logger.error(f"Script file not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading script file: {file_path}. Error: {e}")
        raise

async def generate_video(script: str, video_type: str, output_dir: str) -> str:
    """Generate a video from the given script."""
    try:
        # Process the script
        processed_script = process_script(script, video_type)
        logger.info(f"Script processed. Length: {len(processed_script)} characters")

        # Generate audio
        audio_file = os.path.join(output_dir, "audio_tts.wav")
        await generate_audio(processed_script, audio_file)
        logger.info(f"Audio generated: {audio_file}")

        # Generate timed captions
        timed_captions = generate_timed_captions(audio_file)
        logger.info(f"Timed captions generated: {len(timed_captions)} captions")

        # Generate search terms for background videos
        search_terms = getVideoSearchQueriesTimed(processed_script, timed_captions)
        if not search_terms:
            raise ValueError("No search terms generated for background videos")
        logger.info(f"Search terms generated: {len(search_terms)} terms")

        # Generate background video URLs
        background_video_urls = generate_video_url(search_terms, "pexel")
        if not background_video_urls:
            raise ValueError("No background video URLs generated")
        logger.info(f"Background video URLs generated: {len(background_video_urls)} URLs")

        # Merge empty intervals in background video URLs
        background_video_urls = merge_empty_intervals(background_video_urls)

        # Generate the final video
        output_video = get_output_media(audio_file, timed_captions, background_video_urls, "pexel")
        if not output_video:
            raise ValueError("Failed to generate the final video")
        logger.info(f"Output video generated: {output_video}")

        return output_video

    except Exception as e:
        logger.error(f"An error occurred during video generation: {str(e)}")
        raise

async def main(script_file: str, video_type: str, output_dir: str):
    """Main function to orchestrate the video generation process."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        script = read_script_from_file(script_file)
        logger.info(f"Script read from file: {script[:50]}...")

        output_video = await generate_video(script, video_type, output_dir)
        logger.info(f"Video generation completed. Output: {output_video}")

    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a script file.")
    parser.add_argument("script_file", type=str, help="Path to the script file")
    parser.add_argument("--video_type", type=str, choices=['short', 'long'], default='short', help="Type of video to generate")
    parser.add_argument("--output_dir", type=str, default="output", help="Directory to store output files")

    args = parser.parse_args()

    asyncio.run(main(args.script_file, args.video_type, args.output_dir))
