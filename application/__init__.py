from flask import Flask
from flask_sqlalchemy import SQLAlchemy

"""
Setting up the database
"""
db = SQLAlchemy()

def create_app():
    """
    Function Construct the core application for the flask   
    """
    app = Flask(__name__)
    app.config.from_object('config.Config')
    """
    Initializing the sqlalchemy db with the app
    """
    db.init_app(app)
    """
    Creating the app context
    """
    with app.app_context():
        from . import routes
        db.create_all()
        return app
