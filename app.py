import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '83930bHKHKLJE_-wnreknwi43hnwkj4888'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed password
    full_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('signin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        contact = request.form.get('contact', '')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists! Try signing in.", "danger")
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password, full_name=full_name, contact=contact)
        db.session.add(new_user)
        db.session.commit()
        session['user'] = email
        flash("Account created successfully!", "success")
        return redirect(url_for('chat'))
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("User does not exist. Please sign up.", "danger")
            return redirect(url_for('signin'))
        
        if not check_password_hash(user.password, password):
            flash("Incorrect password!", "danger")
            return redirect(url_for('signin'))
        
        session['user'] = email
        flash("Logged in successfully!", "success")
        return redirect(url_for('chat'))
    return render_template('signin.html')

@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect(url_for('signin'))
    user = User.query.filter_by(email=session['user']).first()
    return render_template('chat.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)
