print('Iniciando...')

from gunicorn.app.base import BaseApplication

from gunicorn import util

import os

APP_MODULE = os.getenv("FLASK_APP", "api2:app")

class GunicornApp(BaseApplication):

    def __init__(self, app_uri, options=None):

        self.options = options or {}

        self.application = util.import_app(app_uri)  # ✅ IMPORTA LA APP REAL

        super().__init__()

    def load_config(self):

        for key, value in self.options.items():

            if key in self.cfg.settings and value is not None:

                self.cfg.set(key, value)

    def load(self):

        return self.application  # ✅ WSGI callable real

if __name__ == "__main__":

    options = {

        "bind": "0.0.0.0:5416",

        "workers": 2,

        "threads": 2,

        "worker_class": "gthread",

        "timeout": 30,

        "loglevel": "info",

        "accesslog": "-",

        "errorlog": "-",

    }

    GunicornApp(APP_MODULE, options).run()