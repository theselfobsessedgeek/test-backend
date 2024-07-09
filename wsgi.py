import sys
import os

# Add the parent directory to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(parent_dir)

from kapsite import app

# import __init__ as init

if __name__ == "__main__":
    # app = init.create_app()
    app.run(host='0.0.0.0', port=4000, debug=False, ssl_context=('cert.pem', 'key.pem'))