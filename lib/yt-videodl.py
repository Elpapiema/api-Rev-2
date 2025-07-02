import requests
from flask import request, jsonify

def register(app):
    @app.route('/download_video', methods=['GET'])
    def yt_download_neoxr():
        yt_url = request.args.get('url')
        if not yt_url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        api_key = 'GataDios'
        api_endpoint = 'https://api.neoxr.eu/api/youtube'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        }

        params = {
            'url': yt_url,
            'type': 'video',
            'quality': '360p',
            'apikey': api_key
        }

        try:
            res = requests.get(api_endpoint, params=params, headers=headers)
            res.raise_for_status()
            data = res.json()

            if not data.get('status') or 'data' not in data or 'url' not in data['data']:
                return jsonify({'error': 'No se pudo obtener el enlace de descarga'}), 502

            return jsonify({
                'message': 'Descarga Exitosa',
                'download_url': data['data']['url']
            })

        except Exception as e:
            return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500
