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

from flask import session, redirect, url_for

@eleve_bp.route("/notes")
def notes_eleve():
    if "user_id" not in session:  # Vérifie si l'utilisateur est connecté
        return "Accès interdit", 403

    user_id = session["user_id"]  # Récupération de l'ID utilisateur depuis la session
    print(f"Utilisateur connecté : {user_id}")  # Debug

    cursor = db.cursor(dictionary=True)

    # Requête pour récupérer l'ID de l'élève à partir de la table users
    query_id_eleve = "SELECT ID_eleve FROM users WHERE id = %s"
    cursor.execute(query_id_eleve, (user_id,))
    result = cursor.fetchone()
    print(f"Résultat de la requête ID_eleve : {result}")  # Debug

    if not result:
        cursor.close()
        return "Utilisateur non trouvé", 404

    id_eleve = result["ID_eleve"]  # Extraction de l'ID de l'élève
    print(f"ID de l'élève trouvé : {id_eleve}")  # Debug

    # Requête SQL pour récupérer uniquement les notes de cet élève
    query_notes = """
    SELECT e.nom, e.prenom, m.nom_matiere, n.note
    FROM notes n
    JOIN eleves e ON n.eleve_id = e.id
    JOIN matieres m ON n.matiere_id = m.id
    WHERE e.id = %s
    ORDER BY m.nom_matiere;
    """

    cursor.execute(query_notes, (id_eleve,))
    notes = cursor.fetchall()
    cursor.close()
    
    return render_template("notes_eleve.html", notes=notes)






# Route pour afficher l'emploi du temps prof
@eleve_bp.route("/abs")
def abs():
    return render_template("abs.html")