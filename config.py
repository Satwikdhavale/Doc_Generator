import os
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GENERATED_FOLDER = os.path.join(BASE_DIR, "generated_docs")
    TEMPLATE_PATH = os.path.join(BASE_DIR, "doc_templates", "notice_template.docx")