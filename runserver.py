"""
This script runs the application using a development server.
"""

from os import environ
from lang_ident import APP

if __name__ == '__main__':
    # HOST = environ.get('SERVER_HOST', 'localhost') # only accept connections from same computer
    HOST = '0.0.0.0'  # hosting in local network
    try:
        PORT = int(environ.get('SERVER_PORT', '4242'))
    except ValueError:
        PORT = 4242
    
    APP.secret_key = "This secret key will be in wsgi on production"
    
    APP.run(HOST, PORT)