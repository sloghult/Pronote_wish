from flask import Flask

def create_app():
    app = Flask(__name__)

    # Importer et enregistrer les Blueprints
    from app.admin.routes import admin_bp
    from app.eleve.routes import eleve_bp
    from app.prof.routes import prof_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(eleve_bp, url_prefix='/eleve')
    app.register_blueprint(prof_bp, url_prefix='/prof')

    return app
