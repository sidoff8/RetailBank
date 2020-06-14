from flask import Flask,render_template,url_for,request,redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app=Flask(__name__)

# Secret key (can be anything, it's for extra protection)
app.secret_key = 'thisismysecretkey123456789'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'retailbank'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if password matches the criteria and then proceed
        if re.match("(?=^.{10,}$)(?=.*\d)(?=.*[!@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$", password):
            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM userstore WHERE login = %s AND password = %s', (username, password,))
            # Fetch one record and return result
            account = cursor.fetchone()
            # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                # session['id'] = account['id']
                session['login'] = account['login']
                # Redirect to home page
                # msg = 'Logged in successfully!'
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/password !!'
        else:
            msg = 'Password should contain one special character, one upper case, one numeric.'

    return render_template("login.html", msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['login'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

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

@app.route('/deposit_money')
def deposit_money():
    return render_template("deposit_money.html")

@app.route('/account_statement')
def account_statement():
    return render_template("account_statement.html")


if __name__==("__main__"):
    app.run(debug=True)

