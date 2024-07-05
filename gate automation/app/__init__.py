from flask import Flask, current_app, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sse import sse
from flask_login import LoginManager
from os import path
import os


db = SQLAlchemy()
DB_NAME = 'management.db'


def createApp():
    from .models import Admins
    app = Flask(__name__)
    app.config["REDIS_URL"] = "redis://localhost:6379/0"
    app.config['SECRET_KEY'] = 'Al3xandruP0p1ca2ooe'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'routes.home'
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(id):
        return Admins.query.get(int(id))

    from .routes import routes

    app.register_blueprint(routes,  url_prefix='/')
    app.register_blueprint(sse, url_prefix='/stream')

    with app.app_context():
        db.create_all()


    return app


#ConnectDB called function
def connectDB():
    database_url = f'sqlite:///{os.path.join(current_app.instance_path, 'management.db')}'
    engine = create_engine(database_url)

    Session = sessionmaker(bind=engine)
    
    return Session()


def create_database(app):
    if not path.exists(DB_NAME):
        with app.app_context():
            db.create_all()
        print('Database created')

