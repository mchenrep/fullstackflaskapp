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

@app.route("/transfer", methods=["GET"])
def transact_form():
    return render_template("transfer.html")

@app.route("/transact", methods=["POST"])
def transact_result():
   pass



if __name__ == "__main__":
    app.run(debug=True)