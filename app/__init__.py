import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "routes.login"
login_manager.login_message_category = "info"

def create_app(test_config=None):  # 👈 added optional test_config
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Default configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///habitflow.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 👇 Override config for tests if provided
    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from . import routes
    app.register_blueprint(routes.bp)

    # If testing with SQLite in-memory, create tables automatically
    if test_config and "sqlite:///:memory:" in app.config["SQLALCHEMY_DATABASE_URI"]:
        with app.app_context():
            db.create_all()

    return app
