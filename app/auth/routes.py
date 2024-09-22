import re
import json
from flask import request, jsonify, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .. import db

allowed_usernames = re.compile(r'^[A-Za-z0-9]*$')
allowed_emails = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

@auth.route('/register', methods=['POST'])
def register():
    if not current_app.config['ALLOW_REGISTRATION']:
        return 'Registration is disabled on this server.', 403

    data = request.get_json()
    username = data['username']
    if len(username) < 8 or len(username) > 20:
        return 'Username must be between 8-20 characters long!', 400
    elif not allowed_usernames.match(username):
        return 'Username can only contain A-Z, a-z and 0-9!', 400
    mail = data['mail']
    if not allowed_emails.match(mail):
        return 'Invalid email!', 400
    password = generate_password_hash(data['password'])
    if len(data['password']) < 8 or len(data['password']) > 20:
        return 'Password must be between 8-20 characters long!', 400
    user = User(username=username, password=password, mail=mail, admin=False)
    db.session.add(user)
    db.session.commit()
    return 'User registered successfully!', 201

@auth.route('/login', methods=['POST'])
def login():
    if not current_app.config['ALLOW_LOGIN']:
        return 'Logging in is currently disabled on this server.', 403

    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        login_user(user)
        session['user_id'] = user.id
        return 'Logged in successfully!', 200
    return 'Invalid credentials!', 401

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully', 200