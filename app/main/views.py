from flask import Flask, request, render_template, make_response,send_file
import os,sys
from flask import Flask, render_template, session, redirect, url_for, flash
from . import main
from .forms import ReportForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Report, GitHubOauth
from .. import db, github



@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = ReportForm()
    if current_user is not None:
        form.name = current_user.username
    if form.validate_on_submit():
        report = Report(date=form.date.data,
                        body=form.body.data,
                        author=current_user._get_current_object())
        db.session.add(report)
        return redirect(url_for('.index'))
    return render_template("report.html", form=form)


@main.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('.next') or url_for('.index')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)
    username, email = GitHubOauth.get_user_info(github=github, access_token=oauth_token)
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(username=username, email=email, github_access_token=oauth_token)
    user.github_access_token = oauth_token
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(request.args.get('next') or url_for('main.index'))


@main.route("/login", methods=['GET', 'POST'])
def login():
    return github.authorize()


@main.route("/login_normal", methods=['GET', 'POST'])
def login_normal():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User(username=form.username.data)
            db.session.add(user)
            db.session.commit()
        login_user(user, form.remember_me.data)
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template("login.html", form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

if __name__ == '__main__':
    pass

