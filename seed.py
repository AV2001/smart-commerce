from app import app
from models import db

# Drop and create tables.
with app.app_context():
    db.drop_all()
    db.create_all()
