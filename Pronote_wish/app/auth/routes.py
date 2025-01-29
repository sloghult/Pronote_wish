from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.models import db, User
from app.auth.forms import LoginForm
from app.auth import auth_bp  # ✅ Importer auth_bp depuis __init__.py

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:  # Vérification en clair
            login_user(user)
            flash("Connexion réussie", "success")

            # 📌 Correction : Vérifie que les redirections sont bien définies
            if user.role == "admin":
                return redirect(url_for("admin.admin_home"))
            elif user.role == "prof":
                return redirect(url_for("prof.home_page_prof"))
            elif user.role == "eleve":
                return redirect(url_for("eleve.eleve_home"))

        flash("Identifiants invalides", "danger")

    return render_template('login.html', form=form)
