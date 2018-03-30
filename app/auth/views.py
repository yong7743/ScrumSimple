from flask import Flask, request, render_template, make_response,send_file
import os,sys
from flask import Flask, render_template, session, redirect, url_for, flash, current_app
from . import auth
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Report, GitHubOauth, WeeklyPlan
from .. import db, github
from datetime import datetime, timedelta
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetForm, ChangeEmailForm


@auth.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('next') or url_for('main.reports')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)
    github_id, github_login, username, email = GitHubOauth.get_user_info(github=github, access_token=oauth_token)
    user = User.query.filter_by(github_id=github_id).first()
    if user is None:
        if username is None:
            username = github_login
        user = User(username=username, email=email, github_id=github_id, github_access_token=oauth_token)
    user.github_access_token = oauth_token
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(request.args.get('next') or url_for('main.reports'))


@auth.route("/login_github", methods=['GET', 'POST'])
def login_github():
    return github.authorize()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    github_id=None, github_access_token=None)
        db.session.add(user)
        db.session.commit()
        flash('You have created the account now.')
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


if __name__ == '__main__':
    pass

