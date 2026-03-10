from flask import Flask, render_template, request, redirect, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from docx import Document
import os

from config import Config
from database import db, User, Document as DocModel

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

    # Create default admin if not exists
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            role="Admin"
        )
        db.session.add(admin)
        db.session.commit()

os.makedirs(Config.GENERATED_FOLDER, exist_ok=True)

# ---------------- ROUTES ---------------- #

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect("/dashboard")

    return "Invalid Credentials"

@app.route("/dashboard")
@login_required
def dashboard():
    documents = DocModel.query.all()
    return render_template("dashboard.html", documents=documents)

@app.route("/create_notice")
@login_required
def create_notice():
    return render_template("create_notice.html")

@app.route("/generate_notice", methods=["POST"])
@login_required
def generate_notice():

    title = request.form["title"]
    department = request.form["department"]
    date = request.form["date"]
    message = request.form["message"]
    authority = request.form["authority"]

    doc = Document(Config.TEMPLATE_PATH)

    for p in doc.paragraphs:
        p.text = p.text.replace("{{TITLE}}", title)
        p.text = p.text.replace("{{DEPARTMENT}}", department)
        p.text = p.text.replace("{{DATE}}", date)
        p.text = p.text.replace("{{MESSAGE}}", message)
        p.text = p.text.replace("{{AUTHORITY}}", authority)

    filename = f"{title.replace(' ', '_')}.docx"
    filepath = os.path.join(Config.GENERATED_FOLDER, filename)
    doc.save(filepath)

    # Save to database
    new_doc = DocModel(
        title=title,
        department=department,
        date=date,
        authority=authority,
        filename=filename
    )

    db.session.add(new_doc)
    db.session.commit()

    return send_file(filepath, as_attachment=True)

# ✅ DOWNLOAD ROUTE ADDED HERE
@app.route("/generated_docs/<filename>")
@login_required
def download_file(filename):
    filepath = os.path.join(Config.GENERATED_FOLDER, filename)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    
    return "File not found", 404


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)