import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
# Use SQLite for simplicity
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Database Models ---
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(100), nullable=False)

# --- User Loader (Hardcoded for this example) ---
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == '1':
        return User(id='1')
    return None

# --- Routes ---

# 1. Visitor Page (Greeting, Latest Quote, About)
@app.route('/')
def index():
    # Get the latest quote added
    latest_quote = Quote.query.order_by(Quote.id.desc()).first()
    return render_template('index.html', quote=latest_quote)

# 2. Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Hardcoded credentials as requested
        if username == 'admin' and password == 'admin':
            user = User(id='1')
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Focus and try again.')
    return render_template('login.html')

# 3. Admin Dashboard (Add Quote)
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        quote_text = request.form['quote']
        quote_source = request.form['source']
        if quote_text and quote_source:
            new_quote = Quote(text=quote_text, source=quote_source)
            db.session.add(new_quote)
            db.session.commit()
            flash('Quote added to the journey.')
    
    # Show last 5 quotes
    recent_quotes = Quote.query.order_by(Quote.id.desc()).limit(5).all()
    return render_template('admin.html', quotes=recent_quotes)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Create DB if it doesn't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
  
