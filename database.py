from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ---------------- USER MODEL ---------------- #
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)

    otp = db.Column(db.String(6))
    otp_created_at = db.Column(db.DateTime)
    otp_expiry = db.Column(db.DateTime)

    active = db.Column(db.Boolean, default=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_active(self):
        return self.active


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
email = db.Column(db.String(120), unique=True, nullable=False)
otp = db.Column(db.String(6))
otp_expiry = db.Column(db.DateTime)