import os
import sys

from flask import jsonify, request


CORE_DIR = os.path.join(os.path.dirname(__file__), "core")
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

from yt_mp3_mp4 import YoutubeConvertError, convert


def register(app):
    @app.route('/download_audio', methods=['GET'])
    def yt_download_audio():
        yt_url = request.args.get('url')
        bitrate = request.args.get('bitrate', '128k')

        if not yt_url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        try:
            result = convert(yt_url, output_type="audio", bitrate=bitrate)
            return jsonify({
                'message': 'Descarga Exitosa',
                'file_url': result['download_url'],
                'title': result['title'],
                'duration': result['duration'],
                'duration_formatted': result['duration_formatted'],
                'video_id': result['video_id'],
                'Developed_by': 'Emma Violets Version'
            })
        except YoutubeConvertError as error:
            return jsonify({'error': str(error)}), 502
        except Exception as error:
            return jsonify({'error': f'Error interno al procesar la solicitud: {str(error)}'}), 500
