import requests
import random
from flask import request, jsonify

def register(app):
    @app.route('/download_video', methods=['GET'])
    def yt_download_video():
        yt_url = request.args.get('url')
        if not yt_url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        # Lista de APIs con su extractor correspondiente
        apis = [
            {
                "url": "https://api.zenzxz.my.id/downloader/ytmp4",
                "params": {"url": yt_url, "resolution": "360p"},
                "extract": lambda r: r.get("data", {}).get("download_url")
            },
            {
                "url": "https://api.zenzxz.my.id/downloader/ytmp4v2",
                "params": {"url": yt_url, "resolution": "360"},
                "extract": lambda r: r.get("data", {}).get("download_url")
            },
            {
                "url": "https://api.yupra.my.id/api/downloader/ytmp4",
                "params": {"url": yt_url},
                "extract": lambda r: r.get("data", {}).get("download_url")
            },
            {
                "url": "https://api.vreden.web.id/api/v1/download/youtube/video",
                "params": {"url": yt_url, "quality": "360"},
                "extract": lambda r: r.get("result", {}).get("download", {}).get("url")
            }
        ]

        # Mezclar para usar APIs en orden aleatorio
        random.shuffle(apis)

        # Intentar APIs una por una
        for api in apis:
            try:
                res = requests.get(api["url"], params=api["params"], timeout=15)
                res.raise_for_status()
                data = res.json()

                download_link = api["extract"](data)

                if download_link:
                    return jsonify({
                        'message': 'Descarga Exitosa',
                        'file_url': download_link,
                        'Developed_by': 'Emma Violets Version'
                    })

            except Exception:
                # Continuar con la siguiente API si falla
                continue

        # Si todas fallan
        return jsonify({
            'error': 'Error interno al procesar la solicitud'
        }), 502
