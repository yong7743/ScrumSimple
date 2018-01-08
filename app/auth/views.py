from flask import Flask, request, render_template, make_response,send_file
import os,sys
from flask import Flask, render_template, session, redirect, url_for, flash, current_app
from . import auth
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Report, GitHubOauth, WeeklyPlan
from .. import db, github
from datetime import datetime, timedelta


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


@auth.route("/login", methods=['GET', 'POST'])
def login():
    return github.authorize()
#    form = LoginForm()
#    if form.validate_on_submit():
#        return github.authorize()
#    return render_template("login.html", form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.reports'))


if __name__ == '__main__':
    pass

