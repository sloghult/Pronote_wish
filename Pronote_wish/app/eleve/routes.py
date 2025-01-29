from flask import Blueprint, render_template, jsonify

eleve_bp = Blueprint('eleve', __name__)


emploi_du_temps_ele = [
    {"jour": "Lundi", "heure": "08:00 - 10:00", "activité": "Mathématiques"},
    {"jour": "Lundi", "heure": "10:00 - 12:00", "activité": "Histoire"},
    {"jour": "Mardi", "heure": "09:00 - 11:00", "activité": "Physique"},
    # Ajoutez d'autres activités ici
]

@eleve_bp.route('/')
def eleve_home():
    return render_template("home_ele.html")
# Route pour afficher l'emploi du temps élève

@eleve_bp.route("/edt")
def emploi_du_temps_page_ele():
    return render_template("edt_ele.html", emploi=emploi_du_temps_ele)
