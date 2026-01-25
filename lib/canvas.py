from flask import request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import socket
import os
import requests.packages.urllib3.util.connection as urllib3_cn


# =========================
# FORZAR IPv4 (fix red)
# =========================
def allowed_gai_family():
    return socket.AF_INET

urllib3_cn.allowed_gai_family = allowed_gai_family


# =========================
# RUTAS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")


# =========================
# HEADERS HTTP
# =========================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (AlyaBot Image Renderer)",
    "Accept": "image/*"
}


# =========================
# DESCARGA DE IMÁGENES
# =========================
def download_image(url):
    r = requests.get(
        url,
        headers=HEADERS,
        stream=True,
        timeout=15
    )
    r.raise_for_status()
    return Image.open(BytesIO(r.content))


# =========================
# AUTO AJUSTE DE FUENTE
# =========================
def auto_font(draw, text, font_path, max_width, max_size=160, min_size=36):
    size = max_size

    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            return font

        size -= 4

    return ImageFont.truetype(font_path, min_size)


# =========================
# ENDPOINT
# =========================
def register(app):

    @app.route('/canvas', methods=['GET'])
    def render_bye():

        # -------- Parámetros --------
        background_url = request.args.get('background')
        profile_url = request.args.get('profile')

        text = request.args.get('text', 'BYE MEMBER')
        group = request.args.get('group', '')

        font1_name = request.args.get('font', 'BebasNeue-Regular.ttf')
        font2_name = request.args.get('font2', 'Poppins-Bold.ttf')

        glitch = request.args.get('glitch', 'on').lower()

        if not background_url or not profile_url:
            return jsonify({
                "status": False,
                "error": "Faltan parámetros: background o profile"
            }), 400

        font1_path = os.path.join(FONT_DIR, font1_name)
        font2_path = os.path.join(FONT_DIR, font2_name)

        if not os.path.isfile(font1_path):
            return jsonify({"status": False, "error": f"Fuente no encontrada: {font1_name}"}), 400

        if group and not os.path.isfile(font2_path):
            return jsonify({"status": False, "error": f"Fuente no encontrada: {font2_name}"}), 400

        try:
            # =========================
            # FONDO
            # =========================
            bg = download_image(background_url).convert("RGBA")
            bg = bg.resize((1280, 720))

            draw = ImageDraw.Draw(bg)

            center_x = bg.width // 2
            center_y = bg.height // 2

            # =========================
            # TEXTO PRINCIPAL (ARRIBA)
            # =========================
            font_main = auto_font(draw, text, font1_path, max_width=1100)

            text_main_y = center_y - 220

            if glitch == 'on':
                draw.text((center_x + 3, text_main_y), text, font=font_main, fill=(255, 0, 0), anchor="mm")
                draw.text((center_x - 3, text_main_y), text, font=font_main, fill=(0, 255, 255), anchor="mm")

            draw.text(
                (center_x, text_main_y),
                text,
                font=font_main,
                fill=(255, 255, 255),
                anchor="mm"
            )

            # =========================
            # AVATAR (CENTRO)
            # =========================
            avatar = download_image(profile_url).convert("RGBA")
            avatar = avatar.resize((220, 220))

            mask = Image.new("L", avatar.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)
            avatar.putalpha(mask)

            avatar_y = center_y - (avatar.height // 2)

            bg.paste(
                avatar,
                (center_x - avatar.width // 2, avatar_y),
                avatar
            )

            # =========================
            # TEXTO SECUNDARIO (ABAJO)
            # =========================
            if group:
                font_group = auto_font(
                    draw,
                    group,
                    font2_path,
                    max_width=900,
                    max_size=100,
                    min_size=72
                )

                group_y = avatar_y + avatar.height + 70

                draw.text(
                    (center_x, group_y),
                    group,
                    font=font_group,
                    fill=(220, 220, 220),
                    anchor="mm"
                )

            # =========================
            # OUTPUT
            # =========================
            output = BytesIO()
            bg.save(output, format="PNG")
            output.seek(0)

            return send_file(output, mimetype="image/png")

        except Exception as e:
            return jsonify({
                "status": False,
                "error": str(e)
            }), 500