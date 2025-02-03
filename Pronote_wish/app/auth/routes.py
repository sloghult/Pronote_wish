from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from app.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash
import logging

auth_bp = Blueprint("auth", __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Veuillez vous connecter pour accéder à cette page", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def is_admin():
    return session.get("is_admin", False)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        logger.info(f"Tentative de connexion pour l'utilisateur: {username}")
        
        if not username or not password:
            flash("Veuillez remplir tous les champs", "danger")
            return render_template("login.html")
        
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            
            # Vérifier si c'est un admin
            cursor.execute("""
                SELECT id, username, password, role 
                FROM users 
                WHERE username = %s AND role = 'admin'
            """, (username,))
            user = cursor.fetchone()
            
            if user:
                logger.info(f"Utilisateur admin trouvé: {user}")
                stored_password = user.get('password', '')
                
                # Vérification temporaire : accepte les mots de passe non hashés
                if password == stored_password:
                    logger.info("Mot de passe admin correct (non hashé)")
                    session.clear()
                    session["user_id"] = user["id"]
                    session["username"] = user["username"]
                    session["is_admin"] = True
                    logger.info(f"Session après connexion admin: {session}")
                    cursor.close()
                    return redirect(url_for("admin.admin_home"))
            
            # Si ce n'est pas un admin, vérifier si c'est un professeur
            cursor.execute("""
                SELECT u.id as user_id, u.username, u.password, p.id as prof_id
                FROM users u
                JOIN prof p ON u.id = p.user_id
                WHERE u.username = %s AND u.role = 'prof'
            """, (username,))
            prof = cursor.fetchone()
            
            if prof:
                logger.info(f"Professeur trouvé: {prof}")
                stored_password = prof.get('password', '')
                
                # Vérification temporaire : accepte les mots de passe non hashés
                if password == stored_password:
                    logger.info("Mot de passe prof correct (non hashé)")
                    session.clear()
                    session["user_id"] = prof["user_id"]
                    session["username"] = prof["username"]
                    session["is_admin"] = False
                    session["is_prof"] = True
                    session["prof_id"] = prof["prof_id"]
                    logger.info(f"Session après connexion prof: {session}")
                    cursor.close()
                    return redirect(url_for("prof.notes_prof"))
            
            # Si ce n'est pas un prof, vérifier si c'est un élève
            cursor.execute("""
                SELECT u.id as user_id, u.username, u.password, e.id as eleve_id
                FROM users u
                JOIN eleves e ON u.ID_eleve = e.id
                WHERE u.username = %s AND u.role = 'eleve'
            """, (username,))
            eleve = cursor.fetchone()
            
            if eleve:
                logger.info(f"Élève trouvé: {eleve}")
                stored_password = eleve.get('password', '')
                
                # Vérification temporaire : accepte les mots de passe non hashés
                if password == stored_password:
                    logger.info("Mot de passe élève correct (non hashé)")
                    session.clear()
                    session["user_id"] = eleve["user_id"]
                    session["username"] = eleve["username"]
                    session["is_admin"] = False
                    session["eleve_id"] = eleve["eleve_id"]
                    logger.info(f"Session après connexion élève: {session}")
                    cursor.close()
                    return redirect(url_for("eleve.eleve_home"))
            
            flash("Nom d'utilisateur ou mot de passe incorrect", "danger")
            cursor.close()
            logger.warning("Échec de la connexion: utilisateur non trouvé ou mot de passe incorrect")
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {str(e)}")
            flash("Une erreur est survenue lors de la connexion", "danger")
            return render_template("login.html")
    
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/hash_password/<password>")
def hash_password(password):
    hashed = generate_password_hash(password)
    return {"hash": hashed}
