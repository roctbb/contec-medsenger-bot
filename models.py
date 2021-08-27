from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_import = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, default=True)