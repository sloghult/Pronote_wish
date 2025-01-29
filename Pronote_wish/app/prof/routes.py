from flask import Blueprint, render_template, jsonify
import mysql.connector

prof_bp = Blueprint('prof', __name__)

# Configuration de la connexion MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",       # Remplace par ton utilisateur MySQL
    password="rootpassword",       # Remplace par ton mot de passe MySQL
    database="pronote1"   # Nom de la base de données
)



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
    cursor = db.cursor(dictionary=True)
    
    # Requête SQL pour récupérer les notes triées par élève et matière
    query = """
    SELECT e.nom, e.prenom, m.nom_matiere, n.note
    FROM notes n
    JOIN eleves e ON n.eleve_id = e.id
    JOIN matieres m ON n.matiere_id = m.id
    ORDER BY e.nom, m.nom_matiere;
    """
    
    cursor.execute(query)
    notes = cursor.fetchall()
    cursor.close()
    return render_template("notes_prof.html",notes=notes)


# Route pour afficher l'emploi du temps prof
@prof_bp.route("/appel")
def appel():
    return render_template("appel.html")

