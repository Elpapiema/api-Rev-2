import os
from flask import Flask, send_from_directory, jsonify, request

import importlib.util

app = Flask(__name__)

# Ruta para servir archivos estáticos desde /web
@app.route('/')
def index():
    return send_from_directory('web', 'index2.html')

# Cargar dinámicamente los endpoints desde /lib
def load_endpoints():
    lib_dir = os.path.join(os.path.dirname(__file__), 'lib')
    if not os.path.isdir(lib_dir):
        return
    for fname in os.listdir(lib_dir):
        if fname.endswith('.py') and not fname.startswith('_'):
            module_path = os.path.join(lib_dir, fname)
            module_name = f'lib.{fname[:-3]}'
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'register'):
                module.register(app)

# Endpoint de ejemplo para descargar archivos desde /tmp
@app.route('/download/<path:filename>')
def download_file(filename):
    tmp_dir = '/tmp'
    return send_from_directory(tmp_dir, filename, as_attachment=True)

# Inicializar
if __name__ == '__main__':
    load_endpoints()
    app.run(debug=True, port=3269, host='0.0.0.0')