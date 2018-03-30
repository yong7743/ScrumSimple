#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app, request, url_for
from . import db, login_manager
import json
import urllib
import hashlib
from markdown import markdown
import bleach
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin


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


# Permission enum
class Permission:
    READ = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.READ, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.READ, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.READ, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


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
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

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

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def _photo_from_id(self, size=100, default='identicon', rating='g'):
        if self.github_id is not None:
            url = 'https://avatars.githubusercontent.com/u'
            return '{url}/{id}?s={size}&d={default}&r={rating}'.format(
            url=url, id=self.github_id, size=size, default=default, rating=rating)
        return None

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)


    def gravatar(self, size=100, default='identicon', rating='g'):
        photo_url = self._photo_from_id(size, default, rating)
        if photo_url is not None:
            return photo_url

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


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


def add_url_for_issue(matched):
    base_url = "https://devtopia.esri.com/runtime/arcgis-earth/issues/"
    number = str(matched.group(0)[1:])
    return "[#" + number + "](" + base_url + number + ")"


def replace_issue(body):
    import re
    return re.sub('#[0-9]{1,}', add_url_for_issue, body)


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
            markdown(replace_issue(value), output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Report.body, 'set', Report.on_changed_body)


class WeeklyPlan(db.Model):
    __tablename__ = 'weeklys'
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
            markdown(replace_issue(value), output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(WeeklyPlan.body, 'set', WeeklyPlan.on_changed_body)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))






