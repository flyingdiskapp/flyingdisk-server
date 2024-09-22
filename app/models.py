from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    mail = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    packages = db.Column(db.JSON, nullable=False, default="[]")
    admin = db.Column(db.Boolean, nullable=False)

class Package(db.Model):
    package = db.Column(db.Text, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    shortDescription = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    version = db.Column(db.String(20), nullable=False)
    files = db.Column(db.JSON, nullable=False, default=[])

    __table_args__ = (db.UniqueConstraint(
        'name', 'version', name='_name_version_uc'),)