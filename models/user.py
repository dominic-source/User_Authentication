from app import db

class User(db.Model):
    """
    This is the Category class. It represents a category in the database.

    Attributes:
        id (int): The primary key of the category.
        name (str): The name of the category. It is unique and cannot be null.
    """
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), unique=True, nullable=False)
