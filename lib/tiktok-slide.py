import requests
from bs4 import BeautifulSoup
from flask import request, jsonify

def register(app):
    @app.route('/Tiktok_slidesdl', methods=['GET'])
    def tiktok_slides_download():
        url = request.args.get('url')

        if not url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        panda = "y1g4rhhYToTA"
        panda2 = "G32254GLM09MN89Maa"

        urls = [
            f"https://dlpanda.com/?url={url}&t0ken={panda}",
            f"https://dlpanda.com/?url={url}&t0ken51={panda2}"
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept': 'text/html'
        }

        img_urls = []

        for source_url in urls:
            try:
                response = requests.get(source_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                images = soup.select('div.col-md-12 > img')

                for img in images:
                    src = img.get('src')
                    if src:
                        img_urls.append(src)

                if img_urls:
                    break

            except Exception as e:
                print(f"Error al intentar con {source_url}: {e}")

        if not img_urls:
            return jsonify({'error': 'No se pudieron obtener imágenes. Verifica que el enlace sea válido y en modo presentación.'}), 400

        return jsonify({
            'message': 'Imágenes extraídas exitosamente.',
            'slides': img_urls
        })
