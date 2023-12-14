from flask import render_template
import sqlite3
from flask import Flask
from flask import request,redirect,url_for,session,flash
from flask.json import jsonify
from flask_wtf import Form
from wtforms import TextField
app = Flask(__name__)
app.secret_key = "super secret key"
from datetime import datetime,timedelta
from collections import defaultdict

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
        val = request.form['search']
        type = request.form['type']
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
        email = request.form['email']
        password = request.form['pass']
        # if email == 'admin@bloodbank.com' and password == 'admin':       
        a = 'yes'
        session['username'] = email
        #session['logged_in'] = True
        session['admin'] = True
        # return redirect(url_for('index'))

        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select email,pass,cid from users where email=?",(email,))
        rows = cur.fetchall();
        for row in rows:
            a = row['email']
            session['username'] = a
            session['logged_in'] = True
            session['cid']=row['cid']
            u = {'username': a}
            p = row['pass']
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


   cur.execute("select * from Service_Locations join Customer_Service_Locations on Service_Locations.service_location_id=Customer_Service_Locations.service_location_id where cid=?",(session['cid'],))

   rows1 = cur.fetchall();

   cur.execute("select Service_Location_Devices.device_id, Service_Locations.street_number, Service_Locations.street_name, Service_Locations.apt_number, Service_Locations.city, Service_Locations.zipcode, Appliance_Information.appliance_type, Appliance_Information.model from Service_Location_Devices join Customer_Service_Locations on Service_Location_Devices.service_location_id=Customer_Service_Locations.service_location_id join Service_Locations on Service_Locations.service_location_id = Customer_Service_Locations.service_location_id join Device_Appliance_Mapping on Service_Location_Devices.device_id = Device_Appliance_Mapping.device_id join Appliance_Information on Appliance_Information.appliance_id = Device_Appliance_Mapping.appliance_id where cid=?",(session['cid'],))

   rows2 = cur.fetchall()

   data = {
        'labels': ['Category 1', 'Category 2', 'Category 3', 'Category 4'],
        'values': [20, 35, 25, 40]
    }

   return render_template("dashboard.html",rows1=rows1, rows2=rows2, appliance_dictionary=appliance_dictionary, data=data)

@app.route('/get_weekly_data')
def get_weekly_data():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    today = datetime.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    formatted_dates = [date.strftime('%m-%d-%Y') for date in last_7_days]
    date_dict = {key: 0 for key in formatted_dates}
    cur.execute("select consumption_time,energy_consumed from Service_Location_Devices join Customer_Service_Locations on Service_Location_Devices.service_location_id=Customer_Service_Locations.service_location_id join Service_Locations on Service_Locations.service_location_id = Customer_Service_Locations.service_location_id join Energy_Consumption on Service_Location_Devices.device_id=Energy_Consumption.device_id where cid=?",(session['cid'],))
    rows=cur.fetchall()
    for row in rows:
        ctime=row[0].split(' ')
        date=ctime[0]
        if date in date_dict:
            date_dict[date]+=row[1]
    arr=date_dict.items()
    labels=[]
    values=[]
    for item in arr:
        labels.append(item[0])
        values.append(item[1])
    data = {
        'labels': labels,
        'values': values
    }
    return jsonify(data)

@app.route('/get_monthly_data')
def get_monthly_data():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    months=['09','10','11','12']
    date_dict = {key: 0 for key in months}
    cur.execute("select consumption_time,energy_consumed from Service_Location_Devices join Customer_Service_Locations on Service_Location_Devices.service_location_id=Customer_Service_Locations.service_location_id join Service_Locations on Service_Locations.service_location_id = Customer_Service_Locations.service_location_id join Energy_Consumption on Service_Location_Devices.device_id=Energy_Consumption.device_id where cid=?",(session['cid'],))
    rows=cur.fetchall()
    for row in rows:
        ctime=row[0].split(' ')
        date=ctime[0]
        temp=date.split('-')
        month=temp[0]
        if month in date_dict:
            date_dict[month]+=row[1]
    arr=date_dict.items()
    values=[]
    for item in arr:
        values.append(item[1])
    data = {
        'labels': ['Sept', 'Oct', 'Nov', 'Dec'],
        'values': values
    }
    return jsonify(data)


