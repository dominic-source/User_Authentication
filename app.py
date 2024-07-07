from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from dotenv import load_dotenv
import os
from database import db

load_dotenv()

class Config: 
    POSTGRESQL_USER = os.environ.get('POSTGRESQL_USER')
    POSTGRESQL_PWD = os.environ.get('POSTGRESQL_PWD')
    POSTGRESQL_HOST = os.environ.get('POSTGRESQL_HOST')
    POSTGRESQL_PORT = os.environ.get('POSTGRESQL_PORT')
    POSTGRESQL_DB = os.environ.get('POSTGRESQL_DB')

    app = Flask(__name__)

    app.config['SESSION_TYPE'] = 'sqlalchemy'

    # Set up the secret key for signing sessions
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    # Setup MySQL server URI
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'postgresql+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PWD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}'
    )

class TestConfig(Config):
    app = Flask(__name__)
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app(test=False):

    if test:
        app = TestConfig.app
        app.config.from_object(TestConfig)
        db.init_app(app)
    else:
        app = Config.app
        app.config.from_object(Config)
        db.init_app(app)
        with app.app_context():
            # Create tables
            db.drop_all()
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
    uvicorn.run(app, host="127.0.0.2", port=5000)
