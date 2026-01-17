import requests
import random
from flask import request, jsonify

def register(app):
    @app.route('/download_audio', methods=['GET'])
    def yt_download_audio():
        yt_url = request.args.get('url')
        if not yt_url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        apis = [
            {
                "name": "Ootaizumi Play",
                "url": "https://api.ootaizumi.web.id/downloader/youtube/play",
                "params": {"query": yt_url},
                "extract": lambda r: r.get("result", {}).get("download")
            },
            {
                "name": "Vreden YT Audio 256",
                "url": "https://api.vreden.web.id/api/v1/download/youtube/audio",
                "params": {"url": yt_url, "quality": "256"},
                "extract": lambda r: r.get("result", {}).get("download", {}).get("url")
            },
            {
                "name": "StellarWA YTMP3",
                "url": "https://api.stellarwa.xyz/dl/ytmp3",
                "params": {"url": yt_url, "quality": "256", "key": "Destroy"},
                "extract": lambda r: r.get("data", {}).get("dl")
            },
            {
                "name": "Ootaizumi MP3",
                "url": "https://api.ootaizumi.web.id/downloader/youtube",
                "params": {"url": yt_url, "format": "mp3"},
                "extract": lambda r: r.get("result", {}).get("download")
            },
            {
                "name": "Vreden Play Audio",
                "url": "https://api.vreden.web.id/api/v1/download/play/audio",
                "params": {"query": yt_url},
                "extract": lambda r: r.get("result", {}).get("download", {}).get("url")
            },
            {
                "name": "Nekolabs MP3",
                "url": "https://api.nekolabs.web.id/downloader/youtube/v1",
                "params": {"url": yt_url, "format": "mp3"},
                "extract": lambda r: r.get("result", {}).get("downloadUrl")
            },
            {
                "name": "Nekolabs Play",
                "url": "https://api.nekolabs.web.id/downloader/youtube/play/v1",
                "params": {"q": yt_url},
                "extract": lambda r: r.get("result", {}).get("downloadUrl")
            }
        ]

        random.shuffle(apis)

        errores = []

        for api in apis:
            try:
                res = requests.get(api["url"], params=api["params"], timeout=15)
                data = res.json()

                download_link = api["extract"](data)
                if download_link:
                    return jsonify({
                        'message': 'Descarga Exitosa',
                        'file_url': download_link,
                        'Developed_by': 'Emma Violets Version'
                    })

                errores.append({
                    "api": api["name"],
                    "status": res.status_code,
                    "data": data
                })

            except Exception as e:
                errores.append({"api": api["name"], "error": str(e)})

        return jsonify({
            'error': 'Error interno al procesar la solicitud',
            'fallos': errores
        }), 502
