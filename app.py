import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-to-something-secret'

# --- DATABASE CONFIGURATION (CRITICAL FIX) ---
# 1. Get the database URL from Render's environment variables
database_url = os.environ.get('DATABASE_URL')

# 2. If we are on Render, fix the URL (postgres:// -> postgresql://)
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# 3. If we are on your computer (no Render URL), use a local file
if not database_url:
    database_url = 'sqlite:///journey.db'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ---------------------------------------------

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- MODELS ---
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(100), nullable=False)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

# --- LOGIN LOGIC ---
@login_manager.user_loader
def load_user(user_id):
    if user_id == '1':
        return User(id='1')
    return None

# --- ROUTES ---

@app.route('/')
def index():
    # Show the latest quote
    try:
        latest_quote = Quote.query.order_by(Quote.id.desc()).first()
    except:
        # If DB isn't created yet, just show nothing
        latest_quote = None
    return render_template('index.html', quote=latest_quote)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcoded credentials
        if username == 'admin' and password == 'admin':
            user = User(id='1')
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Focus and try again.')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        quote_text = request.form.get('quote')
        quote_source = request.form.get('source')
        
        if quote_text and quote_source:
            new_quote = Quote(text=quote_text, source=quote_source)
            db.session.add(new_quote)
            db.session.commit()
            flash('Quote added successfully.')
            
    recent_quotes = Quote.query.order_by(Quote.id.desc()).limit(5).all()
    return render_template('admin.html', quotes=recent_quotes)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- SERVER STARTUP ---
# This ensures tables exist before the app runs
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Use the port defined by Render, or 5000 locally
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
