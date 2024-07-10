from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from dotenv import load_dotenv
import os
from database import db
# from flask_migrate import Migrate

load_dotenv()
PORT = os.environ.get('PORT')

class Config: 
    POSTGRESQL_USER = os.environ.get('POSTGRESQL_USER')
    POSTGRESQL_PWD = os.environ.get('POSTGRESQL_PWD')
    POSTGRESQL_HOST = os.environ.get('POSTGRESQL_HOST')
    POSTGRESQL_PORT = os.environ.get('POSTGRESQL_PORT')
    POSTGRESQL_DB = os.environ.get('POSTGRESQL_DB')
    POSTGRESQL_URL = os.environ.get('POSTGRESQL_URL')

    SESSION_TYPE = 'sqlalchemy'

    # Set up the secret key for signing sessions
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PWD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}'
    ) if POSTGRESQL_URL == 'None' else POSTGRESQL_URL

    # Setup MySQL server URI
    # SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://SG-same-weaver-228-5724-pgsql-master.servers.mongodirector.com:5432/authdatabase"

class TestConfig():
    TESTING = True
    # Set up the secret key for signing sessions
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app(test=False):
    app = Flask(__name__)
    if test:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
    db.init_app(app)
    from models import User

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    from views import app_views
    app.register_blueprint(app_views)
    # Wrap the Flask app with the ASGI middleware for ASGI compatibility
    app = WsgiToAsgi(app)

    # Run the Flask app using Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
