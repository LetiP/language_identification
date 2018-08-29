"""
The flask application package.
"""

from flask import Flask

APP = Flask(__name__)

import lang_ident.views