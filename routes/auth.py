from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(request.url)

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome {user.username}!", "success")
            return redirect(url_for('images.home'))
        else:
            flash("Invalid credentials!", "danger")
            return redirect(request.url)
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('auth.login'))

def current_user():
    from models import User
    from flask import session
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None
