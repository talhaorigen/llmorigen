import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot import APPCFG, ChatBot
from prepare_vectordb import PrepareVectorDB
from upload_file import UploadFile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '83930bHKHKLJE_-wnreknwi43hnwkj4888'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'  
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  

db = SQLAlchemy(app)

import logging

# Configure logging
logging.basicConfig(
    filename='chatbot_history.log',  # Log file path
    level=logging.DEBUG,              # Set to DEBUG for detailed output
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Example usage
logging.info('Chatbot application started')


# Database Model for User Authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  
    full_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))

with app.app_context():
    db.create_all()

u1= User(email= 'ahmad.i@origen.qa',password= "ahmad@123", full_name= 'Ahmad Intisar', contact = "+923048852145")
u2= User(email= 'talha.j@origen.qa',password= "talha@123", full_name= 'Talha Javed', contact = "+923337420315")
u3= User(email= 'ali.s@origen.co',password= "ali@123", full_name= 'Ali Saeed', contact = "+1 5145625713")
u4= User(email= 'abdulaziz.a@origen.qa',password= "aziz@456", full_name= 'Abdul Aziz', contact = "+1 5145625713")
u4= User(email= 'nabeel.a@origen.qa',password= "nabeel@456", full_name= 'Nabeel Asif', contact = "+1 5145625713")

with app.app_context():
    db.session.execute(text('DELETE FROM user'))  
    db.session.add_all([u1,u2, u3, u4])
    db.session.commit()

# Home Route
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('signin'))

# Disabled Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    flash("Request an account from the Origen Account Manager", "danger")
    return redirect(url_for('signin'))

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

        if not user.password == password:
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
    # Print the chatbot history before clearing
    chatbot_history = session.get('chatbot_history', [])
    print("Chatbot history before logout:", chatbot_history)
    
    # Clear the user session and chatbot history
    session.pop('user', None)
    session.pop('chatbot_history', None)  # Clear chat history on logout
    
    # Confirm that the history has been cleared
    cleared_history = session.get('chatbot_history', [])
    print("Chatbot history after clearing:", cleared_history)
    
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
    
    # chatbot_history = []  # Placeholder for user-specific history
    chatbot_history = session.get('chatbot_history', [])

    _, updated_chat, references = ChatBot.respond(chatbot_history, user_input, data_type, temperature)

    session['chatbot_history'] = updated_chat[-APPCFG.number_of_q_a_pairs:]

    return jsonify({"response": updated_chat[-1][1], "references": references})

# 📌 API Endpoint for File Upload and Processing
import shutil

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    if 'files[]' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files[]')  # Get all uploaded files
    data_type = request.form.get('data_type', "Process for RAG")
    temperature = request.form.get('temperature', 0.0)

    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No valid files selected"}), 400

    # Clear the upload folder before saving new files
    upload_folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)  # Remove the directory and its contents
    os.makedirs(upload_folder, exist_ok=True)  # Recreate the directory

    uploaded_files = []
    chatbot_history = []  # Placeholder for user-specific history

    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            uploaded_files.append(file_path)

    # Use session-specific directory for vector database
    user_directory = os.path.join(APPCFG.custom_persist_directory, session['user'])
    os.makedirs(user_directory, exist_ok=True)
    print(f"Files are being saved to: {user_directory}")

    # Process all uploaded files with session-specific directory
    _, updated_chat = UploadFile.process_uploaded_files(uploaded_files, chatbot_history, data_type, user_directory)

    return jsonify({
        "message": "Files uploaded successfully!",
        "chatbot_responses": [chat[1] for chat in updated_chat]  # Collect all responses
    })

# 📌 API Endpoint for File Upload and Processing
@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    # Use session-specific directory for clearing the vector database
    user_directory = os.path.join(APPCFG.custom_persist_directory, session['user'])
    print(f"Clearing cache for directory: {user_directory}")

    prepare_vectordb_instance = PrepareVectorDB(
        data_directory=[],
        persist_directory=user_directory,
        embedding_model_engine=APPCFG.embedding_model_engine,
        chunk_size=APPCFG.chunk_size,
        chunk_overlap=APPCFG.chunk_overlap
    )
    prepare_vectordb_instance.clear_vectordb()
    chatbot_history = session.pop('chatbot_history', [])
    return jsonify({"message": "Vector database and chat history cleared successfully."})

# 📌 API Endpoint for Fetching Available Processing Options
@app.route('/options', methods=['GET'])
def get_options():
    return jsonify({
        "options": ["Process for RAG", "Give Full summary"]
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))  # Default to 7860 if no PORT is set
    #demo.launch(server_name="0.0.0.0", server_port=port)
    print(f"🚀 Flask app running on: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)