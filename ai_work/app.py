from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_cloud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')  # user or admin

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # computing, lora, prompt
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user, remember=remember)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    applications = Application.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', applications=applications)

@app.route('/apply/computing', methods=['GET', 'POST'])
@login_required
def apply_computing():
    if request.method == 'POST':
        gpu_model = request.form['gpu_model']
        memory = request.form['memory']
        duration = request.form['duration']
        
        details = f"GPU Model: {gpu_model}, Memory: {memory}, Duration: {duration}"
        new_application = Application(
            user_id=current_user.id,
            type='computing',
            status='rejected',  # 自动设置为已否决
            details=details
        )
        db.session.add(new_application)
        db.session.commit()
        
        flash('Application submitted and rejected')
        return redirect(url_for('dashboard'))
    return render_template('apply_computing.html')

@app.route('/apply/lora', methods=['GET', 'POST'])
@login_required
def apply_lora():
    if request.method == 'POST':
        base_model = request.form['base_model']
        data_description = request.form['data_description']
        parameters = request.form['parameters']
        
        details = f"Base Model: {base_model}, Data: {data_description}, Parameters: {parameters}"
        new_application = Application(
            user_id=current_user.id,
            type='lora',
            status='rejected',  # 自动设置为已否决
            details=details
        )
        db.session.add(new_application)
        db.session.commit()
        
        flash('Application submitted and rejected')
        return redirect(url_for('dashboard'))
    return render_template('apply_lora.html')

@app.route('/apply/prompt', methods=['GET', 'POST'])
@login_required
def apply_prompt():
    if request.method == 'POST':
        template = request.form['template']
        requirements = request.form['requirements']
        scenario = request.form['scenario']
        
        details = f"Template: {template}, Requirements: {requirements}, Scenario: {scenario}"
        new_application = Application(
            user_id=current_user.id,
            type='prompt',
            status='rejected',  # 自动设置为已否决
            details=details
        )
        db.session.add(new_application)
        db.session.commit()
        
        flash('Application submitted and rejected')
        return redirect(url_for('dashboard'))
    return render_template('apply_prompt.html')

@app.route('/services')
def services():
    return render_template('services.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)