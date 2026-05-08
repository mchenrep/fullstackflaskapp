from flask import Flask
from flask import render_template, redirect, url_for, request
from service import TransactionService

app = Flask(__name__)
service = TransactionService()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/start", methods = ["GET"])
def start():
    return redirect(url_for('home'))

@app.route("/transact", methods=["GET"])
def transact_form():
    return render_template("transact_form.html")

@app.route("/transact", methods=["POST"])
def transact_result():
    if request.form["from"] == "" or request.form["to"] == "" or request.form["amount"] == "":
        return render_template("transact_error.html")
    return render_template("transact_success.html", from_account = request.form["from"], to_account = request.form("to"), amount = request.form("amount"))



if __name__ == "__main__":
    app.run(debug=True)