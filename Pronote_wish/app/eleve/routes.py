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

    cursor = db.cursor(dictionary=True)

    # Récupération de l'ID de l'élève
    query_id_eleve = "SELECT ID_eleve FROM users WHERE id = %s"
    cursor.execute(query_id_eleve, (user_id,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        return "Utilisateur non trouvé", 404

    id_eleve = result["ID_eleve"]  # Extraction de l'ID de l'élève

    # Récupérer les notes avec coefficients
    query_notes = """
    SELECT m.nom_matiere, n.note, n.coef
    FROM notes n
    JOIN matieres m ON n.matiere_id = m.id
    WHERE n.eleve_id = %s
    ORDER BY m.nom_matiere;
    """
    cursor.execute(query_notes, (id_eleve,))
    notes = cursor.fetchall()

    # Calculer la moyenne par matière (déjà correct)
    query_moyennes = """
    SELECT m.nom_matiere, 
    SUM(n.note * n.coef) / SUM(n.coef) AS moyenne
    FROM notes n
    JOIN matieres m ON n.matiere_id = m.id
    WHERE n.eleve_id = %s
    GROUP BY m.nom_matiere;
    """
    cursor.execute(query_moyennes, (id_eleve,))
    moyennes = cursor.fetchall()

    # Calculer la moyenne globale sans coefficient (nouvelle requête)
    query_moyenne_globale = """
    SELECT AVG(moyenne) AS moyenne_globale
    FROM (
    SELECT SUM(n.note * n.coef) / SUM(n.coef) AS moyenne
    FROM notes n
    JOIN matieres m ON n.matiere_id = m.id
    WHERE n.eleve_id = %s
    GROUP BY m.nom_matiere
    ) AS sous_requete;
    """
    cursor.execute(query_moyenne_globale, (id_eleve,))
    moyenne_globale_result = cursor.fetchone()

    #   Vérifier si la moyenne globale est None (si l'élève n'a pas de notes)
    moyenne_globale = moyenne_globale_result["moyenne_globale"] if moyenne_globale_result and moyenne_globale_result["moyenne_globale"] is not None else 0

    cursor.close()

    return render_template("notes_eleve.html", notes=notes, moyennes=moyennes, moyenne_globale=moyenne_globale)






# Route pour afficher l'emploi du temps prof
@eleve_bp.route("/abs")
def abs():
    return render_template("abs.html")