import os 
import requests
from utility.utils import log_response, LOG_TYPE_PEXEL
import logging
import time
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

PEXELS_API_KEY = os.environ.get('PEXELS_KEY')
MAX_RETRIES = 3
RETRY_DELAY = 2

def search_videos(query_string: str, orientation_landscape: bool = True, page: int = 1) -> Optional[dict]:
    """Search for videos using the Pexels API."""
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15,
        "page": page
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            json_data = response.json()
            log_response(LOG_TYPE_PEXEL, query_string, json_data)
            return json_data
        except requests.RequestException as e:
            logger.error(f"Error in API request (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                logger.error("Max retries reached. Giving up.")
                return None

def getBestVideo(query_string: str, orientation_landscape: bool = True, used_vids: List[str] = [], page: int = 1) -> Optional[str]:
    """Get the best video for a given query string."""
    vids = search_videos(query_string, orientation_landscape, page)
    
    if vids is None or 'videos' not in vids:
        logger.warning(f"No valid response for query: {query_string}")
        return None

    videos = vids['videos']

    if not videos:
        logger.warning(f"No videos found for query: {query_string}")
        return None

    if orientation_landscape:
        filtered_videos = [video for video in videos if video['width'] >= 1920 and video['height'] >= 1080 and video['width']/video['height'] == 16/9]
    else:
        filtered_videos = [video for video in videos if video['width'] >= 1080 and video['height'] >= 1920 and video['height']/video['width'] == 16/9]

    sorted_videos = sorted(filtered_videos, key=lambda x: abs(15-int(x['duration'])))

    for video in sorted_videos:
        for video_file in video['video_files']:
            if orientation_landscape:
                if video_file['width'] == 1920 and video_file['height'] == 1080:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        return video_file['link']
            else:
                if video_file['width'] == 1080 and video_file['height'] == 1920:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        return video_file['link']

    logger.warning(f"No suitable videos found for query: {query_string}")
    return None

def generate_video_url(timed_video_searches: List[Tuple[Tuple[float, float], List[str]]], video_server: str) -> List[Tuple[Tuple[float, float], Optional[str]]]:
    """Generate video URLs for timed video searches."""
    timed_video_urls = []
    if video_server == "pexel":
        used_links = []
        for (t1, t2), search_terms in timed_video_searches:
            url = None
            for page in range(1, 4):  # Try up to 3 pages
                for query in search_terms:
                    url = getBestVideo(query, orientation_landscape=True, used_vids=used_links, page=page)
                    if url:
                        used_links.append(url.split('.hd')[0])
                        break
                if url:
                    break
            timed_video_urls.append(((t1, t2), url))
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)
    else:
        logger.error(f"Unsupported video server: {video_server}")

    return timed_video_urls
