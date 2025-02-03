from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db
from app.auth.routes import is_admin, login_required
from werkzeug.security import generate_password_hash
import json

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/")
@login_required
def admin_home():
    if not is_admin():
        flash("Accès non autorisé", "danger")
        return redirect(url_for("auth.login"))
    return render_template('admin/admin_home.html')

@admin_bp.route("/users", methods=["GET", "POST"])
def users():
    cursor = get_db().cursor(dictionary=True)
    
    # Récupérer les classes et matières pour les formulaires
    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    cursor.execute("SELECT * FROM matieres")
    matieres = cursor.fetchall()

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")

        if not all([username, email, password, confirm_password, role]):
            flash("Tous les champs sont requis", "danger")
            return redirect(url_for("admin.users"))

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "danger")
            return redirect(url_for("admin.users"))

        # Vérifier si le nom d'utilisateur existe déjà
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("Ce nom d'utilisateur existe déjà", "danger")
            return redirect(url_for("admin.users"))

        # Vérifier si l'email existe déjà
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Cet email est déjà utilisé", "danger")
            return redirect(url_for("admin.users"))

        try:
            # Créer l'utilisateur
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                (username, email, hashed_password, role),
            )
            user_id = cursor.lastrowid

            if role == "prof":
                nom_prof = request.form.get("nom_prof")
                prenom_prof = request.form.get("prenom_prof")
                matiere = request.form.get("matiere")
                matiere2 = request.form.get("matiere2")
                matiere3 = request.form.get("matiere3")
                classe1 = request.form.get("classe1")
                classe2 = request.form.get("classe2")
                classe3 = request.form.get("classe3")

                if not all([nom_prof, prenom_prof, matiere]):
                    get_db().rollback()
                    flash("Le nom, prénom et la matière principale du professeur sont requis", "danger")
                    return redirect(url_for("admin.users"))

                try:
                    cursor.execute(
                        "INSERT INTO prof (user_id, nom, prenom, matiere_id, matiere2_id, matiere3_id, classe1, classe2, classe3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (user_id, nom_prof, prenom_prof, matiere, matiere2, matiere3, classe1, classe2, classe3)
                    )
                except Exception as e:
                    get_db().rollback()
                    if "foreign key constraint" in str(e).lower():
                        flash("Erreur : Une ou plusieurs matières ou classes sélectionnées n'existent pas", "danger")
                    else:
                        flash(f"Erreur lors de l'ajout des informations du professeur : {str(e)}", "danger")
                    return redirect(url_for("admin.users"))

            elif role == "eleve":
                nom_eleve = request.form.get("nom_eleve")
                prenom_eleve = request.form.get("prenom_eleve")
                classe_eleve = request.form.get("classe_eleve")

                if not all([nom_eleve, prenom_eleve, classe_eleve]):
                    get_db().rollback()
                    flash("Le nom, prénom et la classe de l'élève sont requis", "danger")
                    return redirect(url_for("admin.users"))

                try:
                    cursor.execute(
                        "INSERT INTO eleves (nom, prenom, classe_id) VALUES (%s, %s, %s)",
                        (nom_eleve, prenom_eleve, classe_eleve)
                    )
                    eleve_id = cursor.lastrowid
                    cursor.execute(
                        "UPDATE users SET ID_eleve = %s WHERE id = %s",
                        (eleve_id, user_id)
                    )
                except Exception as e:
                    get_db().rollback()
                    if "foreign key constraint" in str(e).lower():
                        flash("Erreur : La classe sélectionnée n'existe pas", "danger")
                    else:
                        flash(f"Erreur lors de l'ajout des informations de l'élève : {str(e)}", "danger")
                    return redirect(url_for("admin.users"))

            get_db().commit()
            if role == "prof":
                flash(f"Le professeur {nom_prof} {prenom_prof} a été ajouté avec succès", "success")
            else:
                flash(f"L'élève {nom_eleve} {prenom_eleve} a été ajouté avec succès", "success")

        except Exception as e:
            get_db().rollback()
            if "Duplicate entry" in str(e):
                if "username" in str(e):
                    flash("Ce nom d'utilisateur est déjà utilisé", "danger")
                elif "email" in str(e):
                    flash("Cet email est déjà utilisé", "danger")
                else:
                    flash("Une erreur est survenue lors de la création de l'utilisateur", "danger")
            else:
                flash(f"Erreur lors de la création de l'utilisateur : {str(e)}", "danger")
        finally:
            cursor.close()
        return redirect(url_for("admin.users"))

    # Récupérer la liste des utilisateurs avec leurs informations détaillées
    query = """
    SELECT 
        users.id,
        users.username,
        users.email,
        users.role,
        COALESCE(eleves.nom, prof.nom) AS nom,
        COALESCE(eleves.prenom, prof.prenom) AS prenom,
        CASE 
            WHEN users.role = 'eleve' THEN classes.classe
            WHEN users.role = 'prof' THEN CONCAT_WS(', ',
                NULLIF(c1.classe, ''),
                NULLIF(c2.classe, ''),
                NULLIF(c3.classe, '')
            )
            ELSE ''
        END AS classe
    FROM users
    LEFT JOIN eleves ON users.ID_eleve = eleves.id
    LEFT JOIN prof ON users.id = prof.user_id
    LEFT JOIN classes ON eleves.classe_id = classes.id
    LEFT JOIN classes c1 ON prof.classe1 = c1.id
    LEFT JOIN classes c2 ON prof.classe2 = c2.id
    LEFT JOIN classes c3 ON prof.classe3 = c3.id
    ORDER BY users.id
    """
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()

    return render_template("admin/users.html", users=users, classes=classes, matieres=matieres)

