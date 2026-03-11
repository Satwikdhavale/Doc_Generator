from flask import Flask, render_template, request, redirect, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from docx import Document as DocxDocument
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


# ================= INITIAL SETUP ================= #

with app.app_context():
    db.create_all()

    # Default Users
    if not User.query.first():
        users = [
            User(username="admin", password=generate_password_hash("admin123"), role="admin"),
            User(username="faculty", password=generate_password_hash("123"), role="faculty"),
            User(username="hod", password=generate_password_hash("123"), role="hod"),
            User(username="dean", password=generate_password_hash("123"), role="dean"),
            User(username="student", password=generate_password_hash("123"), role="student"),
        ]
        db.session.add_all(users)
        db.session.commit()

    # Default Templates

with app.app_context():
    db.create_all()

    if not Template.query.first():
        templates = [

        # ---------------- STUDENT ----------------
        Template(
            name="Bonafide Certificate",
            file_path="doc_templates/bonafide_template.docx",
            allowed_roles="student,admin",
            approval_flow="hod,dean"
        ),

        Template(
            name="NOC Request",
            file_path="doc_templates/noc_template.docx",
            allowed_roles="student,admin",
            approval_flow="hod,dean"
        ),

        Template(
            name="Internship Permission Request",
            file_path="doc_templates/internship_request.docx",
            allowed_roles="student,admin",
            approval_flow="hod"
        ),

        Template(
            name="Leave Application",
            file_path="doc_templates/leave_application.docx",
            allowed_roles="student,admin",
            approval_flow="faculty"
        ),

        # ---------------- FACULTY ----------------
        Template(
            name="Recommendation Letter",
            file_path="doc_templates/recommendation.docx",
            allowed_roles="faculty,hod,admin",
            approval_flow="hod"
        ),

        Template(
            name="Internship Approval",
            file_path="doc_templates/internship_approval.docx",
            allowed_roles="faculty,hod,admin",
            approval_flow="hod"
        ),

        Template(
            name="Meeting Minutes",
            file_path="doc_templates/meeting_minutes.docx",
            allowed_roles="faculty,hod,admin",
            approval_flow="hod"
        ),

        Template(
            name="Event Certificate",
            file_path="doc_templates/event_certificate.docx",
            allowed_roles="faculty,hod,admin",
            approval_flow="hod"
        ),

        Template(
            name="Notice Draft",
            file_path="doc_templates/notice_draft.docx",
            allowed_roles="faculty,hod,admin",
            approval_flow="hod"
        ),

        # ---------------- HOD ----------------
        Template(
            name="Official Notice",
            file_path="doc_templates/official_notice.docx",
            allowed_roles="hod,admin",
            approval_flow="dean"
        ),

        Template(
            name="Circular",
            file_path="doc_templates/circular.docx",
            allowed_roles="hod,dean,admin",
            approval_flow="dean"
        ),

        Template(
            name="Department Letter",
            file_path="doc_templates/department_letter.docx",
            allowed_roles="hod,admin",
            approval_flow="dean"
        ),

        Template(
            name="Workload Allocation",
            file_path="doc_templates/workload_allocation.docx",
            allowed_roles="hod,admin",
            approval_flow="dean"
        ),

        # ---------------- DEAN ----------------
        Template(
            name="Policy Letter",
            file_path="doc_templates/policy_letter.docx",
            allowed_roles="dean,admin",
            approval_flow="dean"
        ),

        Template(
            name="Appointment Letter",
            file_path="doc_templates/appointment_letter.docx",
            allowed_roles="dean,admin",
            approval_flow="dean"
        ),

        Template(
            name="Promotion Letter",
            file_path="doc_templates/promotion_letter.docx",
            allowed_roles="dean,admin",
            approval_flow="dean"
        ),
    ]
        
        db.session.add_all(templates)
        db.session.commit()

# ================= AUTH ROUTES ================= #

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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# ================= DASHBOARD ================= #

