# import os
# from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from chatbot import ChatBot
# from upload_file import UploadFile
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.secret_key = '83930bHKHKLJE_-wnreknwi43hnwkj4888'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure folder exists

# db = SQLAlchemy(app)

# # Database Model for User Authentication
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)  # Store hashed password
#     full_name = db.Column(db.String(100), nullable=False)
#     contact = db.Column(db.String(100))

# with app.app_context():
#     db.create_all()

# # Home Route
# @app.route('/')
# def home():
#     if 'user' in session:
#         return redirect(url_for('chat'))
#     return redirect(url_for('signin'))

# # Signup Route
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         full_name = request.form['full_name']
#         contact = request.form.get('contact', '')

#         existing_user = User.query.filter_by(email=email).first()
#         if existing_user:
#             flash("User already exists! Try signing in.", "danger")
#             return redirect(url_for('signup'))

#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
#         new_user = User(email=email, password=hashed_password, full_name=full_name, contact=contact)
#         db.session.add(new_user)
#         db.session.commit()
#         session['user'] = email
#         flash("Account created successfully!", "success")
#         return redirect(url_for('chat'))
#     return render_template('signup.html')

# # Signin Route
# @app.route('/signin', methods=['GET', 'POST'])
# def signin():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         user = User.query.filter_by(email=email).first()
#         if not user:
#             flash("User does not exist. Please sign up.", "danger")
#             return redirect(url_for('signin'))

#         if not check_password_hash(user.password, password):
#             flash("Incorrect password!", "danger")
#             return redirect(url_for('signin'))

#         session['user'] = email
#         flash("Logged in successfully!", "success")
#         return redirect(url_for('chat'))
#     return render_template('signin.html')

# # Chat Page Route
# @app.route('/chat')
# def chat():
#     if 'user' not in session:
#         return redirect(url_for('signin'))
#     user = User.query.filter_by(email=session['user']).first()
#     return render_template('chat.html', user=user)

# # Logout Route
# @app.route('/logout')
# def logout():
#     session.pop('user', None)
#     flash("Logged out successfully!", "info")
#     return redirect(url_for('signin'))

# # 📌 API Endpoint for Chatbot Responses
# @app.route('/chatbot', methods=['POST'])
# def chatbot_response():
#     if 'user' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     data = request.json
#     user_input = data.get("message", "")
#     data_type = data.get("data_type", "Preprocessed doc")  # Default data type
#     temperature = float(data.get("temperature", 0.0))  # Default temperature

#     if not user_input:
#         return jsonify({"error": "Message cannot be empty"}), 400

#     chatbot_history = []  # Placeholder for user-specific history
#     _, updated_chat, references = ChatBot.respond(chatbot_history, user_input, data_type, temperature)

#     return jsonify({"response": updated_chat[-1][1], "references": references})

# # 📌 API Endpoint for File Upload
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'user' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     filename = secure_filename(file.filename)
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     file.save(file_path)

#     chatbot_history = []  # Placeholder for user-specific history
#     _, updated_chat = UploadFile.process_uploaded_files([file_path], chatbot_history, "Upload doc: Process for RAG")

#     return jsonify({"message": "File uploaded successfully!", "chatbot_response": updated_chat[-1][1]})

# if __name__ == '__main__':
#     app.run(debug=True)
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot import APPCFG, ChatBot
from upload_file import UploadFile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '83930bHKHKLJE_-wnreknwi43hnwkj4888'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure folder exists

db = SQLAlchemy(app)

# Database Model for User Authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed password
    full_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))

with app.app_context():
    db.create_all()

# Home Route
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('signin'))

# Signup Route
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

# Signin Route
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

# Chat Page Route (Frontend UI)
@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect(url_for('signin'))
    user = User.query.filter_by(email=session['user']).first()
    return render_template('chat.html', user=user)

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('signin'))

# 📌 API Endpoint for Chatbot Responses
@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    user_input = data.get("message", "")
    data_type = data.get("data_type", "Process for RAG")  # Default data type
    print("Data type:" , data_type)
    temperature = float(data.get("temperature", 0.0))  # Default temperature

    if not user_input:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    chatbot_history = []  # Placeholder for user-specific history
    _, updated_chat, references = ChatBot.respond(chatbot_history, user_input, data_type, temperature)

    return jsonify({"response": updated_chat[-1][1], "references": references})

# 📌 API Endpoint for File Upload and Processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    chatbot_history = []  # Placeholder for user-specific history
    _, updated_chat = UploadFile.process_uploaded_files([file_path], chatbot_history, "Give Full Summary")

    return jsonify({"message": "File uploaded successfully!", "chatbot_response": updated_chat[-1][1]})

# 📌 API Endpoint for Fetching Available Processing Options
@app.route('/options', methods=['GET'])
def get_options():
    return jsonify({
        "options": ["Process for RAG", "Give Full summary"]
    })

if __name__ == '__main__':
    app.run(debug=True)
