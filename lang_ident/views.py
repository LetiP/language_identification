# -*- coding: utf-8 -*-
"""
Routes and views for the flask application.
"""

import os
import sys
from datetime import datetime
from flask import render_template, json, request, redirect, url_for, session
from lang_ident import APP

from lang_ident import lang_ident as li

import time


@APP.route('/')
@APP.route('/home')
def home():
    """ Renders the home page. """
    return render_template(
        'index.html',
        title='lang i dent',
        year=datetime.now().year
    )

@APP.route('/identifyLang', methods=['POST'])
def identifyLang():
    """ Identify the language for the input text."""
    # parse text
    txt = request.json['txt'].strip('?!,.')
    txt = txt.split(' ')

    t1 = time.time()
    lang = li.identify(txt)
    print('Took', time.time()-t1)

    return json.dumps({'language': lang})