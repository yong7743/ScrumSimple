#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, DateField
from wtforms.validators import Required


class ReportForm(FlaskForm):
    date = DateField('Date?', validators=[Required()])
    body = TextAreaField("Today?", validators=[Required()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('What is your name?', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

