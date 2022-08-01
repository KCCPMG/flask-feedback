from app import app
from models import db, User

db.drop_all()
db.create_all()

# docs



#db.session.add_all([])
db.session.commit()