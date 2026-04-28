from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)
from flask_login import login_user, logout_user, login_required
from .models import verify_user, register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    lang = session.get("lang", "en")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        lang     = request.form.get("lang", lang)
        session["lang"] = lang

        if not username or not password:
            flash("fill_all", "error")
            return render_template("login.html", lang=lang)

        user = verify_user(username, password)
        if user:
            login_user(user, remember=True)
            return redirect(url_for("main.home"))
        flash("invalid", "error")

    return render_template("login.html", lang=lang)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    lang = session.get("lang", "en")
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username  = request.form.get("username", "").strip()
        password  = request.form.get("password", "").strip()
        lang      = request.form.get("lang", lang)
        session["lang"] = lang

        if not full_name or not username or not password:
            flash("fill_all", "error")
            return render_template("register.html", lang=lang)

        result = register_user(username, password, full_name)
        if result["success"]:
            flash("registered", "success")
            return redirect(url_for("auth.login"))
        flash("user_exists", "error")

    return render_template("register.html", lang=lang)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))