import os
from flask import Flask, request, jsonify, send_from_directory, render_template_string

UPLOAD_FOLDER = './auth'
API_KEY = 'alyabot2025'  # Reemplaza esto por tu clave

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def register(app):
    @app.route('/auth', methods=['POST'])
    def upload_cookies():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Falta la cabecera Authorization con Bearer token'}), 401
        
        token = auth_header.split()[1]
        if token != API_KEY:
            return jsonify({'error': 'API key inválida'}), 403

        file = request.files.get('cookies')
        if not file or file.filename == '':
            return jsonify({'error': 'No se proporcionó ningún archivo'}), 400

        if not file.filename.endswith('.txt'):
            return jsonify({'error': 'Solo se permiten archivos .txt'}), 400

        save_path = os.path.join(UPLOAD_FOLDER, 'cookies.txt')
        file.save(save_path)
        return jsonify({'message': 'Archivo subido correctamente'}), 200

    @app.route('/upload-cookies', methods=['GET'])
    def upload_form():
        html_form = """
        <!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Subir cookies.txt</title>
  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #1f1c2c, #928dab);
      color: #fff;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }

    .container {
      background-color: rgba(0, 0, 0, 0.7);
      padding: 40px;
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      width: 100%;
      max-width: 400px;
      text-align: center;
    }

    h2 {
      margin-bottom: 20px;
      font-size: 24px;
    }

    input[type="file"],
    input[type="text"] {
      width: 100%;
      padding: 10px;
      margin: 10px 0;
      border: none;
      border-radius: 8px;
    }

    input[type="text"] {
      background-color: #2d2a3e;
      color: #fff;
    }

    input[type="file"] {
      background-color: #2d2a3e;
      color: #ccc;
    }

    button {
      background-color: #5e60ce;
      color: #fff;
      border: none;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }

    button:hover {
      background-color: #6930c3;
    }

    #response {
      margin-top: 20px;
      white-space: pre-wrap;
      background-color: #1e1e2e;
      padding: 10px;
      border-radius: 8px;
      font-size: 14px;
      color: #a3a3ff;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Subir archivo de cookies</h2>
    <form id="uploadForm" enctype="multipart/form-data">
      <input type="file" name="cookies" accept=".txt" required>
      <input type="text" name="apikey" id="apikey" placeholder="API Key" required>
      <button type="submit">Subir</button>
    </form>
    <p id="response"></p>
  </div>

  <script>
    document.getElementById('uploadForm').addEventListener('submit', async function (e) {
      e.preventDefault();
      const form = new FormData();
      const fileInput = document.querySelector('input[name="cookies"]');
      const apiKey = document.getElementById('apikey').value;

      if (!fileInput.files.length) {
        alert('Selecciona un archivo.');
        return;
      }

      form.append('cookies', fileInput.files[0]);

      try {
        const response = await fetch('/auth', {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ' + apiKey
          },
          body: form
        });

        const result = await response.json();
        document.getElementById('response').textContent = JSON.stringify(result, null, 2);
      } catch (err) {
        document.getElementById('response').textContent = 'Error: ' + err;
      }
    });
  </script>
</body>
</html>

        """
        return render_template_string(html_form)
