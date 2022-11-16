from flask import Flask, render_template, request, redirect, url_for, session
import os
import re
import ibm_db

conn= ibm_db.connect("DATABASE=bludb;HOSTNAME=2d46b6b4-cbf6-40eb-bbce-6251e6ba0300.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32328;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=kxz33978;PWD=HWEnA3t3Q6pAznDA",'','')

app = Flask(__name__)
app.secret_key=os.urandom(12)

@app.route('/', methods =['GET', 'POST'])
def home():
	return redirect(url_for('login'))

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg=''
	if request.method == 'GET':
		return render_template('login.htm')
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		sql="SELECT * FROM KXZ33978.USER WHERE USER_NAME='"+username+"'AND PASSWORD='"+password+"'"
		stmt= ibm_db.exec_immediate(conn,sql)
		account= ibm_db.fetch_assoc(stmt)
		if account:
			session['loggedin'] = True
			session['id'] = account['USER_ID']
			session['username'] = account['USER_NAME']
			msg = 'Logged in successfully !'
			return render_template('dashboard.html', msg = username)

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg=''
	if request.method == 'GET':
		return render_template('register.html')
		
	if request.method == 'POST'  and 'username' in request.form and 'password' in request.form and 'email' in request.form:
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		print(request.form)
		sql="SELECT * FROM KXZ33978.USER WHERE USER_NAME='"+username+"'"
		stmt= ibm_db.exec_immediate(conn,sql)
		account= ibm_db.fetch_assoc(stmt)
		if account:
			msg = 'Account already exists !'
			return render_template('register.html', msg = msg)
		else:
			sql="INSERT INTO KXZ33978.USER(USER_ID,"'USER_NAME'","'PASSWORD'","'EMAIL'") VALUES(seq_person.nextval,'"+username+"','"+password+"','"+email+"')"
			stmt= ibm_db.exec_immediate(conn,sql)
			msg = 'You have successfully registered !'
			return render_template('login.htm', msg = msg)

@app.route('/dash', methods =['GET', 'POST'])
def dash():
	if request.method == 'GET':
		return render_template('home.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
	
if __name__ == '__main__':
	app.run(debug=True)


