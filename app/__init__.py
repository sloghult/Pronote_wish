from flask import Flask
from app.models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation de la base de données
    db.init_app(app)

    # Importation et enregistrement des Blueprints
    from app.admin.routes import admin_bp
    from app.eleve.routes import eleve_bp
    from app.prof.routes import prof_bp
    from app.auth.routes import auth_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(eleve_bp, url_prefix='/eleve')
    app.register_blueprint(prof_bp, url_prefix='/prof')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
