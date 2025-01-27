from flask import Blueprint

prof_bp = Blueprint('prof', __name__)

@prof_bp.route('/')
def prof_home():
    return "Bienvenue sur la page Prof"
