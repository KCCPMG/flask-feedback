from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
  db.app = app
  db.init_app(app)



class User(db.Model):
  """A User who can log into their account"""

  __tablename__ = "users"

  username = db.Column(db.String(20), primary_key=True, unique=True)
  password = db.Column(db.String, nullable=False)
  email = db.Column(db.String(50), nullable=False)
  first_name = db.Column(db.String(30), nullable=False)
  last_name = db.Column(db.String(30), nullable=False)

  @classmethod
  def register(cls, username, password, email, first_name, last_name):
    hashed_password = bcrypt.generate_password_hash(password).decode("utf8")

    return cls(username=username, password=hashed_password, email=email, first_name=first_name, last_name=last_name)

  @classmethod
  def login(cls, username, password):
    user = User.query.get(username)

    if bcrypt.check_password_hash(user.password, password):
      return True
    else:
      return False



class Feedback(db.Model):

  __tablename__ = "feedback"

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  title = db.Column(db.String(100), nullable=False)
  content = db.Column(db.String, nullable=False)
  username = db.Column(db.String, foreign_key="User.username")