from flask import Flask, request, render_template, make_response,send_file
import os,sys
from flask import Flask, render_template, session, redirect, url_for, flash, current_app
from . import main
from .forms import ReportForm, ScrumForm, WeeklyPlanForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Report, GitHubOauth, WeeklyPlan
from .. import db, github
from .extension.duty_schedule import DutySchedule
import datetime


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@main.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    current_time = datetime.datetime.utcnow()
    form = ReportForm()
    if form.validate_on_submit():
        rpt = Report(date=form.date.data,
                        body=form.body.data,
                        author=current_user._get_current_object())
        db.session.add(rpt)
        return redirect(url_for('.reports'))
    page = request.args.get('page', 1, type=int)
    pagination = Report.query.order_by(Report.date.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    rpts = pagination.items
    return render_template("reports.html", form=form, current_time=current_time, reports=rpts, pagination=pagination)


def get_duty_text():
    # Temp solution for the U.S time zone
    today_date = (datetime.datetime.now() + datetime.timedelta(hours=8)).date()
    dutySchedule = DutySchedule("e:/team-status/app/main/extension/member.json", datetime.date(2018, 2, 19))
    duty_name = dutySchedule.get_member_onduty(today_date)
    members_name = dutySchedule.get_members()
    text = duty_name + "! o(*￣︶￣*)o ~~~~ Orders:" + ', '.join(members_name)
    return text


@main.route('/weeklys', methods=['GET', 'POST'])
@login_required
def weeklys():
    form = WeeklyPlanForm()
    if form.validate_on_submit():
        report = WeeklyPlan(date=form.date.data,
                        body=form.body.data,
                        author=current_user._get_current_object())
        db.session.add(report)
        return redirect(url_for('.weeklys'))
    page = request.args.get('page', 1, type=int)
    pagination = WeeklyPlan.query.order_by(WeeklyPlan.date.desc()).paginate(
        page, per_page=12,
        error_out=False)
    wlps = pagination.items
    text = ""
    try:
        text = get_duty_text()
    except ValueError:
        print(ValueError)

    return render_template("weekly_home.html", form=form, current_time=text, weeklys=wlps, pagination=pagination)


@main.route('/help', methods=['GET', 'POST'])
def help():
    return render_template("help.html")


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
        start = datetime.datetime.strptime(session['start'], '%d/%m/%Y')
        start = start - datetime.timedelta(days = 1)
        end = datetime.datetime.strptime(session['end'], '%d/%m/%Y')
        header = "Scrums form %s to %s" % (session['start'],session['end'] )
        pagination = Report.query.filter(
            Report.date.between(start, end)).order_by(Report.author_id.asc(), Report.date.asc()).paginate(
        page, per_page=100,#current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
        scrums = pagination.items
#        session.pop('start', None)
#        session.pop('end', None)
    return render_template("scrum.html", form=form, scrums=scrums, header=header, pagination=pagination)


def report_filter(reports, start, end):
    current = Report.query.filter(Report.date.between(start, end)).order_by(Report.date.desc(), Report.author_id.desc())
    return current


@main.route('/users', methods=['GET', 'POST'])
def users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.username.asc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template("users.html", users=users, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    usr = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = usr.reports.order_by(Report.date.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    rpts = pagination.items

    wpls = WeeklyPlan.query.filter_by(author_id=usr.id).order_by(WeeklyPlan.date.desc()).all()
    wpln_index = min(2, len(wpls))
    wpls = wpls[:wpln_index]
    return render_template('user.html', user=usr, reports=rpts, weeklys = wpls,
                           pagination=pagination)


@main.route('/report/<int:id>')
def report(id):
    report = Report.query.get_or_404(id)
    return render_template('report.html', reports=[report])


@main.route('/weeklyplan/<int:id>')
def weekly_plan(id):
    report = WeeklyPlan.query.get_or_404(id)
    return render_template('weekly_plan.html', reports=[report])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    report = Report.query.get_or_404(id)
    if current_user != report.author and not current_user.is_administrator():
        return "Not allow! Only current user and administrator can edit it"
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


@main.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    report = Report.query.get_or_404(id)
    if current_user != report.author and not current_user.is_administrator():
        return "Not allow! Only current user and administrator can delete it"
    else:
        form = ReportForm()
        db.session.delete(report)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('main.reports'))


@main.route('/weeklyedit/<int:id>', methods=['GET', 'POST'])
@login_required
def weekly_edit(id):
    report = WeeklyPlan.query.get_or_404(id)
    if current_user != report.author:
        return "Not allow!"
    form = WeeklyPlanForm()
    if form.validate_on_submit():
        report.body = form.body.data
        report.date = form.date.data
        db.session.add(report)
        flash('The post has been updated.')
        return redirect(url_for('.weeklys', id=report.id))
    form.body.data = report.body
    form.date.data = report.date
    return render_template('edit_weekly.html', form=form)


@main.route('/weeklydelete/<int:id>', methods=['GET', 'POST'])
@login_required
def weekly_delete(id):
    report = WeeklyPlan.query.get_or_404(id)
    if current_user != report.author:
        return "Not allow!"
    else:
        db.session.delete(report)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('main.weeklys'))


if __name__ == '__main__':
    pass

