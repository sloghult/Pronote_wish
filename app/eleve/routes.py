from flask import Blueprint

eleve_bp = Blueprint('eleve', __name__)

@eleve_bp.route('/')
def eleve_home():
    return "Bienvenue sur la page Élève"
