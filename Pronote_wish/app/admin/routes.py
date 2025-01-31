from flask import Blueprint, render_template, request, redirect, url_for, flash
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

@admin_bp.route('/sup', methods=['GET', 'POST'])
def list_users():
    filter_role = request.form.get('filter_role')
    filter_classe = request.form.get('filter_classe')

    cursor = db.cursor(dictionary=True)
    query = """
    SELECT users.id, users.username, users.email, users.role, 
    IF(users.role = 'eleve', eleves.nom, prof.nom) AS nom, 
    IF(users.role = 'eleve', eleves.prenom, prof.prenom) AS prenom,
    IF(users.role = 'eleve', classes.classe, 
        GROUP_CONCAT(DISTINCT c1.classe, ', ', c2.classe, ', ', c3.classe SEPARATOR ', ')) AS classe
    FROM users
    LEFT JOIN eleves ON users.ID_eleve = eleves.id
    LEFT JOIN prof ON users.id = prof.user_id
    LEFT JOIN classes ON eleves.classe_id = classes.id
    LEFT JOIN classes c1 ON prof.classe1 = c1.id
    LEFT JOIN classes c2 ON prof.classe2 = c2.id
    LEFT JOIN classes c3 ON prof.classe3 = c3.id
    """

    if filter_role:
        query += " WHERE users.role = '{}'".format(filter_role)
        if filter_classe and filter_role == 'eleve':
            query += " AND classes.classe = '{}'".format(filter_classe)
        elif filter_classe and filter_role == 'prof':
            query += " AND (c1.classe = '{}' OR c2.classe = '{}' OR c3.classe = '{}')".format(filter_classe, filter_classe, filter_classe)
    elif filter_classe:
        query += " WHERE (classes.classe = '{}' OR c1.classe = '{}' OR c2.classe = '{}' OR c3.classe = '{}')".format(filter_classe, filter_classe, filter_classe, filter_classe)

    query += " GROUP BY users.id, users.username, users.email, users.role, eleves.nom, prof.nom, eleves.prenom, prof.prenom"
    cursor.execute(query)
    users = cursor.fetchall()

    # Récupérer toutes les classes pour les options du filtre
    cursor.execute("SELECT classe FROM classes")
    classes = cursor.fetchall()

    cursor.close()
    return render_template("sup_user.html", users=users, filter_role=filter_role, filter_classe=filter_classe, classes=classes)

# Route pour afficher la page HTML des étudiants
@admin_bp.route('/students')
def students_page():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM eleves")  
    eleves = cursor.fetchall()
    cursor.close()
    return render_template("students.html", eleves=eleves)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, classe FROM classes")
    classes = [(classe["id"], classe["classe"]) for classe in cursor.fetchall()]
    cursor.execute("SELECT id, nom_matiere FROM matieres")
    matieres = [(matiere["id"], matiere["nom_matiere"]) for matiere in cursor.fetchall()]
    cursor.close()

    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                       (username, email, password, role))
        user_id = cursor.lastrowid

        if role == 'eleve':
            nom = request.form['nom']
            prenom = request.form['prenom']
            classe_id = request.form['classe_id']
            cursor.execute("INSERT INTO eleves (nom, prenom, classe_id) VALUES (%s, %s, %s)",
                           (nom, prenom, classe_id))
            eleve_id = cursor.lastrowid
            cursor.execute("UPDATE users SET ID_eleve = %s WHERE id = %s", (eleve_id, user_id))
        elif role == 'prof':
            nomp = request.form['nomp']
            matiere1 = request.form['matiere1']
            matiere2 = request.form['matiere2']
            matiere3 = request.form['matiere3']
            classe1 = request.form['classe1']
            classe2 = request.form['classe2']
            classe3 = request.form['classe3']
            cursor.execute("INSERT INTO prof (user_id, nom, matiere1, matiere2, matiere3, classe1, classe2, classe3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (user_id, nomp, matiere1, matiere2, matiere3, classe1, classe2, classe3))
        db.commit()
        cursor.close()
        return redirect(url_for('admin.add_user'))
    return render_template('add_user.html', classes=classes, matieres=matieres)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("admin.list_users"))
    if user['role'] == "prof":
        cursor.execute("DELETE FROM prof WHERE user_id = %s", (user_id,))
    elif user['role'] == "eleve":
        cursor.execute("DELETE FROM notes WHERE eleve_id = %s", (user['ID_eleve'],))
        cursor.execute("DELETE FROM eleves WHERE id = %s", (user['ID_eleve'],))
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    flash("Utilisateur supprimé avec succès.", "success")
    return redirect(url_for("admin.list_users"))
