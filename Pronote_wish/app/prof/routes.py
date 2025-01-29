from flask import Blueprint, render_template, jsonify

prof_bp = Blueprint('prof', __name__)

# Données statiques pour l'emploi du temps prof
emploi_du_temps_prof = [
    {"jour": "Jeudi", "heure": "08:00 - 10:00", "activité": "Mathématiques"},
    {"jour": "Jeudi", "heure": "10:00 - 12:00", "activité": "Histoire"},
    {"jour": "Dimanche", "heure": "09:00 - 11:00", "activité": "Physique"},
    # Ajoutez d'autres activités ici
]


@prof_bp.route('/')
def home_page_prof():
    return render_template("home_prof.html")

# Route pour afficher l'emploi du temps prof
@prof_bp.route("/edt")
def emploi_du_temps_page_prof():
    return render_template("edt_prof.html", emploi=emploi_du_temps_prof)

# Route pour afficher l'emploi du temps prof
@prof_bp.route("/notes")
def notes_prof():
    return render_template("notes_prof.html")