import flask_login
from flask import render_template, Blueprint, current_app, session, redirect, flash
from flask_login import current_user


def logout_user(e):
    flash("An internal error occured. You are automatically logged out.", 'warning')
    if current_user.is_authenticated:
        current_app.logger.info(current_user.username + " logged out.")
        session[current_user.id] = None
        flask_login.logout_user()
    return redirect("/login/")

def handle_500(e):
    flash("An internal error occured. You are automatically logged out.", 'warning')
    if current_user.is_authenticated:
        current_app.logger.info(current_user.username + " logged out.")
        session[current_user.id] = None
        flask_login.logout_user()
    return redirect("/login/")