from flask import render_template
import sqlite3
# import requests
from flask import Flask
from flask import request,redirect,url_for,session,flash
from flask_wtf import Form
from wtforms import TextField
app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/')
def hel():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS users (first_name VARCHAR(50) NOT NULL, last_name VARCHAR(50) NOT NULL, street_number BIGINT NOT NULL, street_name VARCHAR(50) NOT NULL, apt_number VARCHAR(10) NOT NULL, city VARCHAR(50) NOT NULL,  state VARCHAR(50) NOT NULL, zipcode BIGINT NOT NULL, bg TEXT, email TEXT UNIQUE, pass TEXT)')
    print( "Table created successfully")
    conn.close()
    if session.get('username')==True:
        messages = session['username']

    else:
        messages = ""
    user = {'username': messages}
    return redirect(url_for('index',user=user))


@app.route('/reg')
def add():
    return render_template('register.html')


@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   msg = ""
   #con = None
   if request.method == 'POST':
      try:
         first_name = request.form['first_name']
         last_name = request.form['last_name']
         street_number = request.form['street_number']
         street_name = request.form['street_name']
         apt_number = request.form['apt_number']
         city = request.form['city']
         state = request.form['state']
         zipcode = request.form['zipcode']
         bg = request.form['bg']
         email = request.form['email']
         passs = request.form['pass']

         with sqlite3.connect("database.db") as con:
             cur = con.cursor()
             cur.execute("INSERT INTO users (first_name,last_name,street_number,street_name,apt_number,city,state,zipcode,bg,email,pass) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(first_name,last_name,street_number,street_name,apt_number,city,state,zipcode,bg,email,passs) )
             con.commit()
             msg = "Record successfully added"



      except:
             con.rollback()
             msg = "error in insert operation"

      finally:
             flash('done')
             return redirect(url_for('index'))
             con.close()





@app.route('/index',methods = ['POST','GET'])
def index():



    if request.method == 'POST':
        if session.get('username') is not None:
            messages = session['username']

        else:
            messages = ""
        user = {'username': messages}
        print(messages)
        val = request.form['search']
        print(val)
        type = request.form['type']
        print(type)
        if type=='blood':
            con = sqlite3.connect('database.db')
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("select * from users where bg=?",(val,))
            search = cur.fetchall();
            cur.execute("select * from users ")

            rows = cur.fetchall();


            return render_template('index.html', title='Home', user=user,rows=rows,search=search)

        if type=='donorname':
            con = sqlite3.connect('database.db')
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("select * from users where name=?",(val,))
            search = cur.fetchall();
            cur.execute("select * from users ")

            rows = cur.fetchall();


            return render_template('index.html', title='Home', user=user,rows=rows,search=search)



    if session.get('username') is not None:
        messages = session['username']

    else:
        messages = ""
    user = {'username': messages}
    print(messages)
    if request.method=='GET':
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from users ")

        rows = cur.fetchall();
        return render_template('index.html', title='Home', user=user, rows=rows)


@app.route('/list')
def list():
   con = sqlite3.connect('database.db')
   con.row_factory = sqlite3.Row

   cur = con.cursor()
   cur.execute("select * from users")

   rows = cur.fetchall();
   print(rows)
   return render_template("list.html",rows = rows)

@app.route('/drop')
def dr():
        con = sqlite3.connect('database.db')
        con.execute("DROP TABLE request")
        return "dropped successfully"

@app.route('/login',methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('/login.html')
    if request.method == 'POST':
        print(session)
        email = request.form['email']
        password = request.form['pass']
        # if email == 'admin@bloodbank.com' and password == 'admin':       
        a = 'yes'
        session['username'] = email
        #session['logged_in'] = True
        session['admin'] = True
        # return redirect(url_for('index'))
        print((password,email))
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select email,pass,cid from users where email=?",(email,))
        rows = cur.fetchall();
        for row in rows:
            print(row['email'],row['pass'])
            a = row['email']
            session['username'] = a
            session['logged_in'] = True
            session['cid']=row['cid']
            print(a)
            u = {'username': a}
            p = row['pass']
            print(p)
            print(session)
            if email == a and password == p:
                return redirect(url_for('index'))
            else:
                return render_template('/login.html')
        return render_template('/login.html')
    else:
        return render_template('/')


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   session.pop('logged_in',None)
   try:
       session.pop('admin',None)
   except KeyError as e:
       print("I got a KeyError - reason " +str(e))


   return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
   con = sqlite3.connect('database.db')
   con.row_factory = sqlite3.Row

   cur = con.cursor()
   cur.execute("select appliance_type, COUNT(*) from Service_Location_Devices join Customer_Service_Locations on Service_Location_Devices.service_location_id=Customer_Service_Locations.service_location_id join Service_Locations on Service_Locations.service_location_id = Customer_Service_Locations.service_location_id join Device_Appliance_Mapping on Service_Location_Devices.device_id = Device_Appliance_Mapping.device_id join Appliance_Information on Appliance_Information.appliance_id = Device_Appliance_Mapping.appliance_id where cid=? group by appliance_type",(session['cid'],))
   rows3 = cur.fetchall()

   appliance_dictionary={'Fridge':0, 'Lights':0, 'AC':0}
   for row in rows3:
    appliance_dictionary[row[0]]=row[1]

   print(appliance_dictionary)

   cur.execute("select * from Service_Locations join Customer_Service_Locations on Service_Locations.service_location_id=Customer_Service_Locations.service_location_id where cid=?",(session['cid'],))

   rows1 = cur.fetchall();

   cur.execute("select Service_Location_Devices.device_id, Service_Locations.street_number, Service_Locations.street_name, Service_Locations.apt_number, Service_Locations.city, Service_Locations.zipcode, Appliance_Information.appliance_type, Appliance_Information.model from Service_Location_Devices join Customer_Service_Locations on Service_Location_Devices.service_location_id=Customer_Service_Locations.service_location_id join Service_Locations on Service_Locations.service_location_id = Customer_Service_Locations.service_location_id join Device_Appliance_Mapping on Service_Location_Devices.device_id = Device_Appliance_Mapping.device_id join Appliance_Information on Appliance_Information.appliance_id = Device_Appliance_Mapping.appliance_id where cid=?",(session['cid'],))

   rows2 = cur.fetchall();

   return render_template("requestdonors.html",rows1=rows1, rows2=rows2, appliance_dictionary= appliance_dictionary)


@app.route('/bloodbank')
def bl():
    print(session)
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS blood (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, donorname TEXT, donorsex TEXT, qty TEXT, dweight TEXT, donoremail TEXT, phone TEXT)')
    print( "Table created successfully")
    conn.close()
    return render_template('/adddonor.html')

@app.route('/device')
def adddevice():
    print(session)
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS Service_Location_Devices (device_id INTEGER, service_location_id	INTEGER NOT NULL, PRIMARY KEY(device_id), FOREIGN KEY(service_location_id) REFERENCES Service_Locations(service_location_id))')
    print( "Table created successfully")
    cur = conn.cursor()
    cur.execute("select Customer_Service_Locations.service_location_id,street_number,street_name,apt_number,city,state,zipcode from Customer_Service_Locations JOIN Service_Locations on Customer_Service_Locations.service_location_id=Service_Locations.service_location_id where cid=?",(session['cid'],))
    rows = cur.fetchall()
    arr={}
    for row in rows:
        string=''
        for x in row[1:]:
            string+=str(x)+', '
        string=string[:-2]
        arr[row[0]]=string

    cur.execute("select * from Appliance_Information")
    rows1 = cur.fetchall()
    arr1={}
    for row in rows1:
        string=''
        for x in row[1:]:
            string+=str(x)+': '
        string=string[:-2]
        arr1[row[0]]=string
    conn.close()
    return render_template('/adddevice.html',rows=arr, rows1=arr1)


@app.route('/addb',methods =['POST','GET'])
def addb():
    msg = ""
    print(session)
    if request.method == 'POST':
        try:
            street_number = request.form['street_number']
            street_name = request.form['street_name']
            apt_number = request.form['apt_number']
            city = request.form['city']
            state = request.form['state']
            zipcode = request.form['zipcode']
            square_footage = request.form['square_footage']
            num_bedrooms = request.form['num_bedrooms']
            num_occupants = request.form['num_occupants']
            move_in_date = request.form['move_in_date']

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Service_Locations (street_number, street_name, apt_number, city,state, zipcode, square_footage, num_bedrooms, num_occupants) VALUES (?,?,?,?,?,?,?,?,?)",(street_number, street_name, apt_number, city,state, zipcode, square_footage, num_bedrooms, num_occupants) )
                con.commit()
                cur.execute('select service_location_id from Service_Locations where street_number=? and street_name=? and apt_number=?',(street_number,street_name,apt_number,))
                row = cur.fetchone()
                cur.execute("INSERT INTO Customer_Service_Locations (cid, service_location_id, move_in_date) VALUES (?,?,?)",(session['cid'], row[0], move_in_date) )

                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return redirect(url_for('dashboard'))
            con.close()

    else:
        return render_template("rest.html",msg=msg)

@app.route('/adddevicedb',methods =['POST','GET'])
def adddevicedb():
    msg = ""
    print(session)
    if request.method == 'POST':
        try:
            form_data = request.form  
            for key, value in form_data.items():
                if key=='service_location_id':
                    service_location_id=int(value)
                else:
                    appliance_id=int(value)

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Service_Location_Devices (service_location_id) VALUES (?)",(service_location_id,) )
                con.commit()
                cur.execute('select MAX(device_id) from Service_Location_Devices where service_location_id = ?',(service_location_id,))
                row = cur.fetchone()
                cur.execute("INSERT INTO Device_Appliance_Mapping (device_id, appliance_id) VALUES (?,?)",(row[0], appliance_id,) )
                con.commit()
                msg = "Record successfully added"
            
           
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return redirect(url_for('dashboard'))
            con.close()

    else:
        return render_template("rest.html",msg=msg)

@app.route("/editdonor/<id>", methods=('GET', 'POST'))
def editdonor(id):
    msg =""
    if request.method == 'GET':
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from blood where id=?",(id,))
        rows = cur.fetchall();
        return render_template("editdonor.html",rows = rows)
    if request.method == 'POST':
        try:
           type = request.form['blood_group']
           donorname = request.form['donorname']
           donorsex = request.form['gender']
           qty = request.form['qty']
           dweight = request.form['dweight']
           email = request.form['email']
           phone = request.form['phone']



           with sqlite3.connect("database.db") as con:
              cur = con.cursor()
              cur.execute("UPDATE blood SET type = ?, donorname = ?, donorsex = ?, qty = ?,dweight = ?, donoremail = ?,phone = ? WHERE id = ?",(type,donorname,donorsex,qty,dweight,email,phone,id) )
              con.commit()
              msg = "Record successfully updated"
        except:
           con.rollback()
           msg = "error in insert operation"

        finally:
            flash('saved successfully')
            return redirect(url_for('dashboard'))
            con.close()

@app.route("/myprofile/<email>", methods=('GET', 'POST'))
def myprofile(email):
    msg =""
    if request.method == 'GET':


        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from users where email=?",(email,))
        rows = cur.fetchall();
        return render_template("myprofile.html",rows = rows)
    if request.method == 'POST':
        try:
           name = request.form['name']
           addr = request.form['addr']
           city = request.form['city']
           pin = request.form['pin']
           bg = request.form['bg']
           emailid = request.form['email']


           with sqlite3.connect("database.db") as con:
              cur = con.cursor()
              cur.execute("UPDATE users SET name = ?, addr = ?, city = ?, pin = ?,bg = ?, email = ? WHERE email = ?",(name,addr,city,pin,bg,emailid,email) )
              con.commit()
              msg = "Record successfully updated"
        except:
           con.rollback()
           msg = "error in insert operation"

        finally:
           flash('profile saved')
           return redirect(url_for('index'))
           con.close()



@app.route('/contactforblood/<emailid>', methods=('GET', 'POST'))
def contactforblood(emailid):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        print("Opened database successfully")
        conn.execute('CREATE TABLE IF NOT EXISTS request (id INTEGER PRIMARY KEY AUTOINCREMENT, toemail TEXT, formemail TEXT, toname TEXT, toaddr TEXT)')
        print( "Table created successfully")
        fromemail = session['username']
        name = request.form['nm']
        addr = request.form['add']

        print(fromemail,emailid)
        conn.execute("INSERT INTO request (toemail,formemail,toname,toaddr) VALUES (?,?,?,?)",(emailid,fromemail,name,addr) )
        conn.commit()
        conn.close()
        flash('request sent')
        return redirect(url_for('index'))
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        print("Opened database successfully")
        conn.execute('CREATE TABLE IF NOT EXISTS request (id INTEGER PRIMARY KEY AUTOINCREMENT, toemail TEXT, formemail TEXT, toname TEXT, toaddr TEXT)')
        print( "Table created successfully")
        fromemail = session['username']
        name = request.form['nm']
        addr = request.form['add']

        print(fromemail,emailid)
        conn.execute("INSERT INTO request (toemail,formemail,toname,toaddr) VALUES (?,?,?,?)",(emailid,fromemail,name,addr) )
        conn.commit()
        conn.close()
        flash('request sent')
        return redirect(url_for('index'))



@app.route('/notifications',methods=('GET','POST'))
def notifications():
    if request.method == 'GET':
            conn = sqlite3.connect('database.db')
            print("Opened database successfully")
            conn.row_factory = sqlite3.Row

            cur = conn.cursor()
            cor = conn.cursor()
            cur.execute('select * from request where toemail=?',(session['username'],))
            cor.execute('select * from request where toemail=?',(session['username'],))
            row = cor.fetchone();
            rows = cur.fetchall();
            if row==None:
                return render_template('notifications.html')
            else:
                return render_template('notifications.html',rows=rows)


@app.route('/deleteuser/<useremail>',methods=('GET', 'POST'))
def deleteuser(useremail):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from users Where email=?',(useremail,))
        flash('deleted user:'+useremail)
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))


