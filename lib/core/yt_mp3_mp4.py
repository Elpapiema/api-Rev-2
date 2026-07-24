import json
import os
import re
import time

import requests


API_URL = "https://hub.convert1s.com/api/download"
ORIGIN = "https://real-y2mate.com"
REFERER = "https://real-y2mate.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"
YT_REGEX = re.compile(r"(?:youtube\.com/(?:watch\?v=|shorts/|live/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})")
VALID_QUALITIES = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
DEFAULT_QUALITY = "1080p"
DEFAULT_AUDIO_BITRATE = "128k"
POLL_INTERVAL = 2.5
POLL_MAX = 80


def load_env_file():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(base_dir, ".env")
    if not os.path.isfile(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()
YT_CONVERT_DEBUG = os.getenv("YT_CONVERT_DEBUG", "false").lower() in ("1", "true", "yes", "on")


class YoutubeConvertError(Exception):
    pass


def debug_log(message, **values):
    if not YT_CONVERT_DEBUG:
        return

    print(f"[yt-convert] {message}: {values}", flush=True)


def response_preview(response):
    try:
        return response.json()
    except ValueError:
        return response.text[:1000]


def base_headers(extra=None):
    headers = {
        "accept": "application/json",
        "accept-language": "es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7",
        "origin": ORIGIN,
        "referer": REFERER,
        "user-agent": USER_AGENT
    }
    if extra:
        headers.update(extra)
    return headers


def extract_video_id(url):
    match = YT_REGEX.search(str(url or ""))
    return match.group(1) if match else None


def normalize_quality(quality):
    quality = str(quality or "").lower()
    if quality.endswith("p"):
        quality = quality[:-1]
    normalized = f"{quality}p" if quality else DEFAULT_QUALITY
    return normalized if normalized in VALID_QUALITIES else DEFAULT_QUALITY


def format_duration(seconds):
    seconds = max(0, int(seconds or 0))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def build_payload(url, output_type, quality=None, bitrate=DEFAULT_AUDIO_BITRATE):
    payload = {
        "url": url,
        "os": "windows",
        "audio": {"bitrate": bitrate}
    }

    if output_type == "audio":
        payload["output"] = {
            "type": "audio",
            "format": "mp3"
        }
    else:
        payload["output"] = {
            "type": "video",
            "format": "mp4",
            "quality": normalize_quality(quality)
        }

    return payload


def convert(url, output_type="video", quality=DEFAULT_QUALITY, bitrate=DEFAULT_AUDIO_BITRATE):
    video_id = extract_video_id(url)
    if not video_id:
        raise YoutubeConvertError("Enlace de YouTube inválido")

    payload = build_payload(url, output_type, quality, bitrate)
    debug_log(
        "starting conversion",
        video_id=video_id,
        output_type=output_type,
        payload=payload
    )

    response = requests.post(
        API_URL,
        headers=base_headers({"content-type": "application/json"}),
        json=payload,
        timeout=30
    )
    debug_log(
        "initial response",
        status_code=response.status_code,
        body=response_preview(response)
    )
    if not response.ok:
        raise YoutubeConvertError(
            f"El servicio respondió HTTP {response.status_code}: {json.dumps(response_preview(response), ensure_ascii=False)}"
        )

    data = response.json()
    status_url = data.get("statusUrl")
    if not status_url:
        raise YoutubeConvertError(data.get("error") or "No se pudo iniciar la conversión")

    debug_log(
        "polling status",
        status_url=status_url,
        title=data.get("title"),
        selected_quality=data.get("selectedQuality"),
        duration=data.get("duration")
    )

    title = data.get("title") or ""
    for attempt in range(1, POLL_MAX + 1):
        status_response = requests.get(status_url, headers=base_headers(), timeout=30)
        status_body = response_preview(status_response)
        debug_log(
            "status response",
            attempt=attempt,
            status_code=status_response.status_code,
            body=status_body
        )

        if not status_response.ok:
            time.sleep(POLL_INTERVAL)
            continue

        status = status_body
        if not isinstance(status, dict):
            time.sleep(POLL_INTERVAL)
            continue

        title = status.get("title") or title
        current_status = status.get("status")

        if current_status in ("error", "failed"):
            raise YoutubeConvertError(
                status.get("error")
                or status.get("message")
                or f"La conversión falló: {json.dumps(status, ensure_ascii=False)}"
            )

        download_url = status.get("downloadUrl")
        if current_status == "completed" and download_url:
            duration = data.get("duration") or status.get("duration") or 0
            return {
                "video_id": video_id,
                "download_url": download_url,
                "title": title,
                "selected_quality": data.get("selectedQuality") or normalize_quality(quality),
                "duration": duration,
                "duration_formatted": format_duration(duration)
            }

        time.sleep(POLL_INTERVAL)

    raise YoutubeConvertError("La conversión tardó demasiado, intenta de nuevo")
