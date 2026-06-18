from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load dotenv environment keys
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))



app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_fallback_development_key')

# --- DATABASE CONFIGURATION ---
# This creates a 'school.db' file inside the main project folder layer
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # <-- Initialize the database engine

# --- MAIL SERVER CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # IF using Gmail SMTP
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# Add string fallbacks so if the .env fails to read, the app used them directly
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME') # The school's email address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') # App password (NOT personal password)
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

# --- DATABASE MODEL CONFIGURATION ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)  # e.g., "Remise des bulletins"
    date_str = db.Column(db.String(50), nullable=False) # e.g., "25 Juin 2026"
    description = db.Column(db.Text, nullable=False) # Detailed announcement info
    category = db.Column(db.String(50), nullable=False, default="Événement")
    def __repr__(self):
        return f'<Event {self.title}>'

# Automatic database generator runner
with app.app_context():
    db.create_all() # Generates the local .db file and tables  automatically if missing

# Quick diagnostic print when the server starts up
print("\n--- SERVER CONFIG CHECK ---")
print("Loading Mail User as:", app.config['MAIL_USERNAME'])
print("----------------------------\n")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/events')
def events():
    # Fetch every single event row currently saved in the database file
    public_events = Event.query.order_by(Event.id.desc()).all()
    # Pass the database items directly into the existing HTML layout engine
    return render_template('events.html', events=public_events)

# --- BACKEND ADMIN PORTAL FOR EVENTS ---
@app.route('/admin/events', methods=['GET', 'POST'])
def admin_events():
    if request.method == 'POST':
        # Grab details from the new event creation form inputs
        title = request.form.get('title')
        date_str = request.form.get('date_str') 
        description = request.form.get('description')
        category = request.form.get('category')

        if not title or not date_str or not description:
            flash("Veuillez remplir tous les champs obligatoires.", "danger")
            return redirect(url_for('admin_events'))
        
        # Instantiate a new Database Object row
        new_event = Event(title=title, date_str=date_str, description=description, category=category)
        try:
            db.session.add(new_event) # Stage the data record change
            db.session.commit()       # Write the record to the sqlite file permanently
            flash("Nouvel événement publié avec succès !", "success")
        except Exception as e:
            db.session.rollback()
            print(f"Database Write Error: {e}")
            flash("Une erreur est survenue lors de l'enregistrement.", "danger")

        return redirect(url_for('admin_events'))

    # GET Request: fetch all current events so the admin can review or audit them
    current_events = Event.query.order_by(Event.id.desc()).all()
    return render_template('admin_events.html', events=current_events)


# --- ROUTE TO DELETE AN EVENT (UN-NESTED & FLUSH TO THE LEFT MARGIN) ---
@app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
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
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('edit_event.html', event=event)
    
@app.route('/admin/events/update/<int:event_id>', methods=['POST'])
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
        # 1. Extract the secure form payloads using the HTML 'name' attributes
        sender_name = request.form.get('name')
        sender_email = request.form.get('email')
        user_message = request.form.get('message')

        # 2. Construct the actual email payload
        msg = Message (
            subject=f"Nouveau message de {sender_name}",
            sender=app.config['MAIL_USERNAME'], # Pulls directly from the clean config
            recipients=['collegejeanxxiii2000@gmail.com'],  # Where the school actually checks email
            body=f"De: {sender_name} ({sender_email})\n\nMessage:\n{user_message}"
        )

        # Format a professional email body layout for the school administrators
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
        # Override the reply-to header so when the school clicks "Reply", it replies to the  parent/user, not themselves
        msg.reply_to = sender_email

        try:
            # 3. Fire the email engine out to the real world
            mail.send(msg)
            flash("Votre message a été envoyé avec succès ! L'administration vous répondra sous peu.", "success")
        except Exception as e:
            print(f"SMTP Server Mail Exception error raised: {e}")
            flash("Une erreur est survenue lors de l'envoi du message. Veuillez réessayer plus tard.", "danger")
        
        return redirect(url_for('contact'))
    
    # If HTTP request is normal 'GET' page load, just serve the interface view
    return render_template('contact.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')