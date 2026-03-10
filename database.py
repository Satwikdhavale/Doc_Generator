from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ---------------- USER MODEL ---------------- #
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))  # student, faculty, hod, dean, admin


# ---------------- TEMPLATE MODEL ---------------- #
class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    file_path = db.Column(db.String(200))
    allowed_roles = db.Column(db.String(200))
    # Example: "student,admin" or "faculty,hod,admin"


# ---------------- GENERATED DOCUMENT MODEL ---------------- #
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    department = db.Column(db.String(200))
    date = db.Column(db.String(100))
    authority = db.Column(db.String(200))
    filename = db.Column(db.String(200))

    created_by = db.Column(db.String(100))
    role = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- AUDIT LOG MODEL ---------------- #
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    role = db.Column(db.String(50))
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)