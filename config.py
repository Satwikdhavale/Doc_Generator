import os
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GENERATED_FOLDER = os.path.join(BASE_DIR, "generated_docs")
    TEMPLATE_PATH = os.path.join(BASE_DIR, "doc_templates", "notice_template.docx")

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = "satwikdhavale1208@gmail.com"
    MAIL_PASSWORD = "gabeijrjaexloedg"
    MAIL_DeFAULT_SENDER = "satwikdhavale1208@gmail.com" 