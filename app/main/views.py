from flask import Flask, request, render_template, make_response,send_file
import os,sys
from flask import Flask, render_template, session, redirect, url_for, flash, current_app
from . import main
from .forms import ReportForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Report, GitHubOauth
from .. import db, github


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = ReportForm()
#    if current_user is not None:
#        form.name = current_user.username
    if form.validate_on_submit():
        report = Report(date=form.date.data,
                        body=form.body.data,
                        author=current_user._get_current_object())
        db.session.add(report)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Report.query.order_by(Report.date.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    reports = pagination.items
    return render_template("report.html", form=form, reports=reports, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


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
#    form = LoginForm()
#    if form.validate_on_submit():
#        return github.authorize()
#    return render_template("login.html", form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

if __name__ == '__main__':
    pass

