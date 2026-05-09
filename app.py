from flask import Flask
from flask import render_template, redirect, url_for, request
from service import TransactionService

app = Flask(__name__)
service = TransactionService()
service.start()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if request.method == "GET":
        # return transfer form
        return render_template("transfer.html")
    if request.method == "POST":
        try:
            # validate form
            to_account = int(request.form["to"])
            from_account = int(request.form["from"])
            amount = int(request.form["amount"])

            if amount <= 0:
                return redirect(url_for("error"))

            # submit task to back end
            service.submit_task(from_account, to_account, amount)
            
            # redirect to transfer request success page
            return redirect(url_for(
                "success",
                to_account=to_account,
                from_account=from_account,
                amount=amount
            ))
        except:
            # return error page for any errors
            return redirect(url_for("error"))

@app.route("/success")
def success():
    to_account = request.args.get("to_account")
    from_account = request.args.get("from_account")
    amount = request.args.get("amount")
    return render_template("success.html", to_account = to_account, from_account = from_account, amount = amount)

@app.route("/error")
def error():
    return render_template("error.html")
    
if __name__ == "__main__":
    app.run(debug=True)