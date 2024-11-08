import os
import tempfile
import platform
import subprocess
from moviepy.editor import (AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip, concatenate_videoclips)
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# ... (keep the existing imports and helper functions)

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server):
    OUTPUT_FILE_NAME = "rendered_video.mp4"
    magick_path = get_program_path("magick")
    logging.info(f"ImageMagick path: {magick_path}")
    if magick_path:
        os.environ['IMAGEMAGICK_BINARY'] = magick_path
    else:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
    
    visual_clips = []
    
    def process_video(item):
        (t1, t2), video_url = item
        if video_url:
            video_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            if download_file(video_url, video_filename):
                try:
                    video_clip = VideoFileClip(video_filename).subclip(0, t2-t1)
                    video_clip = video_clip.set_start(t1).set_end(t2)
                    return video_clip
                except Exception as e:
                    logging.error(f"Error processing video clip: {str(e)}")
            else:
                logging.warning(f"Failed to download video from {video_url}")
        return None
    
    with ThreadPoolExecutor() as executor:
        future_to_video = {executor.submit(process_video, item): item for item in background_video_data}
        for future in as_completed(future_to_video):
            video_clip = future.result()
            if video_clip:
                visual_clips.append(video_clip)
    
    try:
        audio_clip = AudioFileClip(audio_file_path)
    except Exception as e:
        logging.error(f"Error loading audio file: {str(e)}")
        return None

    for (t1, t2), text in timed_captions:
        try:
            text_clip = TextClip(txt=text, fontsize=40, color="white", stroke_width=2, stroke_color="black", method='caption', size=(1920, 200))
            text_clip = text_clip.set_start(t1).set_end(t2).set_position(('center', 'bottom'))
            visual_clips.append(text_clip)
        except Exception as e:
            logging.error(f"Error creating text clip: {str(e)}")

    try:
        video = CompositeVideoClip(visual_clips, size=(1920, 1080))
        video = video.set_audio(audio_clip)
        video = video.set_duration(audio_clip.duration)

        video.write_videofile(OUTPUT_FILE_NAME, codec='libx264', audio_codec='aac', fps=30, threads=4, logger=None)
    except Exception as e:
        logging.error(f"Error rendering final video: {str(e)}")
        return None
    
    # Clean up downloaded files
    for clip in visual_clips:
        if isinstance(clip, VideoFileClip) and os.path.exists(clip.filename):
            os.remove(clip.filename)

    return OUTPUT_FILE_NAME

# ... (keep the existing combine_video_segments function)
