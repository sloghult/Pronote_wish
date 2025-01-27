from flask import Blueprint, render_template, redirect, url_for, flash
from app.auth.forms import LoginForm
from flask_login import login_user, logout_user

auth_bp = Blueprint('auth', __name__)

# Route pour la connexion
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Remplacez ceci par une vraie vérification avec une base de données
        if username == "admin" and password == "password":
            flash('Connexion réussie', 'success')
            return redirect(url_for('admin.admin_home'))
        else:
            flash('Identifiants invalides', 'danger')

    return render_template('login.html', form=form)

# Route pour la déconnexion
@auth_bp.route('/logout')
def logout():
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('auth.login'))
