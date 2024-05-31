import sys
import os

# Add the parent directory to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(parent_dir)
from flask import Flask
app = Flask(__name__)
@app.route('/')
def index():
    return 'Hello Admin World'
if __name__ == '__main__':
    app.run(debug=False, port=8000, host='0.0.0.0')
