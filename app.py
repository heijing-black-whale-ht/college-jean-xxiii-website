from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# Load dotenv environment keys
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_fallback_development_key')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # <-- Initialize the database engine

# --- MAIL SERVER CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

# --- DATABASE MODEL CONFIGURATION ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    date_str = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="Événement")
    
    def __repr__(self):
        return f'<Event {self.title}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Automatic database generator runner
with app.app_context():
    db.create_all()
     
    # Seed the administrator account safely using environment variables
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        # Pulls from .env; uses a secure fallback if .env is missing locally
        secure_admin_password = os.getenv('ADMIN_PASSWORD', 'admin1234')
        admin.set_password(secure_admin_password)

        db.session.add(admin)
        db.session.commit()
        print("Admin account initialized securely from environment parameters.")

print("\n--- SERVER CONFIG CHECK ---")
print("Loading Mail User as:", app.config['MAIL_USERNAME'])
print("----------------------------\n")

# --- AUTHENTICATION ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Connexion réussie.", "success")
            return redirect(url_for('admin_events'))
        flash("Identifiants incorrects.", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "success")
    return redirect(url_for('login'))

# --- PUBLIC PAGES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/events')
def events():
    public_events = Event.query.order_by(Event.id.desc()).all()
    return render_template('events.html', events=public_events)

# --- BACKEND ADMIN PORTAL FOR EVENTS ---
@app.route('/admin/events', methods=['GET', 'POST'])
@login_required
def admin_events():
    if request.method == 'POST':
        title = request.form.get('title')
        date_str = request.form.get('date_str') 
        description = request.form.get('description')
        category = request.form.get('category')

        if not title or not date_str or not description:
            flash("Veuillez remplir tous les champs obligatoires.", "danger")
            return redirect(url_for('admin_events'))
        
        new_event = Event(title=title, date_str=date_str, description=description, category=category)
        try:
            db.session.add(new_event)
            db.session.commit()
            flash("Nouvel événement publié avec succès !", "success")
        except Exception as e:
            db.session.rollback()
            print(f"Database Write Error: {e}")
            flash("Une erreur est survenue lors de l'enregistrement.", "danger")

        return redirect(url_for('admin_events'))

    current_events = Event.query.order_by(Event.id.desc()).all()
    return render_template('admin_events.html', events=current_events)

@app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event_to_delete = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event_to_delete)
        db.session.commit()
        flash("Événement supprimé avec succès.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Database Delete Error : {e}")
        flash("Impossible de supprimer l'événement.", "danger")
    return redirect(url_for('admin_events'))

@app.route('/admin/events/edit/<int:event_id>', methods=['GET'])
@login_required  # <-- FIXED: Locked down route access to authorized accounts only
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('edit_event.html', event=event)
    
@app.route('/admin/events/update/<int:event_id>', methods=['POST'])
@login_required  # <-- FIXED: Locked down route access to authorized accounts only
def update_event(event_id):
    event = Event.query.get_or_404(event_id)

    title = request.form.get('title')
    date_str = request.form.get('date_str')
    description = request.form.get('description')
    category = request.form.get('category')

    if not title or not date_str or not description:
        flash("Veuillez remplir tous les champs obligatoires.", "danger")
        return redirect(url_for('admin_events'))

    event.title = title
    event.date_str = date_str
    event.description = description
    event.category = category

    try:
        db.session.commit()
        flash("Événement mis à jour avec succès !", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Database Update Error: {e}")
        flash("Erreur lors de la mise à jour.", "danger")
    
    return redirect(url_for('admin_events'))

# --- CONTACT ENDPOINT CONTROLLER ---
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        sender_name = request.form.get('name')
        sender_email = request.form.get('email')
        user_message = request.form.get('message')

        msg = Message (
            subject=f"Nouveau message de {sender_name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=['collegejeanxxiii2000@gmail.com'],
            body=f"De: {sender_name} ({sender_email})\n\nMessage:\n{user_message}"
        )

        msg.body = f"""
        Nouveau message reçu depuis le site internet du Collège Jean XXIII:

        -------------------------------------------------------------------------------------
        Nom complet: {sender_name}
        E-mail de l'expéditeur: {sender_email}
        -------------------------------------------------------------------------------------
        
        Message:
        {user_message}

        -------------------------------------------------------------------------------------
        Remarque: Vous pouvez répondre directement à cet e-mail pour contacter l'expéditeur.
        """
        msg.reply_to = sender_email

        try:
            mail.send(msg)
            flash("Votre message a été envoyé avec succès ! L'administration vous répondra sous peu.", "success")
        except Exception as e:
            print(f"SMTP Server Mail Exception error raised: {e}")
            flash("Une erreur est survenue lors de l'envoi du message. Veuillez réessayer plus tard.", "danger")
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
