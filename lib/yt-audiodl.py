import requests
import random
from flask import request, jsonify

def register(app):
    @app.route('/download_audio', methods=['GET'])
    def yt_download_audio():
        yt_url = request.args.get('url')
        if not yt_url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        # Lista de APIs
        apis = [
            {
                "url": "https://api-adonix.ultraplus.click//download/ytaudio",
                "params": {"apikey": "Yuki-WaBot", "url": yt_url},
                "extract": lambda r: r.get("data", {}).get("url")
            },
            {
                "url": "https://api.zenzxz.my.id/downloader/ytmp3",
                "params": {"url": yt_url},
                "extract": lambda r: r.get("data", {}).get("download_url")
            },
            {
                "url": "https://api.zenzxz.my.id/downloader/ytmp3v2",
                "params": {"url": yt_url},
                "extract": lambda r: r.get("data", {}).get("download_url")
            },
            {
                "url": "https://api.yupra.my.id/api/downloader/ytmp3",
                "params": {"url": yt_url},
                "extract": lambda r: r.get("data", {}).get("download_url")
            },
            {
                "url": "https://api.vreden.web.id/api/v1/download/youtube/audio",
                "params": {"url": yt_url, "quality": "128"},
                "extract": lambda r: r.get("result", {}).get("download", {}).get("url")
            }
        ]

        # Orden aleatorio para el fallback
        random.shuffle(apis)

        # Probar APIs una por una
        for api in apis:
            try:
                res = requests.get(api["url"], params=api["params"], timeout=15)
                res.raise_for_status()
                data = res.json()

                download_link = api["extract"](data)

                # Si existe enlace válido → devolver
                if download_link:
                    return jsonify({
                        'message': 'Descarga Exitosa',
                        'file_url': download_link,
                        'Developed_by': 'Emma Violets Version'
                    })

            except Exception:
                # Ignorar error, intentar siguiente API
                continue

        # Si ninguna API respondió correctamente
        return jsonify({
            'error': 'Error interno al procesar la solicitud',
        }), 502
