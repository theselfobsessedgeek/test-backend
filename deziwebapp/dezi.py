from flask import Flask
app = Flask(__name__)
@app.route('/')
def index():
    return 'Hello DeziWebApp world'
if __name__ == '__main__':
    app.run(debug=False, port=8002, host='0.0.0.0')
