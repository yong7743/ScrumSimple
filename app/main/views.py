from flask import Flask, request, render_template, make_response,send_file
import os,sys
from flask import Flask, render_template, session, redirect, url_for
from . import main
from .forms import ReportForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = ReportForm()
    if form.validate_on_submit():
        pass
    return render_template("report.html", form=form)

if __name__ == '__main__':
    pass

