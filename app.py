from pydoc import doc
from flask import Flask, render_template, request, redirect, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from docx import Document as DocxDocument
from flask_mail import Mail, Message
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

def replace_text(doc, key, value):
    for para in doc.paragraphs:
        for run in para.runs:
            if key in run.text:
                run.text = run.text.replace(key, str(value))

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, str(value))

# ================= INITIAL SETUP ================= #

with app.app_context():
    db.create_all()

    # Default Users
    if not User.query.first():
        users = [
            User(username="admin", password=generate_password_hash("admin123"), role="admin", email="satwikdhavale1208@gmail.com"),
            User(username="faculty", password=generate_password_hash("123"), role="faculty", email="pritibagal25@gmail.com"),
            User(username="hod", password=generate_password_hash("123"), role="hod", email="hod@example.com"),
            User(username="dean", password=generate_password_hash("123"), role="dean", email="dean@example.com"),
            User(username="student", password=generate_password_hash("123"), role="student", email="dhavalesatwik12@gmail.com"),
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

    if user and user.active and check_password_hash(user.password, password):
        login_user(user)
        return redirect("/dashboard")

    return "Invalid Credentials"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        email = request.form["email"]

        user = User(
            username=username,
            password=password,
            role=role,
            email=email
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")


# ================= DASHBOARD ================= #

@app.route("/dashboard")
@login_required
def dashboard():

    query = DocModel.query

    title = request.args.get("title")
    department = request.args.get("department")
    date = request.args.get("date")
    role = request.args.get("role")
    user = request.args.get("user")

    if title:
        query = query.filter(DocModel.title.contains(title))

    if department:
        query = query.filter(DocModel.department.contains(department))

    if date:
        query = query.filter(DocModel.created_at.contains(date))

    if role:
        query = query.join(User, DocModel.created_by == User.username)\
                 .filter(User.role == role)

    if user:
        query = query.filter(DocModel.created_by.contains(user))

    documents = query.all()

    templates = Template.query.all()

    return render_template(
        "dashboard.html",
        documents=documents,
        templates=templates
    )

@app.route("/admin_dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        return "Access Denied", 403

    total_documents = DocModel.query.count()

    approved_documents = DocModel.query.filter_by(status="approved").count()

    pending_documents = DocModel.query.filter(
        DocModel.status != "approved",
        DocModel.status != "rejected"
    ).count()

    rejected_documents = DocModel.query.filter_by(status="rejected").count()

    total_users = User.query.count()

    students = User.query.filter_by(role="student").count()
    faculty = User.query.filter_by(role="faculty").count()
    hod = User.query.filter_by(role="hod").count()
    dean = User.query.filter_by(role="dean").count()

    return render_template(
        "admin_dashboard.html",
        total_documents=total_documents,
        approved_documents=approved_documents,
        pending_documents=pending_documents,
        rejected_documents=rejected_documents,
        total_users=total_users,
        students=students,
        faculty=faculty,
        hod=hod,
        dean=dean
    )


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

    title = request.form["title"]
    department = request.form["department"]
    template_name = request.form["template_name"]

    role = current_user.role

    # Decide first approval level
    if role == "student":
        status = "pending_faculty"

    elif role == "faculty":
        status = "pending_hod"

    elif role == "hod":
        status = "pending_dean"

    else:
        status = "approved"

    new_doc = DocModel(
        title=title,
        template_name=template_name,
        department=department,
        created_by=current_user.username,
        status=status
    )

    db.session.add(new_doc)
    db.session.commit()

    if current_user.role == "student":

        faculty_users = User.query.filter_by(role="faculty").all()

        for user in faculty_users:
            send_email(
                user.email,
                "New Request Pending Approval",
                f"""
                A new request has been submitted.

                Title: {title}
                Department: {department}

                Please login to approve/reject.
         """
            )
        
        hod_users = User.query.filter_by(role="hod").all()

    if current_user.role == "faculty":

        hod_users = User.query.filter_by(role="hod").all()

        for user in hod_users:
            send_email(
                user.email,
                "New Request Pending Approval",
                f"""
                A new request has been submitted.

                Title: {title}
                Department: {department}

                Please login to approve/reject.
         """
            )

        dean_users = User.query.filter_by(role="dean").all()

    if current_user.role == "hod":

        dean_users = User.query.filter_by(role="dean").all()

        for user in dean_users:
            send_email(
                user.email,
                "New Request Pending Approval",
                f"""
                A new request has been submitted.

                Title: {title}
                Department: {department}

                Please login to approve/reject.
         """
            )

    return redirect("/dashboard")


# ================= APPROVAL SYSTEM ================= #

@app.route("/approve/<int:doc_id>", methods=["POST"])
@login_required
def approve_document(doc_id):

    doc = DocModel.query.get_or_404(doc_id)

    role = current_user.role

    if role == "faculty" and doc.status == "pending_faculty":
        doc.status = "approved"

    elif role == "hod" and doc.status == "pending_hod":
        doc.status = "approved"

    elif role == "dean" and doc.status == "pending_dean":
        doc.status = "approved"

    # File generation logic
    if doc.status == "approved":

        template = Template.query.filter_by(name=doc.template_name).first()

        if not template:
            return "Template not found"

        filename = doc.title.replace(" ", "_") + ".docx"
        filepath = os.path.join(Config.GENERATED_FOLDER, filename)

        # Create blank doc if template fails
        try:
            document = DocxDocument(template.file_path)

            replace_text(document, "{{TITLE}}", doc.title)
            replace_text(document, "{{DEPARTMENT}}", doc.department)
            replace_text(document, "{{DATE}}", str(doc.created_at.date()) if doc.created_at else "")
            replace_text(document, "{{MESSAGE}}", doc.title)
            replace_text(document, "{{AUTHORITY}}", doc.created_by)
        except:
            document = DocxDocument()

        document.add_paragraph(f"Document: {doc.title}")
        document.add_paragraph(f"Generated for: {doc.created_by}")

        document.save(filepath)

        doc.filename = filename

        print("FILE CREATED:", filepath)

    creator = User.query.filter_by(username=doc.created_by).first()

    send_email(
        creator.email,
        "Document Approved ",
        f"""
        Your document has been approved.

        Title: {doc.title}
        """
    )

    db.session.commit()

    return redirect("/dashboard")

@app.route("/reject/<int:doc_id>", methods=["POST"])
@login_required
def reject_document(doc_id):

    doc = DocModel.query.get_or_404(doc_id)
    doc.status = "rejected"

    creator = User.query.filter_by(username=doc.created_by).first()
    send_email(
        creator.email,
        "Document Rejected",
        f"""
        Your document has been rejected.

        Title: {doc.title}
        """
    )
    db.session.commit()
    return redirect("/dashboard")


# ================= DOWNLOAD ================= #

@app.route("/generated_docs/<filename>")
@login_required
def download_file(filename):

    filepath = os.path.join(Config.GENERATED_FOLDER, filename)

    print("DOWNLOAD REQUEST:", filepath)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)

    return "File not found", 404


mail = Mail(app)
def send_email(to, subject, body):
    try:
        msg = Message(
            subject,
            sender=app.config["MAIL_USERNAME"],
            recipients=[to]
        )
        msg.body = body
        mail.send(msg)
    except Exception as e:
        print("EMAIL ERROR:", e)


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

@app.route("/reset_password/<int:user_id>")
@login_required
def reset_password(user_id):

    if current_user.role != "admin":
        return "Access Denied"

    user = User.query.get_or_404(user_id)

    user.password = generate_password_hash("123456")

    db.session.commit()

    return redirect("/manage_users")

@app.route("/toggle_user/<int:user_id>")
@login_required
def toggle_user(user_id):

    if current_user.role != "admin":
        return "Access Denied"

    user = User.query.get_or_404(user_id)

    user.active = not user.active

    db.session.commit()

    return redirect("/manage_users")

@app.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):

    if current_user.role != "admin":
        return "Access Denied"

    user = User.query.get_or_404(user_id)

    db.session.delete(user)

    db.session.commit()

    return redirect("/manage_users")

@app.route("/create_user", methods=["GET","POST"])
@login_required
def create_user():

    if current_user.role != "admin":
        return "Access Denied"

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        new_user = User(
            username=username,
            password=password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/manage_users")

    return render_template("create_user.html")

# ================= RUN ================= #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)