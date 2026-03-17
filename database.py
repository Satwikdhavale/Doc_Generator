from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ---------------- USER MODEL ---------------- #
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))   
    email = db.Column(db.String(120), unique=True)
    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- TEMPLATE MODEL ---------------- #
class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    file_path = db.Column(db.String(200))

    allowed_roles = db.Column(db.String(200))   
    approval_flow = db.Column(db.String(200))


# ---------------- GENERATED DOCUMENT MODEL ---------------- #
from datetime import datetime

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    template_name = db.Column(db.String(200))
    filename = db.Column(db.String(200))

    department = db.Column(db.String(200))
    content = db.Column(db.Text)
    authority = db.Column(db.String(200))
    date = db.Column(db.String(100))

    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(50), default="pending")

    approved_by_faculty = db.Column(db.Boolean, default=False)
    approved_by_hod = db.Column(db.Boolean, default=False)
    approved_by_dean = db.Column(db.Boolean, default=False)

# ---------------- AUDIT LOG MODEL ---------------- #
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    role = db.Column(db.String(50))
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------- MAIL MODEL ---------------- #

email = db.Column(db.String(120), unique=True)