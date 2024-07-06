from app import db

class User(db.Model):
    """
    This is the user class. It represents a user in the database.

    Attributes:
        userId (str): The primary key of the user.
        email (str): The email of user. It is unique and cannot be null.
    """
    __tablename__ = 'user'
    userId = db.Column(db.String, primary_key=True, unique=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
