from flask import Blueprint, render_template, jsonify

main = Blueprint('main', __name__)

# Données simulées (vous pouvez les remplacer par une base de données)
students = [
    {
        "id": 1,
        "nom": "Dupont",
        "notes_matiere1": 12,
        "notes_matiere2": 15,
        "notes_matiere3": 14,
        "notes_matiere4": 13,
        "notes_matiere5": 16,
        "prenom": "Jean"
    },
    {
        "id": 2,
        "nom": "Martin",
        "notes_matiere1": 14,
        "notes_matiere2": 13,
        "notes_matiere3": 15,
        "notes_matiere4": 12,
        "notes_matiere5": 10,
        "prenom": "Marie"
    },
    {
        "id": 3,
        "nom": "Durand",
        "notes_matiere1": 17,
        "notes_matiere2": 16,
        "notes_matiere3": 14,
        "notes_matiere4": 18,
        "notes_matiere5": 19,
        "prenom": "Paul"
    }
]

# Route d'accueil
@main.route('/')
def home():
    return "Bienvenue sur l'application Pronote!"

# Route pour afficher la page HTML des étudiants
@main.route('/students')
def students_page():
    return render_template("students.html")

# API JSON pour récupérer les étudiants
@main.route('/api/students')
def get_students():
    return jsonify(students)
