#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app, request, url_for
from flask_login import UserMixin
from . import db, login_manager
import json
import urllib
import hashlib
from markdown import markdown
import bleach

url_user_info = 'https://api.github.com/user'


class GitHubOauth():
    @staticmethod
    def _get(url, data):
        """get请求"""
        request_url = '%s?%s' % (url, urllib.parse.urlencode(data))
        response = urllib.request.urlopen(request_url)
        return response.read().decode('utf-8')

    @staticmethod
    def get_user_info(github, access_token):
        params = {'access_token': access_token,}
        response = GitHubOauth._get(url_user_info, params)
        if response is not None:
            result = json.loads(response)
            return result['id'], result['login'], result['name'], result['email']
        return None


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True)
    avatar_hash = db.Column(db.String(32))
    # https://github.com/cenkalti/github-flask/blob/master/example.py#L49
    github_access_token = db.Column(db.String(200), unique=True)
    github_id = db.Column(db.Integer, unique=True)
    reports = db.relationship('Report', backref='author', lazy='dynamic')
    weeklys = db.relationship('WeeklyPlan', backref='author', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(username=forgery_py.internet.user_name(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        if self.email is None:
            return ""
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'reports': url_for('api.get_user_reports', id=self.id, _external=True),
            'reports_count': self.reports.count()
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.username


class Report(db.Model):
     __tablename__ = 'reports'
     id = db.Column(db.Integer, primary_key=True)
     date = db.Column(db.Date)
     body = db.Column(db.Text)
     body_html = db.Column(db.Text)
     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

     @staticmethod
     def on_changed_body(target, value, oldvalue, initiator):
         allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
         target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Report.body, 'set', Report.on_changed_body)


class WeeklyPlan(db.Model):
    __tablename__ = 'weeklys'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))






