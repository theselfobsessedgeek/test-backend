import sys
import os

# Add the parent directory to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(parent_dir)
import __init__ as init
from flask_mongoengine import MongoEngine
# Start development web server
if __name__ == '__main__':
   app = init.create_app()
   def get_db():
       if 'db' not in init.g:
           init.g.db = MongoEngine()
           init.g.db.init_app(app)
       return init.g.db   
    # @app.before_request
    # def before_request():
    #     g.db = db.init_app(app) #connect_db()
    # @app.teardown_appcontext
    # def teardown_db(exception):
    #     db = g.pop('db', None)
    #     if db is not None:
    #         db.close()
   app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=('cert.pem', 'key.pem'))





# from flask import Flask
# from __init__ import create_app 
# app = Flask(__name__)
# @app.route('/')
# def index():
#     return 'Hello world'
# if __name__ == '__main__':
#     app.run(debug=False, port=8000, host='0.0.0.0')
