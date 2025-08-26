"""# plugins/upscale_opencv.py
from flask import request, send_file
import cv2
from cv2 import dnn_superres
import io
import numpy as np

# Cargar modelo pre-entrenado (ejemplo: EDSR)
sr = dnn_superres.DnnSuperResImpl_create()
sr.readModel("EDSR_x2.pb")
sr.setModel("edsr", 2)

def register(app):
    @app.route("/upscale2", methods=["POST"])
    def upscale_opencv():
        if "image" not in request.files:
            return {"error": "No se envió ninguna imagen"}, 400

        file = request.files["image"]
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        result = sr.upsample(img)
        _, buf = cv2.imencode(".png", result)
        return send_file(io.BytesIO(buf), mimetype="image/png")
"""

# plugins/upscale_opencv.py
from flask import request, send_file
import cv2
from cv2 import dnn_superres
import io
import numpy as np
import os
import requests

MODEL_URL = "https://github.com/Saafke/EDSR_Tensorflow/raw/refs/heads/master/models/EDSR_x2.pb"
MODEL_PATH = "EDSR_x2.pb"

# Descargar automáticamente el modelo si no existe
if not os.path.exists(MODEL_PATH):
    print(f"Descargando modelo desde {MODEL_URL}...")
    response = requests.get(MODEL_URL, stream=True)
    with open(MODEL_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("Modelo descargado correctamente.")

# Cargar modelo pre-entrenado
sr = dnn_superres.DnnSuperResImpl_create()
sr.readModel(MODEL_PATH)
sr.setModel("edsr", 2)

def register(app):
    @app.route("/upscale2", methods=["POST"])
    def upscale_opencv():
        if "image" not in request.files:
            return {"error": "No se envió ninguna imagen"}, 400

        file = request.files["image"]
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        result = sr.upsample(img)
        _, buf = cv2.imencode(".png", result)

        return send_file(io.BytesIO(buf), mimetype="image/png")
