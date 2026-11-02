import os
import inspect
from flask_admin import Admin
from . import models
from .models import db
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    # Flask-Admin no trae autenticación: registra CRUD completo de TODAS
    # las tablas (usuarios incluidos) para quien conozca la URL /admin.
    # Por eso solo se activa en desarrollo (FLASK_DEBUG=1) o a propósito
    # con ENABLE_ADMIN=1. En producción queda deshabilitado.
    if os.environ.get('FLASK_DEBUG') != '1' \
            and os.environ.get('ENABLE_ADMIN') != '1':
        app.logger.info(
            "Flask-Admin deshabilitado: actívalo con FLASK_DEBUG=1 o "
            "ENABLE_ADMIN=1 solo en local.")
        return
    admin = Admin(app, name='4Geeks Admin',
                  theme=Bootstrap4Theme(swatch='cerulean'))

    # Dynamically add all models to the admin interface automatically
    for name, obj in inspect.getmembers(models):
        # Verify that the object is a SQLAlchemy model before adding it to the admin.
        if inspect.isclass(obj) and issubclass(obj, db.Model):
            admin.add_view(ModelView(obj, db.session))
