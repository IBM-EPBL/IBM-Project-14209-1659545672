from flask import Flask, render_template, request, redirect, url_for, session
import os
import re
import ibm_db
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
txt="VJ.YmP8fqxPWbatZ5lcArzrDw.54W7rZNSWEzYKArHHlOI6vOOfU-J-dg8m6JAlSZj-q0"
def decrypt(key, message):

    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""

    for letter in message:
        if letter in alpha: 
            letter_index = (alpha.find(letter) - key) % len(alpha)

            result = result + alpha[letter_index]
        else:
            result = result + letter

    return result
key=decrypt(3,txt)
sg = sendgrid.SendGridAPIClient(key)
from_email = Email("19z346@psgtech.ac.in")  # Change to your verified sender
to_email = To("19z317@psgtech.ac.in")  # Change to your recipient
subject = "Alert:Low stock"

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

@app.route('/add_items', methods =['GET', 'POST'])
def add_items():
	msg=''
	if request.method == 'GET':
		return render_template('add_items.html')
	if request.method == 'POST':
		product_name = request.form['name']
		supplier = request.form['supplier']
		threshold = request.form['t_quantity']
		sql="INSERT INTO KXZ33978.PRODUCT_DETAILS(PRODUCT_ID,"'PRODUCT_NAME'","'SUPPLIER'",QUANTITY,THRESHOLD_QTY) VALUES(product_seq.nextval,'"+product_name+"','"+supplier+"',0,"+threshold+")"
		stmt= ibm_db.exec_immediate(conn,sql)
		#msg = 'Product successfully added !'
		return render_template('add_items.html', msg = msg)

@app.route('/delete_items', methods =['GET', 'POST'])
def delete_items():
	msg=''
	product_details=[]
	if request.method == 'GET':
		sql="SELECT * FROM KXZ33978.PRODUCT_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			data={}
			data['Product_ID']=ibm_db.result(stmt,0)
			data['Product_name']=ibm_db.result(stmt,1)
			data['quantity']=ibm_db.result(stmt,2)
			data['supplier']=ibm_db.result(stmt,3)
			product_details.append(data)
			# msg = 'You have successfully registered !'
			print(product_details)
		return render_template('delete_items.html',product_details=product_details)
	
@app.route('/delete_selected_stocks/<product_id>', methods =['GET', 'POST'])
def delete_selected_stocks(product_id):
	if request.method == 'GET':
		sql="DELETE FROM KXZ33978.PRODUCT_DETAILS WHERE PRODUCT_ID="+product_id
		stmt= ibm_db.exec_immediate(conn,sql)
		return redirect(url_for('delete_items'))

@app.route('/add_stocks', methods =['GET', 'POST'])
def add_stocks():
	msg=''
	product_details=[]
	if request.method == 'GET':
		sql="SELECT * FROM KXZ33978.PRODUCT_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			data={}
			data['Product_ID']=ibm_db.result(stmt,0)
			data['Product_name']=ibm_db.result(stmt,1)
			data['quantity']=ibm_db.result(stmt,2)
			data['supplier']=ibm_db.result(stmt,3)
			product_details.append(data)
			# msg = 'You have successfully registered !'
			print(product_details)
		return render_template('add_stocks.html',product_details=product_details)

@app.route('/add_selected_stocks/<product_id>', methods =['GET', 'POST'])
def add_selected_stocks(product_id):
	if request.method == 'GET':
		return render_template('add_quantity.html',product_id=product_id)
	if request.method == 'POST':
		quantity = int(request.form['quantity'])
		location = request.form['location']
		dop = request.form['dop']
		sql="SELECT quantity,product_name FROM KXZ33978.PRODUCT_DETAILS WHERE PRODUCT_ID="+product_id
		stmt= ibm_db.exec_immediate(conn,sql)
		qty= ibm_db.fetch_assoc(stmt)
		quantity+=qty['QUANTITY']
		product_name=qty['PRODUCT_NAME']
		sql="UPDATE PRODUCT_DETAILS SET QUANTITY ="+str(quantity)+" WHERE PRODUCT_ID="+product_id+";"
		stmt= ibm_db.exec_immediate(conn,sql)
		sql="INSERT INTO KXZ33978.PRODUCT_ADD_DETAILS(ADD_ID,PRODUCT_ID,"'PRODUCT_NAME'","'LOCATION'",QUANTITY,"'DATE_OF_PURCHASE'") VALUES(add_seq.nextval,"+product_id+",'"+product_name+"','"+location+"',"+str(quantity)+",'"+request.form['dop']+"')"
		stmt= ibm_db.exec_immediate(conn,sql)
		# msg = 'Product successfully added !'
		return redirect(url_for('add_stocks'))