@app.route("/dashboard")
@login_required
def dashboard():

    role = current_user.role

    if role == "student":
        documents = DocModel.query.filter_by(created_by=current_user.username).all()

    elif role == "faculty":
        documents = DocModel.query.filter_by(status="pending_faculty").all()

    elif role == "hod":
        documents = DocModel.query.filter_by(status="pending_hod").all()

    elif role == "dean":
        documents = DocModel.query.filter_by(status="pending_dean").all()

    elif role == "admin":
        documents = DocModel.query.all()

    templates = Template.query.all()

    return render_template("dashboard.html", documents=documents, templates=templates)


# ================= TEMPLATE ACCESS ================= #

@app.route("/create/<int:template_id>")
@login_required
def create_document(template_id):

    template = Template.query.get_or_404(template_id)
    roles = template.allowed_roles.split(",")

    if current_user.role not in roles:
        return "Access Denied", 403

    return render_template("create_document.html", template=template)


# ================= SUBMIT REQUEST ================= #

@app.route("/submit_request", methods=["POST"])
@login_required
def submit_request():

    new_doc = DocModel(
        title=request.form.get("title"),
        department=request.form.get("department"),
        content=request.form.get("message"),
        authority=request.form.get("authority"),
        date=request.form.get("date"),
        template_name=request.form.get("template_name"),
        created_by=current_user.username,
        status="pending_faculty"
    )

    db.session.add(new_doc)
    db.session.commit()

    return redirect("/dashboard")


# ================= APPROVAL SYSTEM ================= #

@app.route("/approve/<int:doc_id>", methods=["POST"])
@login_required
def approve_document(doc_id):

    doc = DocModel.query.get_or_404(doc_id)

    if current_user.role == "faculty":
        doc.status = "pending_hod"

    elif current_user.role == "hod":
        doc.status = "pending_dean"

    elif current_user.role == "dean":
        doc.status = "approved"

        template = Template.query.filter_by(name=doc.template_name).first()

        docx = DocxDocument(template.file_path)

        for p in docx.paragraphs:
            p.text = p.text.replace("{{TITLE}}", str(doc.title or ""))
            p.text = p.text.replace("{{DEPARTMENT}}", str(doc.department or ""))
            p.text = p.text.replace("{{MESSAGE}}", str(doc.content or ""))
            p.text = p.text.replace("{{AUTHORITY}}", str(doc.authority or ""))
            p.text = p.text.replace("{{DATE}}", str(doc.date or ""))

        filename = f"{doc.title.replace(' ', '_')}.docx"
        filepath = os.path.join(Config.GENERATED_FOLDER, filename)

        docx.save(filepath)

        doc.filename = filename

    db.session.commit()

    return redirect("/dashboard")


@app.route("/reject/<int:doc_id>", methods=["POST"])
@login_required
def reject_document(doc_id):

    doc = DocModel.query.get_or_404(doc_id)
    doc.status = "rejected"

    db.session.commit()
    return redirect("/dashboard")


# ================= DOWNLOAD ================= #

@app.route("/generated_docs/<filename>")
@login_required
def download_file(filename):

    filepath = os.path.join(Config.GENERATED_FOLDER, filename)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)

    return "File not found", 404


# ================= ADMIN ================= #

@app.route("/manage_users")
@login_required
def manage_users():

    if current_user.role != "admin":
        return "Access Denied", 403

    users = User.query.all()
    return render_template("manage_users.html", users=users)


@app.route("/update_role/<int:user_id>", methods=["POST"])
@login_required
def update_role(user_id):

    if current_user.role != "admin":
        return "Access Denied", 403

    user = User.query.get_or_404(user_id)
    user.role = request.form["role"]

    db.session.commit()
    return redirect("/manage_users")

@app.route("/preview/<int:doc_id>")
@login_required
def preview(doc_id):
    doc = DocModel.query.get_or_404(doc_id)
    return render_template("preview.html", doc=doc)

# ================= RUN ================= #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)