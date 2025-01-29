from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector
from app.prof.forms import NoteForm  # Import du formulaire

prof_bp = Blueprint('prof', __name__)

# Configuration de la connexion MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpassword",
    database="pronote1"
)

# Données statiques pour l'emploi du temps prof
emploi_du_temps_prof = [
    {"jour": "Jeudi", "heure": "08:00 - 10:00", "activité": "Mathématiques"},
    {"jour": "Jeudi", "heure": "10:00 - 12:00", "activité": "Histoire"},
    {"jour": "Dimanche", "heure": "09:00 - 11:00", "activité": "Physique"},
]

@prof_bp.route('/')
def home_page_prof():
    return render_template("home_prof.html")

# Route pour afficher les notes et ajouter une nouvelle note
@prof_bp.route("/notes", methods=["GET", "POST"])
def notes_prof():
    cursor = db.cursor(dictionary=True)

    # Récupérer la liste des élèves
    cursor.execute("SELECT id, nom, prenom FROM eleves ORDER BY nom")
    eleves = cursor.fetchall()

    # Récupérer la liste des matières
    cursor.execute("SELECT id, nom_matiere FROM matieres ORDER BY nom_matiere")
    matieres = cursor.fetchall()

    # Récupérer la liste des notes existantes
    query = """
    SELECT n.id AS note_id, e.nom, e.prenom, m.nom_matiere, n.coef, n.note
    FROM notes n
    JOIN eleves e ON n.eleve_id = e.id
    JOIN matieres m ON n.matiere_id = m.id
    ORDER BY e.nom, m.nom_matiere;
    """
    cursor.execute(query)
    notes = cursor.fetchall()

    # Calcul de la moyenne pondérée
    if notes:
        somme_notes_ponderees = sum(n["note"] * n["coef"] for n in notes)
        somme_coefs = sum(n["coef"] for n in notes)
        moyenne_globale = somme_notes_ponderees / somme_coefs if somme_coefs != 0 else 0
    else:
        moyenne_globale = None

    form = NoteForm()

    # Ajouter les élèves et matières aux listes déroulantes
    form.eleve_id.choices = [(eleve["id"], f"{eleve['nom']} {eleve['prenom']}") for eleve in eleves]
    form.matiere_id.choices = [(matiere["id"], matiere["nom_matiere"]) for matiere in matieres]

    # Ajouter une nouvelle note
    if form.validate_on_submit():
        eleve_id = form.eleve_id.data
        matiere_id = form.matiere_id.data
        note = form.note.data
        coef = form.coef.data

        insert_query = "INSERT INTO notes (eleve_id, matiere_id, note, coef) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (eleve_id, matiere_id, note, coef))
        db.commit()

        flash("Note ajoutée avec succès !", "success")
        return redirect(url_for("prof.notes_prof"))

    cursor.close()
    return render_template("notes_prof.html", notes=notes, form=form, moyenne_globale=moyenne_globale)


# Route pour supprimer une note
@prof_bp.route("/notes/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    cursor = db.cursor()

    delete_query = "DELETE FROM notes WHERE id = %s"
    cursor.execute(delete_query, (note_id,))
    db.commit()

    cursor.close()
    flash("Note supprimée avec succès !", "success")
    return redirect(url_for("prof.notes_prof"))

# Route pour afficher l'emploi du temps prof
@prof_bp.route("/appel")
def appel():
    return render_template("appel.html")

@prof_bp.route("/edt")
def emploi_du_temps_page_prof():
    return render_template("edt_prof.html", emploi=emploi_du_temps_prof)
