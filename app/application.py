"""
Application
"""

import locale
import logging
from importlib import import_module
from logging.handlers import RotatingFileHandler
from werkzeug.contrib.fixers import ProxyFix

from flask import Flask

from app.config import app_config
from app.extensions import extensions
from app.extensions import db
from app.urls import modules


def application(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    handler = RotatingFileHandler('app.log')
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Register Blueprints
    for module in modules:
        import_module(module.import_name)
        app.register_blueprint(module)

    # Register extensions
    for ext in extensions:
        ext.init_app(app)

    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    with app.app_context():
        import_module('app.filters')
        db.create_all()
    return app

