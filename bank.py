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
app.config['MYSQL_PASSWORD'] = 'deep'
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

@app.route('/delete_customer', methods=['GET', 'POST'])
def delete_customer():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            cust_id = userDetails['CustomerID']
            cur = mysql.connection.cursor()
            try:
                sql_select_query = """delete from CustomerStatus where ws_cust_id = %s"""
                cur.execute(sql_select_query, (cust_id,))
                mysql.connection.commit()
                sql_select_query = """delete from Customer where ws_cust_id = %s"""
                cur.execute(sql_select_query, (cust_id,))
                mysql.connection.commit()
                cur.close()
                cust_sts = "Customer Deleted Successfully"
                return render_template('message.html', username=session['login'], message=cust_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('delete_customer.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/deleteCustomer', methods=['GET', 'POST'])
def deleteCustomer():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            cust_ssn_id = userDetails['custssnid']
            cust_id = userDetails['custid']
            cur = mysql.connection.cursor()
            try:
                if cust_id:
                    sql_select_query = """select * from Customer where ws_cust_id = %s"""
                    cur.execute(sql_select_query, (cust_id,))
                    cust_sts = cur.fetchall()
                    cur.close()
                    return render_template('delete_customer.html', username=session['login'], cust_status=cust_sts)
                else:
                    sql_select_query = """select * from Customer where ws_ssn = %s"""
                    cur.execute(sql_select_query, (cust_ssn_id,))
                    cust_sts = cur.fetchall()
                    cur.close()
                    return render_template('delete_customer.html', username=session['login'], cust_status=cust_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('deleteCustomer.html', username=session['login'])
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
            trans_id=randint(100000000, 999999999)
            trans_desc="Deposit"
            trans_type = 'Credit'
            try:
                cur.execute('INSERT INTO Account(ws_cust_id,ws_acct_id, ws_acct_type, ws_acct_balance, ws_acct_crdate, ws_acct_lasttrdate) VALUES(%s,%s, %s, %s, STR_TO_DATE(%s,%s), STR_TO_DATE(%s,%s))',
                            (cust_id, acct_id, acct_type, dpst_amt, cust_date, date_type, act_date, date_type))
                cur.execute('UPDATE AccountStatus SET ws_acct_id = %s, ws_acct_type = %s, ws_status = %s , ws_msg =  %s, ws_lastupdate = STR_TO_DATE(%s,%s) WHERE ws_cust_id = %s',
                            (acct_id, acct_type, act_status, act_msg, cust_date, date_type, cust_id))
                cur.execute('INSERT INTO Transactions(ws_cust_id,ws_accnt_type,ws_amt, ws_trxn_date,ws_src_typ,ws_tgt_typ,ws_trxn_id,ws_description, ws_type) VALUES(%s,%s, %s, STR_TO_DATE(%s,%s),%s,%s,%s,%s,%s)',
                            (cust_id, acct_type, dpst_amt, act_date , date_type, acct_type, acct_type,trans_id,trans_desc, trans_type))
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
                acct_sts = "Account Deleted Successfully"
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

@app.route('/customer_search', methods=['GET', 'POST'])
def customer_search():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            cust_ssn_id = userDetails['custssnid']
            cust_id = userDetails['custid']
            cur = mysql.connection.cursor()
            try:
                if cust_id:
                    sql_select_query = """select * from Customer where ws_cust_id = %s"""
                    cur.execute(sql_select_query, (cust_id,))
                    cust_sts = cur.fetchall()
                    cur.close()
                    return render_template('customerSearch.html', username=session['login'], cust_status=cust_sts)
                else:
                    sql_select_query = """select * from Customer where ws_ssn = %s"""
                    cur.execute(sql_select_query, (cust_ssn_id,))
                    cust_sts = cur.fetchall()
                    cur.close()
                    return render_template('customerSearch.html', username=session['login'], cust_status=cust_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('customer_search.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/account_search', methods=['GET', 'POST'])
def account_search():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            acct_id = userDetails['acctid']
            cust_id = userDetails['custid']
            cur = mysql.connection.cursor()
            try:
                if cust_id:
                    sql_select_query = """select * from Account where ws_cust_id = %s"""
                    cur.execute(sql_select_query, (cust_id,))
                    acct_sts = cur.fetchall()
                    cur.close()
                    return render_template('accountSearch.html', username=session['login'], acct_status=acct_sts)
                else:
                    sql_select_query = """select * from Account where ws_acct_id = %s"""
                    cur.execute(sql_select_query, (acct_id,))
                    acct_sts = cur.fetchall()
                    cur.close()
                    return render_template('accountSearch.html', username=session['login'], acct_status=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('account_search.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/withdraw_amount', methods=['GET', 'POST'])
def withdraw_amount():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            witd_amt = userDetails['witd_amt']
            witd_amt = eval(witd_amt)
            acct_id = userDetails['AccountID']
            cur = mysql.connection.cursor()
            try:
                sql_select_query = """select ws_acct_balance from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (acct_id,))
                avail_blc =cur.fetchall()
                blc = int(avail_blc[0][0])
                new_blc = blc - witd_amt
                sql_select_query = """update Account set ws_acct_balance =%s where ws_acct_id = %s"""
                cur.execute(sql_select_query, (new_blc,acct_id,))
                mysql.connection.commit()
                now = datetime.now()
                cust_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
                date_type = '%d/%m/%Y %H:%i:%s'
                sql_select_query = """update Account set ws_acct_lasttrdate =STR_TO_DATE(%s,%s) where ws_acct_id = %s"""
                cur.execute(sql_select_query,
                            (cust_date, date_type, acct_id,))
                mysql.connection.commit()
                #Transaction Statement
                sql_select_query = """select ws_cust_id,ws_acct_type from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (acct_id,))
                account =cur.fetchall()
                cust_id = int(account[0][0])
                acct_type=account[0][1]
                trans_id=randint(100000000, 999999999)
                trans_desc="Withdraw"
                trans_type = 'Debit'
                act_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
                date_type = '%d/%m/%Y %H:%i:%s'
                cur.execute('INSERT INTO Transactions(ws_cust_id,ws_accnt_type,ws_amt, ws_trxn_date,ws_src_typ,ws_tgt_typ,ws_trxn_id,ws_description, ws_type) VALUES(%s,%s, %s, STR_TO_DATE(%s,%s),%s,%s,%s,%s,%s)',
                            (cust_id, acct_type, witd_amt, act_date , date_type, acct_type, acct_type,trans_id,trans_desc, trans_type))
                mysql.connection.commit()
                cur.close()
                acct_sts = "Account Balance Withdrawn Successfully"
                return render_template('message.html', username=session['login'], message=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('withdraw_amount.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/withdrawAmount', methods=['GET', 'POST'])
def withdrawAmount():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            acct_id = userDetails['acctid']
            cust_id = userDetails['custid']
            cur = mysql.connection.cursor()
            try:
                if cust_id:
                    sql_select_query = """select ws_cust_id,ws_acct_id,ws_acct_type,ws_acct_balance from Account where ws_cust_id = %s"""
                    cur.execute(sql_select_query, (cust_id,))
                    acct_sts= cur.fetchall()
                    cur.close()
                    return render_template('withdraw_amount.html', username=session['login'], acct_status=acct_sts)
                else:
                    sql_select_query = """select ws_cust_id,ws_acct_id,ws_acct_type,ws_acct_balance from Account where ws_acct_id = %s"""
                    cur.execute(sql_select_query, (acct_id,))
                    acct_sts = cur.fetchall()
                    cur.close()
                    return render_template('withdraw_amount.html', username=session['login'], acct_status=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('withdrawAmount.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/transfer_money')
def transfer_money():
    if 'loggedin' in session:
        return render_template('transfer_money.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/transferMoney', methods=['GET', 'POST'])
def transferMoney():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            transfer_amt = userDetails['tranferamt']
            transfer_amt = eval(transfer_amt)
            src_acct_id = userDetails['srcacctid']
            trgt_acct_id = userDetails['trgtacctid']
            cur = mysql.connection.cursor()
            try:
                sql_select_query = """select ws_acct_balance from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (src_acct_id,))
                avail_blc_src = cur.fetchall()
                blc_src = int(avail_blc_src[0][0])
                new_blc_src = blc_src - transfer_amt
                if new_blc_src < 0:
                    e = 'Transfer Amount is not valid as per Source Account Available Balance'
                    return render_template('message.html', username=session['login'], message=e)
                sql_select_query = """select ws_acct_balance from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (trgt_acct_id,))
                avail_blc_trgt = cur.fetchall()
                blc_trgt = int(avail_blc_trgt[0][0])
                new_blc_trgt = blc_trgt + transfer_amt
                now = datetime.now()
                cust_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
                date_type = '%d/%m/%Y %H:%i:%s'
                sql_select_query = """update Account set ws_acct_balance =%s where ws_acct_id = %s"""
                cur.execute(sql_select_query, (new_blc_src, src_acct_id,))
                mysql.connection.commit()
                #Target Transtion Statement
                sql_select_query = """select ws_cust_id from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (trgt_acct_id,))
                account =cur.fetchall()
                cust_id = int(account[0][0])
                sql_select_query = """select ws_acct_type from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (trgt_acct_id,))
                account = cur.fetchall()
                tar_acct_type=str(account[0][0])
                sql_select_query = """select ws_acct_type from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (src_acct_id,))
                account =cur.fetchall()
                src_acct_type=str(account[0][0])
                trans_id=randint(100000000, 999999999)
                trans_desc="Deposit"
                trans_type = 'Credit'
                act_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
                date_type = '%d/%m/%Y %H:%i:%s'
                cur.execute('INSERT INTO Transactions(ws_cust_id,ws_accnt_type,ws_amt, ws_trxn_date,ws_src_typ,ws_tgt_typ,ws_trxn_id,ws_description,ws_type) VALUES(%s,%s, %s, STR_TO_DATE(%s,%s),%s,%s,%s,%s,%s)',
                            (cust_id, tar_acct_type, transfer_amt, act_date , date_type, src_acct_type, tar_acct_type,trans_id,trans_desc,trans_type))
                mysql.connection.commit()
                #source Transtion Statement
                sql_select_query = """select ws_cust_id from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (src_acct_id,))
                account =cur.fetchall()
                cust_id = int(account[0][0])
                sql_select_query = """select ws_acct_type from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (src_acct_id,))
                account = cur.fetchall()
                src_acct_type=str(account[0][0])
                sql_select_query = """select ws_acct_type from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (trgt_acct_id,))
                account = cur.fetchall()
                tar_acct_type = str(account[0][0])
                trans_id=randint(100000000, 999999999)
                trans_desc="Withdraw"
                trans_type = 'Debit'
                act_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
                date_type = '%d/%m/%Y %H:%i:%s'
                cur.execute('INSERT INTO Transactions(ws_cust_id,ws_accnt_type,ws_amt, ws_trxn_date,ws_src_typ,ws_tgt_typ,ws_trxn_id,ws_description,ws_type) VALUES(%s,%s, %s, STR_TO_DATE(%s,%s),%s,%s,%s,%s,%s)',
                            (cust_id, src_acct_type, transfer_amt, act_date , date_type, src_acct_type, tar_acct_type,trans_id,trans_desc,trans_type))
                mysql.connection.commit()
                sql_select_query = """update Account set ws_acct_lasttrdate =STR_TO_DATE(%s,%s) where ws_acct_id = %s"""
                cur.execute(sql_select_query,
                            (cust_date, date_type, src_acct_id,))
                mysql.connection.commit()
                sql_select_query = """update Account set ws_acct_balance =%s where ws_acct_id = %s"""
                cur.execute(sql_select_query, (new_blc_trgt, trgt_acct_id,))
                mysql.connection.commit()
                sql_select_query = """update Account set ws_acct_lasttrdate =STR_TO_DATE(%s,%s) where ws_acct_id = %s"""
                cur.execute(sql_select_query,
                            (cust_date, date_type, trgt_acct_id,))
                mysql.connection.commit()
                sql_select_query = """select ws_acct_balance from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (src_acct_id,))
                lst_blc_src = cur.fetchall()
                lst_acct_src = int(lst_blc_src[0][0])
                sql_select_query = """select ws_acct_balance from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (trgt_acct_id,))
                lst_blc_trgt = cur.fetchall()
                lst_acct_trgt = int(lst_blc_trgt[0][0])
                cur.close()
                return render_template('transfer_money.html', username=session['login'], scractid=src_acct_id, trgtactid=trgt_acct_id, prvActSrc=blc_src, prvActTrgt=blc_trgt, nxtActSrc=lst_acct_src, nxtActTrgt=lst_acct_trgt)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('transferMoney.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/deposit_money', methods=['GET', 'POST'])
