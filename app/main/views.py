from flask import Flask, request, render_template, make_response,send_file
import os,sys
from flask import Flask, render_template, session, redirect, url_for, flash, current_app
from . import main
from .forms import ReportForm, LoginForm, ScrumForm
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Report, GitHubOauth, Todo
from .. import db, github
from datetime import datetime, timedelta

import rethinkdb as r
import json
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from flask import abort, request, g, jsonify

RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
TODO_DB = 'todoapp'

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    current_time = datetime.utcnow()
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
    return render_template("index.html", form=form, current_time=current_time, reports=reports, pagination=pagination)


@main.route('/help', methods=['GET', 'POST'])
def help():
    return render_template("help.html")


@main.route('/users', methods=['GET', 'POST'])
def users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.username.asc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template("users.html", users=users, pagination=pagination)


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
        pagination = Report.query.filter(
            Report.date.between(start, end)).order_by(Report.author_id.asc(), Report.date.asc()).paginate(
        page, per_page=100,#current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
        scrums = pagination.items
#        session.pop('start', None)
#        session.pop('end', None)
    return render_template("scrum.html", form=form, scrums=scrums, header=header, pagination=pagination)


# @main.route('/todos', methdos=['GET', 'POST'])
# @login_required
# def get_todos():
#     selection = list(r.table('todos').run(g.rdb_conn))
#     return json.dumps(selection)


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
        user = User(username=username, email=email, github_id=github_id, github_access_token=oauth_token)
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


# @main.before_request
# def before_request():
#     try:
#         g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT, db=TODO_DB)
#     except RqlDriverError:
#         abort(503, "No database connection could be established.")
#
#
# @main.teardown_request
# def teardown_request(exception):
#     try:
#         g.rdb_conn.close()
#     except AttributeError:
#         pass
#
# #### Listing existing todos
#
# # To retrieve all existing tasks, we are using
# # [`r.table`](http://www.rethinkdb.com/api/python/table/)
# # command to query the database in response to a GET request from the
# # browser. When `table(table_name)` isn't followed by an additional
# # command, it returns all documents in the table.
# #
# # Running the query returns an iterator that automatically streams
# # data from the server in efficient batches.
# @main.route("/todos", methods=['GET'])
# def get_todos():
#     selection = list(r.table('todos').run(g.rdb_conn))
#     return json.dumps(selection)
#
# #### Creating a todo
#
# # We will create a new todo in response to a POST request to `/todos`
# # with a JSON payload using
# # [`table.insert`](http://www.rethinkdb.com/api/python/insert/).
# #
# # The `insert` operation returns a single object specifying the number
# # of successfully created objects and their corresponding IDs:
# #
# # ```
# # {
# #   "inserted": 1,
# #   "errors": 0,
# #   "generated_keys": [
# #     "773666ac-841a-44dc-97b7-b6f3931e9b9f"
# #   ]
# # }
# # ```
#
# @main.route("/todos", methods=['POST'])
# def new_todo():
#     inserted = r.table('todos').insert(request.json).run(g.rdb_conn)
#     return jsonify(id=inserted['generated_keys'][0])
#
#
# #### Retrieving a single todo
#
# # Every new task gets assigned a unique ID. The browser can retrieve
# # a specific task by GETing `/todos/<todo_id>`. To query the database
# # for a single document by its ID, we use the
# # [`get`](http://www.rethinkdb.com/api/python/get/)
# # command.
# #
# # Using a task's ID will prove more useful when we decide to update
# # it, mark it completed, or delete it.
# @main.route("/todos/<string:todo_id>", methods=['GET'])
# def get_todo(todo_id):
#     todo = r.table('todos').get(todo_id).run(g.rdb_conn)
#     return json.dumps(todo)
#
# #### Editing/Updating a task
#
# # Updating a todo (editing it or marking it completed) is performed on
# # a `PUT` request.  To save the updated todo we'll do a
# # [`replace`](http://www.rethinkdb.com/api/python/replace/).
# @main.route("/todos/<string:todo_id>", methods=['PUT'])
# def update_todo(todo_id):
#     return jsonify(r.table('todos').get(todo_id).replace(request.json)
#                     .run(g.rdb_conn))
#
# # If you'd like the update operation to happen as the result of a
# # `PATCH` request (carrying only the updated fields), you can use the
# # [`update`](http://www.rethinkdb.com/api/python/update/)
# # command, which will merge the JSON object stored in the database
# # with the new one.
# @main.route("/todos/<string:todo_id>", methods=['PATCH'])
# def patch_todo(todo_id):
#     return jsonify(r.table('todos').get(todo_id).update(request.json)
#                     .run(g.rdb_conn))
#
#
# #### Deleting a task
#
# # To delete a todo item we'll call a
# # [`delete`](http://www.rethinkdb.com/api/python/delete/)
# # command on a `DELETE /todos/<todo_id>` request.
# @main.route("/todos/<string:todo_id>", methods=['DELETE'])
# def delete_todo(todo_id):
#     return jsonify(r.table('todos').get(todo_id).delete().run(g.rdb_conn))
#
@main.route("/gtd")
def show_todos():
    return render_template('todo.html')


if __name__ == '__main__':
    pass

