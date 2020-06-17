from flask import Flask,render_template,url_for,request,redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
from random import randint


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
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['login'])
        
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




@app.route('/create_customer_screen', methods=['GET', 'POST'])
def create_customer_screen():
    if 'loggedin' in session:
        if request.method == 'POST':
            cust_id=randint(100000000, 999999999)
            userDetails = request.form
            cust_ssnid = userDetails['ssnid']
            cust_name = userDetails['custname']
            cust_age = userDetails['age']
            cust_addr1 = userDetails['addr']
            cust_state = userDetails['state']
            cust_city = userDetails['city']
            cust_addr = cust_addr1 + ", "+cust_city+", "+cust_state
            cur = mysql.connection.cursor()
            cust_msg = 'Customer Created Successfully'
            cust_status = 'Active'
            act_status = 'Pending'
            now = datetime.now()
            act_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
            cust_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
            date_type='%d/%m/%Y %H:%i:%s'
            act_msg = ''

            try:
                cur.execute('INSERT INTO Customer(ws_cust_id,ws_ssn, ws_name, ws_age, ws_adrs) VALUES(%s,%s, %s, %s, %s)',(cust_id,cust_ssnid, cust_name, cust_age, cust_addr))
                cur.execute('INSERT INTO CustomerStatus(ws_cust_id,ws_ssn, ws_status, ws_msg, ws_lastupdate) VALUES(%s,%s, %s, %s, STR_TO_DATE(%s,%s))', (cust_id,cust_ssnid, cust_status, cust_msg, cust_date, date_type))
                cur.execute('INSERT INTO AccountStatus(ws_cust_id,ws_status, ws_msg, ws_lastupdate) VALUES(%s,%s, %s, STR_TO_DATE(%s,%s))', (cust_id,act_status, act_msg, act_date, date_type))
                mysql.connection.commit()
                cur.close()
                message="Customer creation initiated successfully"
                return render_template('message.html', username=session['login'],message=message)
            except Exception as e:
                return render_template('message.html', username=session['login'],message=e) 
        return render_template('create_customer_screen.html', username=session['login'])
    return redirect(url_for('login'))


