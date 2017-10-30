#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, DateField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from app.models import Report, User


class ReportForm(FlaskForm):
    name = StringField('Name?', validators=[Required()])
    date = DateField('Date?', validators=[Required()])
    body = TextAreaField("Today?", validators=[Required()])
    submit = SubmitField('Submit')


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

