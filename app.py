from flask import Flask
from flask import render_template, redirect, url_for, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/start", methods = ["GET"])
def start():
    return redirect(url_for('home'))




if __name__ == "__main__":
    app.run(debug=True)