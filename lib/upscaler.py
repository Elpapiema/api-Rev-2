from flask import request, send_file
from PIL import Image
import io

def register(app):
    @app.route("/upscale", methods=["POST"])
    def upscale():
        if "image" not in request.files:
            return {"error": "No se envió ninguna imagen"}, 400

        # Obtener la imagen subida
        file = request.files["image"]
        try:
            img = Image.open(file)
        except Exception as e:
            return {"error": f"Error al abrir la imagen: {str(e)}"}, 400

        # Escalar al doble
        width, height = img.size
        new_size = (width * 2, height * 2)
        img_upscaled = img.resize(new_size, Image.LANCZOS)

        # Guardar en buffer de memoria
        img_bytes = io.BytesIO()
        img_upscaled.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Devolver la imagen escalada como respuesta
        return send_file(img_bytes, mimetype="image/png")
