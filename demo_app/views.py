from .app import app
from flask import render_template

@app.route("/")
def index():
    return app.send_static_file("index.html")
    # return render_template("demo_index.html")
