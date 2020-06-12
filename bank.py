from flask import Flask,render_template,url_for,request,redirect

app=Flask(__name__)

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/create_customer_screen')
def create_customer_screen():
    return render_template("create_customer_screen.html")

@app.route('/update_customer')
def update_customer():
    return render_template("update_customer.html")

@app.route('/delete_customer')
def delete_customer():
    return render_template("delete_customer.html")

@app.route('/customer_status')
def customer_status():
    return render_template("customer_status.html")

@app.route('/create_account')
def create_account():
    return render_template("create_account.html")

@app.route('/delete_account')
def delete_account():
    return render_template("delete_account.html")

@app.route('/account_status')
def account_status():
    return render_template("account_status.html")


@app.route('/customer_search')
def customer_search():
    return render_template("customer_search.html")

@app.route('/account_search')
def account_search():
    return render_template("account_search.html")

@app.route('/withdraw_amount')
def withdraw_amount():
    return render_template("withdraw_amount.html")

@app.route('/transfer_money')
def transfer_money():
    return render_template("transfer_money.html")

@app.route('/account_statement')
def account_statement():
    return render_template("account_statement.html")


if __name__==("__main__"):
    app.run(debug=True)

