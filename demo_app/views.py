from .app import app

@app.route("/")
def index():
<<<<<<< Updated upstream
    return app.send_static_file("index.html")
=======
    return app.send_static_file("index.html")
>>>>>>> Stashed changes
