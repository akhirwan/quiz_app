from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  nickname = db.Column(db.String(80), nullable=False)
  password_hash = db.Column(db.String(128))
  score = db.Column(db.Integer, default=0)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

class Questions(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  topic = db.Column(db.String(100))
  question_text = db.Column(db.String(255))
  option_a = db.Column(db.String(100))
  option_b = db.Column(db.String(100))
  option_c = db.Column(db.String(100))
  option_d = db.Column(db.String(100))
  correct_option = db.Column(db.String(1))