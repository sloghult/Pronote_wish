from flask import Blueprint, render_template, jsonify
from flask import session, redirect, url_for
import mysql.connector
from ..db import get_db  # Importer la fonction get_db

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

@eleve_bp.route("/notes")
def notes_eleve():
    if "user_id" not in session:  # Vérifie si l'utilisateur est connecté
        return "Accès interdit", 403

    user_id = session["user_id"]  # Récupération de l'ID utilisateur depuis la session

    # Utiliser get_db() pour avoir une connexion fraîche
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Récupération de l'ID de l'élève
    query_id_eleve = "SELECT ID_eleve FROM users WHERE id = %s"
    cursor.execute(query_id_eleve, (user_id,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        return "Utilisateur non trouvé", 404

    id_eleve = result["ID_eleve"]  # Extraction de l'ID de l'élève

    try:
        # Récupérer les notes avec coefficients et commentaires
        query_notes = """
        SELECT m.nom_matiere, n.note, n.coef, n.commentaire,
               CASE 
                   WHEN n.commentaire IS NOT NULL AND n.commentaire != '' 
                   THEN n.commentaire 
                   ELSE 'Devoir'
               END as nom_devoir
        FROM notes n
        JOIN matieres m ON n.matiere_id = m.id
        WHERE n.eleve_id = %s
        ORDER BY m.nom_matiere;
        """
        cursor.execute(query_notes, (id_eleve,))
        all_notes = cursor.fetchall()

        # Organiser les notes par matière
        notes_by_matiere = {}
        for note in all_notes:
            matiere = note['nom_matiere']
            if matiere not in notes_by_matiere:
                notes_by_matiere[matiere] = []
            notes_by_matiere[matiere].append(note)

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

        return render_template("notes_eleve.html", notes=notes_by_matiere, moyennes=moyennes, moyenne_globale=moyenne_globale)

    except mysql.connector.Error as err:
        print(f"Erreur MySQL: {err}")
        return "Erreur lors de la récupération des notes", 500

    finally:
        cursor.close()

# Route pour afficher l'emploi du temps prof
@eleve_bp.route("/abs")
def abs():
    return render_template("abs.html")