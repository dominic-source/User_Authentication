from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRESQL_USER = os.environ.get('POSTGRESQL_USER')
POSTGRESQL_PWD = os.environ.get('POSTGRESQL_PWD')
POSTGRESQL_HOST = os.environ.get('POSTGRESQL_HOST')
POSTGRESQL_PORT = os.environ.get('POSTGRESQL_PORT')
POSTGRESQL_DB = os.environ.get('POSTGRESQL_DB')
app = Flask(__name__)

# Set up the secret key for signing sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Setup MySQL server URI
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PWD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}'
)
db = SQLAlchemy(app)
with app.app_context():
    # Create tables
    db.create_all()

@app.route("/", methods=["GET"])
def myapp():
    return "Hello, World!"


if (__name__ == "__main__"):
      # Wrap the Flask app with the ASGI middleware for ASGI compatibility
    app = WsgiToAsgi(app)

    # Run the Flask app using Uvicorn
    import uvicorn
    uvicorn.run(app, host="127.0.0.2", port=5000)