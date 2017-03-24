"""
Extensions
"""

from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


login_manager = LoginManager()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()


extensions = [
    login_manager,
    db,
    mail,
    migrate
]