@app.route('/updateCustomer', methods=['GET', 'POST'])
def updateCustomer():
    if 'loggedin' in session:  
        if request.method == 'POST':
            userDetails = request.form
            ssn_id = userDetails['ssnid']
            cust_id = userDetails['custid']
            cur = mysql.connection.cursor()
            try:
                if cust_id:
                    sql_select_query = """select ws_ssn, ws_cust_id,ws_name,ws_adrs,ws_age from customer where ws_cust_id = %s"""
                    cur.execute(sql_select_query, (cust_id,))
                    acct_sts = cur.fetchall()
                    cur.close()
                    return render_template('update_customer.html', username=session['login'], acct_status=acct_sts)
                else:
                    sql_select_query = """select ws_ssn, ws_cust_id,ws_name,ws_adrs,ws_age from customer where ws_ssn = %s"""
                    cur.execute(sql_select_query, (ssn_id,))
                    acct_sts = cur.fetchall()
                    cur.close()
                    return render_template('update_customer.html', username=session['login'], acct_status=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('updateCustomer.html', username=session['login'])
    return redirect(url_for('login'))




@app.route('/update_customer', methods=['GET', 'POST'])
def update_customer():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            #acct_id = userDetails['acctid']
            ssn_id = userDetails['SSN_ID']
            cname=str(userDetails['c_name'])
            cadd=userDetails['c_add']
            cage=userDetails['c_age']
            cur = mysql.connection.cursor()
            try:
                sql_select_query = """UPDATE customer SET ws_name = %s , ws_adrs= %s, ws_age=%s where ws_ssn = %s"""
                cur.execute(sql_select_query, (cname,cadd,cage,ssn_id,))
                mysql.connection.commit()
                cur.close()
                acct_sts = "Customer Updated Successfully"
                return render_template('message.html', username=session['login'], message=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('customer_update.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/delete_customer')
def delete_customer():
    if 'loggedin' in session:
        return render_template('delete_customer.html', username=session['login'])
    return redirect(url_for('login'))


@app.route('/customer_status')
def customer_status():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        try:
            sql_select_Query = 'SELECT * FROM CustomerStatus'
            cur.execute(sql_select_Query)
            cust_sts = cur.fetchall()
            cur.close()
        except Exception as e:
            return render_template('message.html', username=session['login'], message=e)
        return render_template('customer_status.html', username=session['login'], cust_status=cust_sts)
    return redirect(url_for('login'))


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if 'loggedin' in session:
        if request.method == 'POST':
            acct_id = randint(100000000, 999999999)
            userDetails = request.form
            cust_id = userDetails['cust_id']
            acct_type = userDetails['acct_type']
            dpst_amt = userDetails['dpst_amt']
            cur = mysql.connection.cursor()
            act_status = 'Active'
            now = datetime.now()
            act_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
            cust_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
            date_type = '%d/%m/%Y %H:%i:%s'
            act_msg = 'Account Created Successfully'
            try:
                cur.execute('INSERT INTO Account(ws_cust_id,ws_acct_id, ws_acct_type, ws_acct_balance, ws_acct_crdate, ws_acct_lasttrdate) VALUES(%s,%s, %s, %s, STR_TO_DATE(%s,%s), STR_TO_DATE(%s,%s))',
                            (cust_id, acct_id, acct_type, dpst_amt, cust_date, date_type, act_date, date_type))
                cur.execute('UPDATE AccountStatus SET ws_acct_id = %s, ws_acct_type = %s, ws_status = %s , ws_msg =  %s, ws_lastupdate = STR_TO_DATE(%s,%s) WHERE ws_cust_id = %s',
                            (acct_id, acct_type, act_status, act_msg, cust_date, date_type, cust_id))
                mysql.connection.commit()
                cur.close()
                message = "Customer Account Created successfully"
                return render_template('message.html', username=session['login'], message=message)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('create_account.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/delete_account', methods = ['GET', 'POST'])
def delete_account():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            #acct_id = userDetails['acctid']
            acct_id = userDetails['AccountID']
            cur = mysql.connection.cursor()
            try:
                sql_select_query = """delete from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (acct_id,))
                mysql.connection.commit()
                sql_select_query = """delete from AccountStatus where ws_acct_id = %s"""
                cur.execute(sql_select_query, (acct_id,))
                mysql.connection.commit()
                cur.close()
                acct_sts = "Acoount Deleted Successfully"
                return render_template('message.html', username=session['login'], message=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('delete_account.html', username=session['login'])
    return redirect(url_for('login'))


@app.route('/deleteAccount', methods=['GET', 'POST'])
def deleteAccount():
    if 'loggedin' in session:  
        if request.method == 'POST':
            userDetails = request.form
            acct_id = userDetails['acctid']
            cust_id = userDetails['custid']
            cur = mysql.connection.cursor()
            try:
                if cust_id:
                    sql_select_query = """select ws_acct_id,ws_acct_type from Account where ws_cust_id = %s"""
                    cur.execute(sql_select_query, (cust_id,))
                    acct_sts = cur.fetchall()
                    cur.close()
                    return render_template('delete_account.html', username=session['login'], acct_status=acct_sts)
                else:
                    sql_select_query = """select ws_acct_id,ws_acct_type from Account where ws_acct_id = %s"""
                    cur.execute(sql_select_query, (acct_id,))
                    acct_sts = cur.fetchall()
                    cur.close()
                    return render_template('delete_account.html', username=session['login'], acct_status=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('deleteAccount.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/account_status')
def account_status():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        try:
            sql_select_Query = 'SELECT * FROM AccountStatus'
            cur.execute(sql_select_Query)
            acct_sts = cur.fetchall()
            cur.close()
        except Exception as e:
            return render_template('message.html', username=session['login'], message=e)
        return render_template('account_status.html', username=session['login'], acct_status=acct_sts)
    return redirect(url_for('login'))

@app.route('/customer_search')
def customer_search():
    if 'loggedin' in session:
        return render_template('customer_search.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/account_search')
def account_search():
    if 'loggedin' in session:
        return render_template('account_search.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/withdraw_amount')
def withdraw_amount():
    if 'loggedin' in session:
        return render_template('withdraw_amount.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/transfer_money')
def transfer_money():
    if 'loggedin' in session:
        return render_template('transfer_money.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/deposit_money')
def deposit_money():
    if 'loggedin' in session:
        return render_template('deposit_money.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/account_statement')
def account_statement():
    if 'loggedin' in session:
        return render_template('account_statement.html', username=session['login'])
    return redirect(url_for('login'))


@app.route('/create_customer_screen/success')
def success_message():
    if 'loggedin' in session:
        return render_template('message.html', username=session['login'])
    return redirect(url_for('login'))

if __name__==("__main__"):
    app.run(debug=True)

