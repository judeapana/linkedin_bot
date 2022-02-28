import dotenv
from flask import Flask

from linkedin.config import LocalConfig

dotenv.load_dotenv('../.env')


def create_app(conf=LocalConfig):
    app = Flask(__name__)
    app.config.from_object(conf)
    app.register_blueprint(application)
    return app


from linkedin.app import app as application
