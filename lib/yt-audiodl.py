import requests
from flask import request, jsonify

def register(app):
    @app.route('/download_audio', methods=['GET'])
    def yt_download_audio():
        yt_url = request.args.get('url')
        if not yt_url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        api_endpoint = 'https://two1-9w16.onrender.com/ytmp3'

        try:
            res = requests.get(api_endpoint, params={'url': yt_url}, timeout=15)
            res.raise_for_status()
            data = res.json()

            # Verificar que el enlace de descarga exista
            if not data.get('estado') or 'enlace_descarga' not in data:
                return jsonify({'error': 'No se pudo obtener el enlace de descarga'}), 502

            return jsonify({
                'message': 'Descarga Exitosa',
                'file_url': data['enlace_descarga'],
                'credits' : 'Newton'
            })

        except Exception as e:
            return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500