@app.route('/update_stocks', methods =['GET', 'POST'])
def update_stocks():
	msg=''
	product_details=[]
	if request.method == 'GET':
		sql="SELECT * FROM KXZ33978.PRODUCT_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			data={}
			data['Product_ID']=ibm_db.result(stmt,0)
			data['Product_name']=ibm_db.result(stmt,1)
			data['quantity']=ibm_db.result(stmt,2)
			data['supplier']=ibm_db.result(stmt,3)
			product_details.append(data)
			# msg = 'You have successfully registered !'
			
		return render_template('update_stocks.html',product_details=product_details)

@app.route('/update_selected_stocks/<product_id>', methods =['GET', 'POST'])
def update_selected_stocks(product_id):
	product_details=[]
	if request.method == 'GET':
		return render_template('update_quantity.html',product_id=product_id)
	if request.method == 'POST':
		quantity = int(request.form['quantity'])
		sql="SELECT quantity,product_name FROM KXZ33978.PRODUCT_DETAILS WHERE PRODUCT_ID="+product_id
		stmt= ibm_db.exec_immediate(conn,sql)
		qty= ibm_db.fetch_assoc(stmt)
		new_quantity=int(qty['QUANTITY']-quantity)
		sql="UPDATE PRODUCT_DETAILS SET QUANTITY ="+str(new_quantity)+" WHERE PRODUCT_ID="+product_id+";"
		stmt= ibm_db.exec_immediate(conn,sql)
		sql="SELECT product_id,product_name FROM KXZ33978.PRODUCT_DETAILS WHERE KXZ33978.PRODUCT_DETAILS.QUANTITY<=THRESHOLD_QTY"
		stmt= ibm_db.exec_immediate(conn,sql)
		strr="Items below threshold\n"
		i=1
		while ibm_db.fetch_row(stmt) != False:
			data={}
			data['Product_ID']=ibm_db.result(stmt,0)
			data['Product_name']=ibm_db.result(stmt,1)
			strr+=str(i)+". "+data['Product_name']+"\n"
			i+=1
		product_details.append(data)
		if len(product_details)>0:
			content = Content("text/plain",strr)
			mail = Mail(from_email, to_email, subject, content)
			# Get a JSON-ready representation of the Mail object
			mail_json = mail.get()

			# Send an HTTP POST request to /mail/send
			response = sg.client.mail.send.post(request_body=mail_json)
			print(response.status_code)
			print(response.headers)

		print(product_details)
		return redirect(url_for('update_stocks'))

