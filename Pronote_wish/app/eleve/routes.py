from flask import Blueprint, render_template, jsonify
import mysql.connector

eleve_bp = Blueprint('eleve', __name__)

# Configuration de la connexion MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",       # Remplace par ton utilisateur MySQL
    password="rootpassword",       # Remplace par ton mot de passe MySQL
    database="pronote1"   # Nom de la base de données
)


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


# Route pour afficher l'emploi du temps prof
@eleve_bp.route("/abs")
def abs():
    return render_template("abs.html")