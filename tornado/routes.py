from tornado import app


@app.route("/home")
def home():
    return 'Hello'