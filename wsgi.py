from kapsite import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False, ssl_context=('cert.pem', 'key.pem'))