@app.route('/view_stocks', methods =['GET', 'POST'])
def view_stocks():
	product_ID=[]
	product_name=[]
	supplier=[]
	location=[]
	if request.method == 'GET':
		sql="SELECT DISTINCT PRODUCT_ID FROM KXZ33978.PRODUCT_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			product_ID.append(ibm_db.result(stmt,0))

		sql="SELECT DISTINCT PRODUCT_NAME FROM KXZ33978.PRODUCT_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			product_name.append(ibm_db.result(stmt,0))
	
		sql="SELECT DISTINCT SUPPLIER FROM KXZ33978.PRODUCT_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			supplier.append(ibm_db.result(stmt,0))

		sql="SELECT DISTINCT LOCATION FROM KXZ33978.PRODUCT_ADD_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			location.append(ibm_db.result(stmt,0))

		return render_template('view_stocks.html',product_ID=product_ID,product_name=product_name,supplier=supplier,location=location)
	if request.method == 'POST':
		product_details=[]
		product_ID = request.form['id']
		product_name = request.form['name']
		quantity = request.form['quantity']
		qty_1 = request.form['qty_1']
		threshold = request.form['threshold_1']
		supplier = request.form['supplier']
		dop = request.form['dop']
		dop_1 = request.form['dop_1']
		location = request.form['location']
		if product_ID!="None":
			sql="SELECT DISTINCT KXZ33978.PRODUCT_DETAILS.PRODUCT_ID,KXZ33978.PRODUCT_DETAILS.PRODUCT_NAME,KXZ33978.PRODUCT_DETAILS.QUANTITY,SUPPLIER FROM KXZ33978.PRODUCT_DETAILS JOIN PRODUCT_ADD_DETAILS ON KXZ33978.PRODUCT_DETAILS.PRODUCT_ID=KXZ33978.PRODUCT_ADD_DETAILS.PRODUCT_ID WHERE KXZ33978.PRODUCT_DETAILS.PRODUCT_ID="+product_ID
		else:
			sql="SELECT DISTINCT KXZ33978.PRODUCT_DETAILS.PRODUCT_ID,KXZ33978.PRODUCT_DETAILS.PRODUCT_NAME,KXZ33978.PRODUCT_DETAILS.QUANTITY,SUPPLIER FROM KXZ33978.PRODUCT_DETAILS JOIN KXZ33978.PRODUCT_ADD_DETAILS ON KXZ33978.PRODUCT_DETAILS.PRODUCT_ID=KXZ33978.PRODUCT_ADD_DETAILS.PRODUCT_ID "
		if product_name!="None":
			if "WHERE" in sql:
				sql+=" AND KXZ33978.PRODUCT_DETAILS.PRODUCT_NAME='"+product_name+"'"
			else:
				sql+="WHERE KXZ33978.PRODUCT_DETAILS.PRODUCT_NAME='"+product_name+"'"
		if quantity!="None":
			if "WHERE" in sql:
				if qty_1=="lesser than":
					sql+=" AND KXZ33978.PRODUCT_DETAILS.QUANTITY<"+quantity
				elif qty_1=="greater than":
					sql+=" AND KXZ33978.PRODUCT_DETAILS.QUANTITY>"+quantity
			else:
				if qty_1=="lesser than":
					sql+="WHERE KXZ33978.PRODUCT_DETAILS.QUANTITY<"+quantity
				elif qty_1=="greater than":
					print("hi")
					sql+="WHERE KXZ33978.PRODUCT_DETAILS.QUANTITY>"+quantity
		if threshold!="None":
			if "WHERE" in sql:
				if threshold=="lesser than":
					sql+=" AND KXZ33978.PRODUCT_DETAILS.QUANTITY<THRESHOLD_QTY"
				elif threshold=="greater than":
					sql+=" AND KXZ33978.PRODUCT_DETAILS.QUANTITY>THRESHOLD_QTY"
			else:
				if threshold=="lesser than":
					sql+="WHERE KXZ33978.PRODUCT_DETAILS.QUANTITY<THRESHOLD_QTY"
				elif threshold=="greater than":
					sql+="WHERE KXZ33978.PRODUCT_DETAILS.QUANTITY>THRESHOLD_QTY"
		if supplier!="None":
			if "WHERE" in sql:
				sql+=" AND SUPPLIER='"+supplier+"'"
			else:
				sql+="WHERE SUPPLIER='"+supplier+"'"
		if dop!="None":
			if "WHERE" in sql:
				if dop_1=="lesser than":
					sql+=" AND DATE_OF_PURCHASE<'"+dop+"'"
				elif dop_1=="greater than":
					sql+=" AND DATE_OF_PURCHASE>'"+dop+"'"
			else:
				if dop_1=="lesser than":
					sql+="WHERE DATE_OF_PURCHASE<'"+dop+"'"
				elif dop_1=="greater than":
					sql+="WHERE DATE_OF_PURCHASE>'"+dop+"'"
		if location!="None":
			if "WHERE" in sql:
				sql+=" AND LOCATION='"+location+"'"
			else:
				sql+="WHERE LOCATION='"+location+"'"
		print(sql)
		print(quantity)
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			data={}
			data['Product_ID']=ibm_db.result(stmt,0)
			data['Product_name']=ibm_db.result(stmt,1)
			data['quantity']=ibm_db.result(stmt,2)
			data['supplier']=ibm_db.result(stmt,3)
			product_details.append(data)
			# msg = 'You have successfully registered !'
		return render_template('display_items.html',product_details=product_details)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
	
if __name__ == '__main__':
	app.run(debug=True)


