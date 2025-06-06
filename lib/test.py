from flask import jsonify

def register(app):
    @app.route('/hello')
    def hello():
        return jsonify({"message": "Hola desde un modulo externo!"})