@app.route('/get_device_day_data')
def get_device_day_data():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    device_dict={'Fridge':0, 'Lights':0, 'AC':0}
    today = datetime.now().date().strftime('%m-%d-%Y')
    cur.execute("select consumption_time,appliance_type, SUM(energy_consumed) from Service_Location_Devices join Customer_Service_Locations on Service_Location_Devices.service_location_id=Customer_Service_Locations.service_location_id join Service_Locations on Service_Locations.service_location_id = Customer_Service_Locations.service_location_id join Energy_Consumption on Service_Location_Devices.device_id=Energy_Consumption.device_id join Device_Appliance_Mapping on Device_Appliance_Mapping.device_id= Service_Location_Devices.device_id join  Appliance_Information on Appliance_Information.appliance_id=Device_Appliance_Mapping.appliance_id where cid=? GROUP BY appliance_type,consumption_time",(session['cid'],))
    rows=cur.fetchall()
    for row in rows:
        ctime=row[0].split(' ')
        date=ctime[0]
        if date==today:
            device_dict[row[1]]+=row[2]
    arr=device_dict.items()
    labels=[]
    values=[]
    for item in arr:
        labels.append(item[0])
        values.append(item[1])
    data = {
        'labels': labels,
        'values': values
    }
    return jsonify(data)

@app.route('/get_grouped_bar_data')
def get_grouped_bar_data():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    today = datetime.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    formatted_dates = [date.strftime('%m-%d-%Y') for date in last_7_days]
    cur.execute("select price_change_time,zipcode,unit_cost FROM Energy_Price WHERE zipcode IN (select zipcode from Service_Location_Devices join Customer_Service_Locations on Service_Location_Devices.service_location_id=Customer_Service_Locations.service_location_id join Service_Locations on Service_Locations.service_location_id = Customer_Service_Locations.service_location_id  where cid=?) ORDER BY zipcode, price_change_time",(session['cid'],))
    rows=cur.fetchall()
    temp_dict=defaultdict(list)
    for row in rows:
        if row[1] not in temp_dict:
            temp_dict[row[1]]=[]
        temp_dict[row[1]].append(row[2])

    colors = ["rgba(255, 99, 132, 0.2)", "rgba(54, 162, 235, 0.2)", "rgba(255, 206, 86, 0.2)", "rgba(75, 192, 192, 0.2)"]

    datasets = []

    for i, (label, values) in enumerate(temp_dict.items()):
        color_index = i % len(colors)
        group_data = {
            "label": f"{label}",
            "data": values,
            "backgroundColor": colors[color_index],
            "borderColor": colors[color_index].replace("0.2", "1"),
            "borderWidth": 1
        }
        datasets.append(group_data)
  
    data = {
        "labels": formatted_dates,
        "datasets": datasets
    }
    return jsonify(data)


@app.route('/bloodbank')
def bl():
    conn = sqlite3.connect('database.db')
    conn.execute('CREATE TABLE IF NOT EXISTS blood (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, donorname TEXT, donorsex TEXT, qty TEXT, dweight TEXT, donoremail TEXT, phone TEXT)')
    print( "Table created successfully")
    conn.close()
    return render_template('/addservicelocation.html')

@app.route('/device')
def adddevice():
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

@app.route('/insights')
def insights():
    return render_template('/insights.html')


@app.route('/addb',methods =['POST','GET'])
def addb():
    msg = ""
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

@app.route('/deleteservicelocation/<id>',methods=('GET', 'POST'))
def deleteservicelocation(id):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from Service_Location_Devices Where service_location_id=?',(id,))
        conn.commit()
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


if __name__ == '__main__':
    app.run(debug=True)
