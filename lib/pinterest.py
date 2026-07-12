import requests
from flask import request, jsonify
from urllib.parse import quote


API_KEY = "causa-4148c87379edfd97"


def register(app):

    @app.route('/pinterest', methods=['GET'])
    def pinterest_search():

        query = request.args.get('search')

        if not query:
            return jsonify({
                "error": "Falta el parámetro search"
            }), 400


        try:
            url = (
                "https://rest.apicausas.xyz/api/v1/"
                "buscadores/pinterest"
            )

            params = {
                "apikey": API_KEY,
                "q": query
            }


            headers = {
                "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 Chrome/117 Safari/537.36"
            }


            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=15
            )


            data = response.json()


            if not data.get("status"):
                return jsonify({
                    "error": "La API no devolvió resultados"
                }), 404



            results = []

            for item in data.get("data", [])[:5]:

                results.append({
                    "title": item.get("title"),
                    "image": item.get("image"),
                    "image_small": item.get("image_small"),
                    "link": item.get("link"),
                    "desc": item.get("desc"),
                    "author": item.get("author_username")
                })


            return jsonify({
                "status": True,
                "query": query,
                "total": len(results),
                "results": results
            })


        except requests.exceptions.Timeout:
            return jsonify({
                "error": "Tiempo de espera agotado"
            }), 504


        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 500