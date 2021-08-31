from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin

from tornado.config import Config
from tornado.admin.routes import MyModelView


db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
admin = Admin()
login_manager = LoginManager()
login_manager.login_view = 'user_login'


def create_app(cofig_class=Config):
    application = Flask(__name__)
    app = application
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    login_manager.init_app(app)

    from tornado.models import (
        User, Profile, Post, 
        PostChild, Comment, Category, 
        Tag)

    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Profile, db.session))
    admin.add_view(MyModelView(Category, db.session))
    admin.add_view(MyModelView(Tag, db.session))
    admin.add_view(MyModelView(Post, db.session))
    admin.add_view(MyModelView(PostChild, db.session))
    admin.add_view(MyModelView(Comment, db.session))
    
    from tornado.accounts.routes import accounts
    from tornado.posts.routes import posts

    app.register_blueprint(accounts)
    app.register_blueprint(posts)

    return app