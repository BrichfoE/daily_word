from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from wotd.config import Config


db = SQLAlchemy()
flask_bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    flask_bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from wotd.main.routes import main
    from wotd.admin.routes import admins
    from wotd.words.routes import words
    from wotd.users.routes import users
    app.register_blueprint(main)
    app.register_blueprint(admins)
    app.register_blueprint(words)
    app.register_blueprint(users)

    return app
