from flask_login_tutorial import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context='adhoc', debug=True)
