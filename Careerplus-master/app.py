from flask import Flask,render_template,request,redirect, url_for, session, flash, abort,jsonify
from flask_pymongo import PyMongo
from datetime import datetime
from bson import ObjectId
from cryptography.fernet import Fernet
app = Flask(__name__)

# mongodb connection
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Carrierplus'
app.config['SECRET_KEY'] = 'afdglnalnheognohe'
mongo = PyMongo(app)


#cryptography fernet
# Fernet key setup for encryption/decryption
file = open('key.key', 'rb')
key = file.read()
file.close()
f = Fernet(key)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def loginuser():
  if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        radio = request.form['radiobtn']

        user = mongo.db.register.find_one({'email': email,'type': radio})

    
        if user:
            test = f.decrypt(user['password']).decode()
            if test == password:
              session['loginuser'] = True
              session['user'] = str(user['_id'])
              session['userid'] = user['userid']
              use = session['userid']
              return redirect(url_for('dashboard', us=use))
            else:
              flash('Invalid username or password', 'error')  # Flash an error message
              return redirect(url_for('loginuser'))
        else:
              flash('Invalid username or password', 'error')  # Flash an error message
              return redirect(url_for('loginuser'))   

  return render_template('login.html')
  


@app.route('/signup',methods=['GET','POST'])
def signup():
  if request.method == 'POST':
        try:
            userid = request.form['username']
            email = request.form['email']
            password = request.form['password']
            repass = request.form['confirm_password']
            radio = request.form['radiobtn']
           

            if password == repass:
                user = mongo.db.register.find_one({'userid': userid})
                if user:
                    flash('Email or username already exists', 'error')  # Flash an error message
                    return redirect(url_for('signup'))
                
                else:
                    password = f.encrypt(password.encode()).decode()
                    users = {'userid': userid, 'email': email, 'password': password,'type': radio ,'date_created': datetime.utcnow()}
                    mongo.db.register.insert_one(users)
            else:
                return redirect(url_for('register'))

            return redirect(url_for('dashboard', us = userid))
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return "An error occurred while registering. Please try again."

  return render_template('signup.html')
     

@app.route('/Dashboard/<us>')
def dashboard(us):
    return render_template('Dashboard.html',us=us)     
  


if __name__ == "__main__":
    app.run(debug=True ,port = 8080)