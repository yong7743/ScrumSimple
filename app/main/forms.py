#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm, widgets
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, DateField
from wtforms.validators import Required
from flask_admin.form import widgets
from flask_pagedown.fields import PageDownField


class ReportForm(FlaskForm):
    date = DateField('Date?', default='', validators=[Required()], format='%Y/%m/%d', widget=widgets.DatePickerWidget())
    body = PageDownField("What are you doing?", validators=[Required()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class ScrumForm(FlaskForm):
    start = DateField('Start Date?', default='', validators=[Required()], format='%Y/%m/%d', widget=widgets.DatePickerWidget())
    end = DateField('End Date?', default='', validators=[Required()], format='%Y/%m/%d', widget=widgets.DatePickerWidget())
    submit = SubmitField('Submit')