@admin_bp.route("/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        # Récupérer les informations de l'utilisateur
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash("Utilisateur introuvable", "danger")
            return redirect(url_for("admin.users"))

        # Supprimer les données associées selon le rôle
        if user['role'] == 'prof':
            cursor.execute("DELETE FROM prof WHERE user_id = %s", (user_id,))
        elif user['role'] == 'eleve':
            cursor.execute("DELETE FROM notes WHERE eleve_id = %s", (user['ID_eleve'],))
            cursor.execute("DELETE FROM eleves WHERE id = %s", (user['ID_eleve'],))

        # Supprimer l'utilisateur
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        get_db().commit()
        flash("Utilisateur supprimé avec succès", "success")
    except Exception as e:
        get_db().rollback()
        flash(f"Erreur lors de la suppression de l'utilisateur: {str(e)}", "danger")
    finally:
        cursor.close()
    return redirect(url_for("admin.users"))

# Route pour afficher la page HTML des étudiants
@admin_bp.route('/students')
def students_page():
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("SELECT * FROM eleves")  
    eleves = cursor.fetchall()
    cursor.close()
    return render_template("students.html", eleves=eleves)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    cursor = get_db().cursor(dictionary=True)

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
        cursor = get_db().cursor()
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
        get_db().commit()
        cursor.close()
        return redirect(url_for('admin.add_user'))
    return render_template('add_user.html', classes=classes, matieres=matieres)

@admin_bp.route('/delete_matiere/<int:matiere_id>', methods=['POST'])
def delete_matiere(matiere_id):
    cursor = get_db().cursor()
    cursor.execute("DELETE FROM notes WHERE matiere_id = %s", (matiere_id,))
    cursor.execute("DELETE FROM matieres WHERE id = %s", (matiere_id,))
    get_db().commit()
    cursor.close()
    flash("Matière et notes associées supprimées avec succès.", "success")
    return redirect(url_for("admin.gestion_matieres"))

@admin_bp.route('/classes', methods=['GET', 'POST'])
def classes():
    if request.method == 'POST':
        nom = request.form.get('nom')
        if not nom:
            flash('Le nom de la classe est requis', 'danger')
            return redirect(url_for('admin.classes'))
        
        cursor = get_db().cursor()
        try:
            cursor.execute("INSERT INTO classes (classe) VALUES (%s)", (nom,))
            get_db().commit()
            flash('Classe ajoutée avec succès', 'success')
        except:
            get_db().rollback()
            flash('Erreur lors de l\'ajout de la classe', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('admin.classes'))

    cursor = get_db().cursor(dictionary=True)
    cursor.execute("SELECT classe as nom FROM classes")
    classes = cursor.fetchall()
    cursor.close()
    return render_template('admin/classes.html', classes=classes)

@admin_bp.route('/classes/supprimer/<string:nom>', methods=['POST'])
def supprimer_classe(nom):
    cursor = get_db().cursor()
    try:
        cursor.execute("DELETE FROM classes WHERE classe = %s", (nom,))
        get_db().commit()
        flash('Classe supprimée avec succès', 'success')
    except:
        get_db().rollback()
        flash('Erreur lors de la suppression de la classe', 'danger')
    finally:
        cursor.close()
    return redirect(url_for('admin.classes'))

@admin_bp.route("/gestion_matieres", methods=["GET", "POST"])
def gestion_matieres():
    if request.method == "POST":
        nom_matiere = request.form.get("nom_matiere")
        if not nom_matiere:
            flash("Le nom de la matière est requis", "danger")
            return redirect(url_for("admin.gestion_matieres"))

        cursor = get_db().cursor()
        try:
            cursor.execute("INSERT INTO matieres (nom_matiere) VALUES (%s)", (nom_matiere,))
            get_db().commit()
            flash("Matière ajoutée avec succès", "success")
        except:
            get_db().rollback()
            flash("Erreur lors de l'ajout de la matière", "danger")
        finally:
            cursor.close()
        return redirect(url_for("admin.gestion_matieres"))

    cursor = get_db().cursor(dictionary=True)
    cursor.execute("SELECT * FROM matieres")
    matieres = cursor.fetchall()
    cursor.close()
    return render_template("matieres.html", matieres=matieres)

@admin_bp.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    if not is_admin():
        flash("Accès non autorisé", "danger")
        return redirect(url_for("auth.login"))
        
    cursor = get_db().cursor(dictionary=True)
    
    # Récupérer les classes et matières pour les formulaires
    cursor.execute("SELECT * FROM classes ORDER BY classe")
    classes = cursor.fetchall()
    cursor.execute("SELECT * FROM matieres ORDER BY nom_matiere")
    matieres = cursor.fetchall()
    
    # Récupérer les élèves pour le formulaire d'ajout
    cursor.execute("""
        SELECT e.id, e.nom, e.prenom, c.classe
        FROM eleves e
        JOIN classes c ON e.classe_id = c.id
        ORDER BY c.classe, e.nom, e.prenom
    """)
    eleves = cursor.fetchall()
    
    if request.method == "POST":
        eleve_id = request.form.get("eleve")
        matiere_id = request.form.get("matiere")
        note = request.form.get("note")
        coef = request.form.get("coef")
        commentaire = request.form.get("commentaire")
        
        if not all([eleve_id, matiere_id, note, coef]):
            flash("Tous les champs obligatoires doivent être remplis", "danger")
            return redirect(url_for("admin.notes"))
            
        try:
            cursor.execute(
                "INSERT INTO notes (eleve_id, matiere_id, note, coef, commentaire) VALUES (%s, %s, %s, %s, %s)",
                (eleve_id, matiere_id, note, coef, commentaire)
            )
            get_db().commit()
            flash("Note ajoutée avec succès", "success")
        except Exception as e:
            get_db().rollback()
            flash(f"Erreur lors de l'ajout de la note : {str(e)}", "danger")
        
        return redirect(url_for("admin.notes"))
    
    # Récupérer toutes les notes avec les informations associées
    cursor.execute("""
        SELECT n.id as note_id, n.note, n.coef, n.commentaire,
               e.nom, e.prenom, c.classe,
               m.nom_matiere
        FROM notes n
        JOIN eleves e ON n.eleve_id = e.id
        JOIN classes c ON e.classe_id = c.id
        JOIN matieres m ON n.matiere_id = m.id
        ORDER BY c.classe, e.nom, e.prenom, m.nom_matiere
    """)
    notes = cursor.fetchall()
    
    return render_template("admin/notes.html", notes=notes, classes=classes, matieres=matieres, eleves=eleves)

@admin_bp.route("/get_eleves")
@login_required
def get_eleves():
    if not is_admin():
        return {"error": "Accès refusé"}, 403

    classe_id = request.args.get('classe_id')
    if not classe_id:
        return {"eleves": []}

    cursor = get_db().cursor(dictionary=True)
    
    try:
        # Récupérer les élèves de la classe
        cursor.execute("""
            SELECT id, nom, prenom
            FROM eleves
            WHERE classe_id = %s
            ORDER BY nom, prenom
        """, (classe_id,))
        
        eleves = cursor.fetchall()
        return {"eleves": eleves}
    
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        cursor.close()

@admin_bp.route("/get_eleves_by_classe/<int:classe_id>")
@login_required
def get_eleves_by_classe(classe_id):
    if not is_admin():
        return jsonify({"error": "Non autorisé"}), 403

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Récupérer les élèves de la classe
        cursor.execute("""
            SELECT id, nom, prenom
            FROM eleves
            WHERE classe_id = %s
            ORDER BY nom, prenom
        """, (classe_id,))
        
        eleves = cursor.fetchall()
        return jsonify(eleves)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/saisir_notes_devoir")
@login_required
def saisir_notes_devoir():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    # Récupérer les paramètres
    classe_id = request.args.get('classe_id')
    matiere_id = request.args.get('matiere_id')
    nom_devoir = request.args.get('nom_devoir')
    coefficient = request.args.get('coefficient')

    if not all([classe_id, matiere_id, nom_devoir, coefficient]):
        flash("Tous les champs sont requis", "danger")
        return redirect(url_for('admin.notes'))

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Récupérer les informations de la classe et de la matière
        cursor.execute("""
            SELECT c.classe, m.nom_matiere
            FROM classes c, matieres m
            WHERE c.id = %s AND m.id = %s
        """, (classe_id, matiere_id))
        info = cursor.fetchone()

        # Récupérer la liste des élèves de la classe
        cursor.execute("""
            SELECT id, nom, prenom
            FROM eleves
            WHERE classe_id = %s
            ORDER BY nom, prenom
        """, (classe_id,))
        eleves = cursor.fetchall()

        return render_template('saisie_notes_devoir.html',
                             classe_id=classe_id,
                             matiere_id=matiere_id,
                             nom_devoir=nom_devoir,
                             coefficient=coefficient,
                             classe=info['classe'],
                             matiere=info['nom_matiere'],
                             eleves=eleves,
                             is_admin=True)

    except Exception as e:
        print(f"Erreur complète : {str(e)}")
        flash(f"Erreur : {str(e)}", "danger")
        return redirect(url_for('admin.notes'))

@admin_bp.route("/ajouter_devoir", methods=["POST"])
@login_required
def ajouter_devoir():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Récupérer les informations du devoir
        devoir_info = json.loads(request.form.get('devoir_info'))
        notes = request.form.to_dict()

        # Insérer les notes pour chaque élève
        for key, value in notes.items():
            if key.startswith('notes[') and key.endswith(']'):
                eleve_id = key[6:-1]  # Extraire l'ID de l'élève de notes[X]
                note = value
                
                if note.strip():  # Vérifier que la note n'est pas vide
                    cursor.execute("""
                        INSERT INTO notes (eleve_id, matiere_id, note, coef, commentaire)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        eleve_id,
                        devoir_info['matiere_id'],
                        float(note),
                        int(devoir_info['coefficient']),
                        devoir_info['nom']
                    ))

        db.commit()
        flash("Les notes ont été ajoutées avec succès", "success")
        
    except Exception as e:
        db.rollback()
        flash(f"Erreur lors de l'ajout des notes : {str(e)}", "danger")
        
    return redirect(url_for('admin.notes'))

@admin_bp.route("/notes/delete/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    if not is_admin():
        flash("Accès non autorisé", "danger")
        return redirect(url_for("auth.login"))
    
    try:
        cursor = get_db().cursor()
        # Utiliser le nom de colonne correct pour l'ID
        cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
        get_db().commit()
        flash("Note supprimée avec succès", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression de la note : {str(e)}", "danger")
        get_db().rollback()
    finally:
        cursor.close()
    
    return redirect(url_for("admin.notes"))
