import os
import random
from flask import request, jsonify, send_file, after_this_request, url_for
import yt_dlp

DOWNLOAD_FOLDER = '/tmp'
COOKIES_FILE = './auth/cookies.txt'  # Pon la ruta si tienes un archivo cookies.txt

def register(app):
    @app.route('/download_videoV2', methods=['GET'])
    def download_video():
        url = request.args.get('url')

        if not url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        try:
            ydl_opts = {
                'format': 'best[height<=360]',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            }

            if COOKIES_FILE:
                ydl_opts['cookiefile'] = COOKIES_FILE

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Detectar automáticamente el archivo descargado más reciente
                downloaded_files = sorted(
                    os.listdir(DOWNLOAD_FOLDER),
                    key=lambda x: os.path.getctime(os.path.join(DOWNLOAD_FOLDER, x)),
                    reverse=True
                )
                original_filename = downloaded_files[0]

                # Renombrar con ID aleatorio
                new_filename = f"{random.randint(1, 10**10)}.mp4"
                old_path = os.path.join(DOWNLOAD_FOLDER, original_filename)
                new_path = os.path.join(DOWNLOAD_FOLDER, new_filename)

                if old_path != new_path:
                    os.rename(old_path, new_path)

            file_url = url_for('serve_file', filename=new_filename, _external=True)

            return jsonify({
                'message': 'Descarga de video completada',
                'title': info.get('title', 'Desconocido'),
                'duration': info.get('duration', 0),
                'quality': '360p',
                'views': info.get('view_count', 0),
                'likes': info.get('like_count', 0),
                'comments': info.get('comment_count', 0),
                'file_url': file_url
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/download_file/<filename>')
    def serve_file(filename):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404

        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f'Error al eliminar archivo: {e}')
            return response

        return send_file(file_path, as_attachment=True, download_name=filename)
