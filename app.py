from flask import Flask, url_for, render_template, request, redirect, session, g
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'crudapplication_db'):
        g.crudapplication_db.close()

def get_current_user():
    user = None
    if 'user' in session:
        user = session['user']
        db = get_database()
        user_cur = db.execute('select * from users where name = ?', [user])
        user = user_cur.fetchone()
    return user

@app.route('/')
def index():
    user = get_current_user()
    return render_template('home.html', user = user)

@app.route('/login', methods=["POST","GET"])
def login():
    user = get_current_user()

    error = None
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        db = get_database()
        user_cursor = db.execute('select * from users where name = ?',[name])
        user = user_cursor.fetchone()

        if user:
            if check_password_hash(user['password'],password):
                session["user"] = user["name"]
                return redirect(url_for('dashboard'))
            else:
                error = "Password didn't match"
    return render_template('login.html', loginerror = error, user = user)

@app.route('/register', methods=["POST", "GET"])
def register():
    user = get_current_user()

    if request.method == 'POST':
        db = get_database()
        name = request.form['name']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        dbusers_cur = db.execute('select * from users where name = ?', [name])
        existing_username = dbusers_cur.fetchone()
        if existing_username:
            return render_template('register.html', registererror = 'Error: Username already taken, try different username please. ', user = user)


        db.execute('insert into users (name, password) values (?,?)', [name, hashed_password])
        db.commit()
        return redirect(url_for('index'))
    return render_template('register.html', user = user)

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    return render_template('dashboard.html', user = user)

@app.route('/addneweployee')
def addnewemployee():
    user = get_current_user()
    return render_template('addnewemployee.html', user = user)

@app.route('/singleemployee')
def singleemployeeprofile():
    user = get_current_user()
    return render_template('singleemployeeprofile.html', user = user)

@app.route('/updateemployee')
def updateemployee():
    user = get_current_user()
    return render_template('updateemployee.html', user = user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    render_template('home.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5058)