@app.route('/deletebloodentry/<id>',methods=('GET', 'POST'))
def deletebloodentry(id):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from blood Where id=?',(id,))
        flash('deleted entry:'+id)
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

@app.route('/deleteservicelocation/<id>',methods=('GET', 'POST'))
def deleteservicelocation(id):
    if request.method == 'GET':
        print('inside the sl delete api')
        print(id)
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from Service_Locations Where service_location_id=?',(id,))
        conn.commit()
        cur.execute('delete from Customer_Service_Locations Where service_location_id=?',(id,))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

@app.route('/deletedevice/<id>',methods=('GET', 'POST'))
def deletedevice(id):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from Service_Location_Devices Where device_id=?',(id,))
        conn.commit()
        cur.execute('delete from Device_Appliance_Mapping Where device_id=?',(id,))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

@app.route('/deleteme/<useremail>',methods=('GET', 'POST'))
def deleteme(useremail):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from users Where email=?',(useremail,))
        flash('deleted user:'+useremail)
        conn.commit()
        conn.close()
        session.pop('username', None)
        session.pop('logged_in',None)
        return redirect(url_for('index'))

@app.route('/deletenoti/<id>',methods=('GET', 'POST'))
def deletenoti(id):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from request Where id=?',(id,))
        flash('deleted notification:'+id)
        conn.commit()
        conn.close()
        return redirect(url_for('notifications'))



if __name__ == '__main__':
    app.run(debug=True)
