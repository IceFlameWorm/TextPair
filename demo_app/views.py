from .app import app

@app.route("/")
def index():
    return app.send_static_file("dai_index.html")