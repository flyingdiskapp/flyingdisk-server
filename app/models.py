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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    author = db.Column(db.String(30), nullable=False)
    versions = db.relationship('PackageVersion', backref='package', lazy=True)

class PackageVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(10), nullable=False)
    short_description = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    changelog = db.Column(db.Text, nullable=True)
    files = db.Column(db.JSON, nullable=False, default=[])
    tags = db.Column(db.JSON, nullable=True, default=[])
