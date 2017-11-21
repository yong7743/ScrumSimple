from flask import Flask, request, render_template, make_response,send_file
import os,sys
from flask import Flask, render_template, session, redirect, url_for, flash, current_app
from . import main
from .forms import ReportForm, LoginForm, ScrumForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Report, GitHubOauth
from .. import db, github
from datetime import datetime, timedelta


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = ReportForm()
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
    return render_template("index.html", form=form, reports=reports, pagination=pagination)


@main.route('/scrum', methods=['GET', 'POST'])
@login_required
def scrum():
    form = ScrumForm()
    if form.validate_on_submit():
        start = form.start.data
        end = form.end.data
        session['start'] = "%s/%s/%s" % (start.day, start.month, start.year)
        session['end'] = "%s/%s/%s" % (end.day, end.month, end.year)
        return redirect(url_for('.scrum'))
    scrums = []
    pagination = None
    header=None
    page = request.args.get('page', 1, type=int)
    if 'start' in session and 'end' in session:
        #Wed, 01 Nov 2017 00:00:00 GM
        start = datetime.strptime(session['start'], '%d/%m/%Y')
        start = start - timedelta(days = 1)
        end = datetime.strptime(session['end'], '%d/%m/%Y')
        header = "Scrums form %s to %s" % (session['start'],session['end'] )
        pagination = Report.query.filter(Report.date.between(start, end)).order_by(Report.author_id.desc(), Report.date.desc()).paginate(
        #page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        page, per_page=100,
        error_out=False)
        scrums = pagination.items
        test = Report.query.filter(Report.date.between(start, end)).all()
        session.pop('start', None)
        session.pop('end', None)
    return render_template("scrum.html", form=form, scrums=scrums, header=header, pagination=pagination)


def report_filter(reports, start, end):
    current = Report.query.filter(Report.date.between(start, end)).order_by(Report.date.desc(), Report.author_id.desc())
    return current


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.reports.order_by(Report.date.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    reports = pagination.items
    return render_template('user.html', user=user, reports=reports,
                           pagination=pagination)


@main.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('.next') or url_for('.index')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)
    github_id, github_login, username, email = GitHubOauth.get_user_info(github=github, access_token=oauth_token)
    user = User.query.filter_by(github_id=github_id).first()
    if user is None:
        if username is None:
            username = login
        user = User(username=username, email=email, github_access_token=oauth_token)
    user.github_access_token = oauth_token
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(request.args.get('next') or url_for('main.index'))


@main.route('/report/<int:id>')
def report(id):
    report = Report.query.get_or_404(id)
    return render_template('report.html', reports=[report])


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


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    report = Report.query.get_or_404(id)
    if current_user != report.author:
        return "Not allow!"
    form = ReportForm()
    if form.validate_on_submit():
        report.body = form.body.data
        report.date = form.date.data
        db.session.add(report)
        flash('The post has been updated.')
        return redirect(url_for('.report', id=report.id))
    form.body.data = report.body
    form.date.data = report.date
    return render_template('edit_report.html', form=form)

if __name__ == '__main__':
    pass

