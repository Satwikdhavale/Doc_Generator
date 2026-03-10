from flask import Flask, render_template, request, redirect, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from docx import Document
import os

from config import Config
from database import db, User, Template, Document as DocModel

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

    # Create default users
    if not User.query.filter_by(username="admin").first():
        users = [
            User(username="admin", password=generate_password_hash("admin123"), role="admin"),
            User(username="faculty", password=generate_password_hash("123"), role="faculty"),
            User(username="hod", password=generate_password_hash("123"), role="hod"),
            User(username="dean", password=generate_password_hash("123"), role="dean"),
            User(username="student", password=generate_password_hash("123"), role="student"),
        ]
        db.session.add_all(users)
        db.session.commit()

    # Create templates if not exists
    if not Template.query.first():
        templates = [

            # STUDENT LEVEL
            Template(name="Bonafide Certificate",
                     file_path="doc_templates/bonafide_template.docx",
                     allowed_roles="student,admin"),

            Template(name="NOC Request",
                     file_path="doc_templates/noc_template.docx",
                     allowed_roles="student,admin"),

            Template(name="Internship Permission Request",
                     file_path="doc_templates/internship_request.docx",
                     allowed_roles="student,admin"),

            Template(name="Leave Application",
                     file_path="doc_templates/leave_application.docx",
                     allowed_roles="student,admin"),

            # FACULTY LEVEL
            Template(name="Recommendation Letter",
                     file_path="doc_templates/recommendation.docx",
                     allowed_roles="faculty,hod,admin"),

            Template(name="Internship Approval",
                     file_path="doc_templates/internship_approval.docx",
                     allowed_roles="faculty,hod,admin"),

            Template(name="Meeting Minutes",
                     file_path="doc_templates/meeting_minutes.docx",
                     allowed_roles="faculty,hod,admin"),

            Template(name="Event Certificate",
                     file_path="doc_templates/event_certificate.docx",
                     allowed_roles="faculty,hod,admin"),

            Template(name="Notice Draft",
                     file_path="doc_templates/notice_draft.docx",
                     allowed_roles="faculty,hod,admin"),

            # HOD LEVEL
            Template(name="Official Notice",
                     file_path="doc_templates/official_notice.docx",
                     allowed_roles="hod,admin"),

            Template(name="Circular",
                     file_path="doc_templates/circular.docx",
                     allowed_roles="hod,dean,admin"),

            Template(name="Department Letter",
                     file_path="doc_templates/department_letter.docx",
                     allowed_roles="hod,admin"),

            Template(name="Workload Allocation",
                     file_path="doc_templates/workload_allocation.docx",
                     allowed_roles="hod,admin"),

            # DEAN LEVEL
            Template(name="Policy Letter",
                     file_path="doc_templates/policy_letter.docx",
                     allowed_roles="dean,admin"),

            Template(name="Appointment Letter",
                     file_path="doc_templates/appointment_letter.docx",
                     allowed_roles="dean,admin"),

            Template(name="Promotion Letter",
                     file_path="doc_templates/promotion_letter.docx",
                     allowed_roles="dean,admin"),
        ]

        db.session.add_all(templates)
        db.session.commit()

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
    templates = Template.query.all()

    allowed_templates = []

    for template in templates:
        roles = template.allowed_roles.split(",")
        if current_user.role in roles:
            allowed_templates.append(template)

    documents = DocModel.query.all()

    return render_template(
        "dashboard.html",
        templates=allowed_templates,
        documents=documents
    )

@app.route("/create/<int:template_id>")
@login_required
def create_document(template_id):
    template = Template.query.get_or_404(template_id)
    roles = template.allowed_roles.split(",")

    if current_user.role not in roles:
        return "Access Denied"

    return render_template("create_document.html", template=template)


@app.route("/generate/<int:template_id>", methods=["POST"])
@login_required
def generate_document(template_id):

    template = Template.query.get_or_404(template_id)

    title = request.form["title"]
    department = request.form["department"]
    date = request.form["date"]
    message = request.form["message"]
    authority = request.form["authority"]

    doc = Document(template.file_path)

    for p in doc.paragraphs:
        p.text = p.text.replace("{{TITLE}}", title)
        p.text = p.text.replace("{{DEPARTMENT}}", department)
        p.text = p.text.replace("{{DATE}}", date)
        p.text = p.text.replace("{{MESSAGE}}", message)
        p.text = p.text.replace("{{AUTHORITY}}", authority)

    filename = f"{title.replace(' ', '_')}.docx"
    filepath = os.path.join(Config.GENERATED_FOLDER, filename)
    doc.save(filepath)

    new_doc = DocModel(
        title=title,
        filename=filename
    )

    db.session.add(new_doc)
    db.session.commit()

    return send_file(filepath, as_attachment=True)

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