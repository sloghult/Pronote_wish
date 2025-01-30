from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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

    cursor.execute("SELECT id FROM prof WHERE user_id = %s", (session.get("user_id"),))
    prof_data = cursor.fetchone()

    prof_id = prof_data["id"] if prof_data else None  # Récupère l'ID du prof ou None si non trouvé

    
    if not prof_id:
        flash("Accès refusé.", "danger")
        return redirect(url_for("auth.login"))

    # Récupérer les classes et matières enseignées par le prof
    cursor.execute("SELECT classe1, classe2, classe3, matiere1, matiere2, matiere3 FROM prof WHERE id = %s", (prof_id,))
    prof_data = cursor.fetchone()

    if not prof_data:  # Vérifier si le professeur existe
        flash("Erreur : Professeur introuvable.", "danger")
        return redirect(url_for("auth.login"))

    # Récupérer les classes et matières si elles existent
    classes_autorisees = [prof_data[key] for key in ['classe1', 'classe2', 'classe3'] if prof_data.get(key)]
    matieres_autorisees = [prof_data[key] for key in ['matiere1', 'matiere2', 'matiere3'] if prof_data.get(key)]

    if not classes_autorisees:
        flash("Vous n'avez pas de classe attribuée.", "warning")
        return redirect(url_for("prof.home_page_prof"))

    # Récupérer les élèves des classes enseignées
    placeholders = ", ".join(["%s"] * len(classes_autorisees))
    cursor.execute(f"SELECT id, nom, prenom FROM eleves WHERE classe_id IN ({placeholders})", tuple(classes_autorisees))
    eleves = cursor.fetchall()

    # Récupérer les matières enseignées
    if matieres_autorisees:
        placeholders = ", ".join(["%s"] * len(matieres_autorisees))
        cursor.execute(f"SELECT id, nom_matiere FROM matieres WHERE id IN ({placeholders})", tuple(matieres_autorisees))
        matieres = cursor.fetchall()
    else:
        matieres = []

    # Filtrer les notes visibles par le prof
    if classes_autorisees and matieres_autorisees:
        query = f"""
        SELECT n.id AS note_id, e.nom, e.prenom, m.nom_matiere, n.coef, n.note
        FROM notes n
        JOIN eleves e ON n.eleve_id = e.id
        JOIN matieres m ON n.matiere_id = m.id
        WHERE e.classe_id IN ({", ".join(["%s"] * len(classes_autorisees))}) 
        AND m.id IN ({", ".join(["%s"] * len(matieres_autorisees))})
        ORDER BY e.nom, m.nom_matiere;
        """
        cursor.execute(query, tuple(classes_autorisees + matieres_autorisees))
        notes = cursor.fetchall()
    else:
        notes = []

    form = NoteForm()
    form.eleve_id.choices = [(eleve["id"], f"{eleve['nom']} {eleve['prenom']}") for eleve in eleves]
    form.matiere_id.choices = [(matiere["id"], matiere["nom_matiere"]) for matiere in matieres]

    if form.validate_on_submit():
        eleve_id = form.eleve_id.data
        matiere_id = form.matiere_id.data
        note = form.note.data
        coef = form.coef.data

        # Vérifier que l'élève et la matière sont bien autorisés
        if any(eleve_id == e['id'] for e in eleves) and any(matiere_id == m['id'] for m in matieres):
            cursor.execute("INSERT INTO notes (eleve_id, matiere_id, note, coef) VALUES (%s, %s, %s, %s)",
                           (eleve_id, matiere_id, note, coef))
            db.commit()
            flash("Note ajoutée avec succès !", "success")
        else:
            flash("Accès refusé : Vous ne pouvez pas ajouter une note pour cet élève ou cette matière.", "danger")
        
        return redirect(url_for("prof.notes_prof"))
    
    cursor.close()
    return render_template("notes_prof.html", notes=notes, form=form)

# Route pour supprimer une note
@prof_bp.route("/notes/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
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
    print("Session actuelle:", session)
    return render_template("edt_prof.html", emploi=emploi_du_temps_prof)
