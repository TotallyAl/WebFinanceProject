#!/usr/bin/env python3
from flask import Flask, render_template, redirect, url_for, request, session
import json

from scripts import Cryptography

app = Flask(__name__)

app.secret_key = 'super secret key'

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register')
async def register():
    if 'user_ID' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login')
async def login():
    if 'user_ID' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register-redirect', methods=['POST', 'GET'])
async def register_redirect():

    if request.method == 'GET':
        return redirect(url_for('register'))

    with open('database/users.json', 'r') as f:
        users_DB = json.load(f)

    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    password = request.form.get('password')

    user_ID = firstname[:2] + lastname
    try:
        if users_DB[user_ID]:
            return {"message": "User already exists"}

    except KeyError:
        salt, hashed_password = Cryptography.Hash.hash_password(password)
        users_DB[user_ID] = {
            'password': hashed_password,
            'salt': salt
        }
        with open('database/users.json', 'w') as f:
            json.dump(users_DB, f, indent=2)
        session['user_ID'] = user_ID
        return redirect(url_for('dashboard'))

@app.route('/login-redirect', methods=['POST', 'GET'])
async def login_redirect():

    if request.method == 'GET':
        return redirect(url_for('login'))

    user_ID = request.form.get('userID')
    password = request.form.get('password')

    with open('database/users.json', 'r') as f:
        users_DB = json.load(f)
    
    try:
        if users_DB[user_ID]:
            print("User exists")
            salt = users_DB[user_ID]['salt']
            _, hashed_login_pwd = Cryptography.Hash.hash_password(password, salt)
            if hashed_login_pwd == users_DB[user_ID]['password']:
                session['user_ID'] = user_ID
                return redirect(url_for('dashboard'))
            else:
                return {"message": "Invalid credentials"}
    except KeyError:
        print("User does not exist")
        return redirect(url_for('register'))


@app.route('/dashboard')
async def dashboard():
    if 'user_ID' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
async def logout():
    session.pop('user_ID', None)
    return redirect(url_for('login'))

### Payment Gateway
@app.route('/payment-add')
async def payment_add():
    pass

@app.route('/payment-history')
async def payment_history():
    articles = [["Title1", "This is the content of article 1"], ["Title2", "This is the content of article 2"], ["Title3", "This is the content of article 3"]]
    return render_template('payment-history.html', articles=articles)

@app.route('/payment-modify')
async def payment_modify():
    pass

if __name__ == '__main__':
    app.run(debug=True, host='10.0.0.4', port=8888)