def deposit_money():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            dpst_amt = userDetails['dpst_amt']
            dpst_amt = eval(dpst_amt)
            acct_id = userDetails['AccountID']
            cur = mysql.connection.cursor()
            try:
                sql_select_query = """select ws_acct_balance from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (acct_id,))
                avail_blc = cur.fetchall()
                blc = int(avail_blc[0][0])
                new_blc = blc + dpst_amt
                sql_select_query = """update Account set ws_acct_balance =%s where ws_acct_id = %s"""
                cur.execute(sql_select_query, (new_blc, acct_id,))
                mysql.connection.commit()
                now = datetime.now()
                cust_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
                date_type = '%d/%m/%Y %H:%i:%s'
                sql_select_query = """update Account set ws_acct_lasttrdate =STR_TO_DATE(%s,%s) where ws_acct_id = %s"""
                cur.execute(sql_select_query,
                            (cust_date, date_type, acct_id,))
                mysql.connection.commit()
                #transaction Statement
                sql_select_query = """select ws_cust_id,ws_acct_type from Account where ws_acct_id = %s"""
                cur.execute(sql_select_query, (acct_id,))
                account =cur.fetchall()
                cust_id = int(account[0][0])
                acct_type=account[0][1]
                trans_id=randint(100000000, 999999999)
                trans_desc="Deposit"
                trans_type = 'Credit'
                act_date = (now.strftime("%d/%m/%Y %H:%M:%S"))
                date_type = '%d/%m/%Y %H:%i:%s'
                cur.execute('INSERT INTO Transactions(ws_cust_id,ws_accnt_type,ws_amt, ws_trxn_date,ws_src_typ,ws_tgt_typ,ws_trxn_id,ws_description,ws_type) VALUES(%s,%s, %s, STR_TO_DATE(%s,%s),%s,%s,%s,%s,%s)',
                            (cust_id, acct_type, dpst_amt, act_date , date_type, acct_type, acct_type,trans_id,trans_desc,trans_type))
                mysql.connection.commit()
                cur.close()
                acct_sts = "Account Balance Deposited Successfully"
                return render_template('message.html', username=session['login'], message=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('deposit_money.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/depositMoney', methods=['GET', 'POST'])
def depositAmount():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            acct_id = userDetails['acctid']
            cust_id = userDetails['custid']
            cur = mysql.connection.cursor()
            try:
                if cust_id:
                    sql_select_query = """select ws_cust_id,ws_acct_id,ws_acct_type,ws_acct_balance from Account where ws_cust_id = %s"""
                    cur.execute(sql_select_query, (cust_id,))
                    acct_sts = cur.fetchall()
                    cur.close()
                    return render_template('deposit_money.html', username=session['login'], acct_status=acct_sts)
                else:
                    sql_select_query = """select ws_cust_id,ws_acct_id,ws_acct_type,ws_acct_balance from Account where ws_acct_id = %s"""
                    cur.execute(sql_select_query, (acct_id,))
                    acct_sts = cur.fetchall()
                    cur.close()
                    return render_template('deposit_money.html', username=session['login'], acct_status=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('depositMoney.html', username=session['login'])
    return redirect(url_for('login'))

@app.route('/accountStatement', methods=['GET', 'POST'])
def accountStatement():
    if 'loggedin' in session:
        if request.method == 'POST':
            userDetails = request.form
            acct_id = userDetails['accountid']
            trnx_no = userDetails['transactions']
            trnx_no = eval(trnx_no)
            cur = mysql.connection.cursor()
            try:
                select = "select ws_cust_id from Account where ws_acct_id = %s"
                cur.execute(select, (acct_id,))
                cust_id = cur.fetchall()
                custId = int(cust_id[0][0])
                sql_select_query = """select ws_trxn_id,ws_description,ws_type,ws_trxn_date, ws_amt from Transactions where ws_cust_id = %s LIMIT %s"""
                cur.execute(sql_select_query, (custId,trnx_no,))
                acct_sts = cur.fetchall()
                cur.close()
                return render_template('account_statement.html', username=session['login'], acct_status=acct_sts)
            except Exception as e:
                return render_template('message.html', username=session['login'], message=e)
        return render_template('accountStatement.html', username=session['login'])
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

