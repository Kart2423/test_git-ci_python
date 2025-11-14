from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Импортируем здесь, чтобы избежать циклических импортов
    from app import models
    from app.routes import init_routes

    with app.app_context():
        db.create_all()
        init_routes(app)  # Инициализируем маршруты

    return app