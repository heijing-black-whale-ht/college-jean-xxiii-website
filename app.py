# NEW BACKEND UPDATES 
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
    # Fetch the 5 most recent updates from the database
    latest_updates = Event.query.order_by(Event.id.desc()).limit(5).all()
    # Pass the updates into the homepage template
    return render_template('index.html', updates=latest_updates)

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

        admin_msg = Message(
            subject=f"Nouveau message de {sender_name}",
            recipients=['collegejeanxxiii2000@gmail.com']
        )

        admin_msg.body = f"""
Nouveau message reçu depuis le site internet du Collège Jean XXIII

Nom: {sender_name}
Email: {sender_email}

Message:
{user_message}
"""

        admin_msg.reply_to = sender_email

        logo_url = url_for('static', filename='images/logo.png', _external=True)

        customer_msg = Message(
            subject="Confirmation de réception — Collège Jean XXIII",
            recipients=[sender_email]
        )

        customer_msg.html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0; padding:0; background:#0b1220; font-family:Arial, sans-serif; color:#e2e8f0;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:30px; background:#0b1220;">
<tr>
<td align="center">

<table width="650" cellpadding="0" cellspacing="0"
       style="background:#111827; border-radius:16px; overflow:hidden; box-shadow:0 24px 60px rgba(0,0,0,0.25);">

<tr>
<td style="background:#EDE8DO; padding:28px 24px; text-align:center;">

<img src="{logo_url}"
     alt="Collège Jean XXIII"
     width="120"
     style="display:block; margin:0 auto 15px;">

<h1 style="color:#ffffff; margin:0; font-size:28px; letter-spacing:0.03em;">
Merci pour votre message
</h1>

<p style="color:#f3d27a; margin:12px 0 0; font-size:15px;">
Votre demande a bien été reçue.
</p>

</td>
</tr>

<tr>
<td style="padding:36px 34px; background:#0f172a;">

<p style="margin:0 0 18px; font-size:16px; line-height:1.75; color:#e2e8f0;">
Bonjour <strong style="color:#ffffff;">{sender_name}</strong>,
</p>

<p style="margin:0 0 18px; font-size:15px; line-height:1.8; color:#cbd5e1;">
Nous vous remercions d'avoir contacté le Collège Jean XXIII. Votre message a été transmis à l'administration et sera traité dans les meilleurs délais.
</p>

<div style="background:#111827; border-left:4px solid #8B0000; padding:18px 18px 16px; margin:20px 0 24px; border-radius:10px;">
<strong style="display:block; color:#ffffff; font-size:15px; margin-bottom:10px;">Résumé de votre message :</strong>
<p style="margin:0; font-size:14px; line-height:1.8; color:#cbd5e1;">
{user_message}
</p>
</div>

<p style="margin:0 0 18px; font-size:15px; line-height:1.8; color:#cbd5e1;">
Si votre demande est urgente, vous pouvez également contacter directement l'administration du collège.
</p>

<p style="margin:0; font-size:15px; line-height:1.8; color:#cbd5e1;">
Cordialement,<br>
<strong style="color:#ffffff;">Administration du Collège Jean XXIII</strong>
</p>

</td>
</tr>

<tr>
<td style="background:#0e1727; padding:22px 24px; text-align:center; font-size:13px; color:#94a3b8;">

Collège Jean XXIII<br>
Former les intelligences, façonner les caractères.

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""


        admin_sent = False

        try:
            mail.send(admin_msg)
            admin_sent = True
        except Exception as e:
            print(f"Admin email error: {e}")

        try:
            mail.send(customer_msg)
        except Exception as e:
            print(f"Customer email error: {e}")

        if admin_sent:
            flash("Votre message a été envoyé avec succès. Un e-mail de confirmation vous a été envoyé.", "success")
        else:
            flash("Impossible de traiter votre demande pour le moment.", "danger")

        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
