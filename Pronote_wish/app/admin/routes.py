from flask import Blueprint, render_template
import mysql.connector

admin_bp = Blueprint('admin', __name__)

# Configuration de la connexion MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",       # Remplace par ton utilisateur MySQL
    password="rootpassword",       # Remplace par ton mot de passe MySQL
    database="pronote1"   # Nom de la base de données
)

@admin_bp.route('/')
def admin_home():
    return render_template("home_admin.html")

# Route pour afficher la page HTML des étudiants
@admin_bp.route('/students')
def students_page():
    cursor = db.cursor(dictionary=True)  # Récupération des résultats sous forme de dictionnaire
    cursor.execute("SELECT * FROM eleves")  
    eleves = cursor.fetchall()
    cursor.close()
    return render_template("students.html", eleves=eleves)