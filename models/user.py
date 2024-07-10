from database import db

# Association table for the many-to-many relationship
user_organization = db.Table('user_organization',
    db.Column('user_id', db.String, db.ForeignKey('user.userId'), primary_key=True),
    db.Column('organization_id', db.String, db.ForeignKey('organization.orgId'), primary_key=True)
)

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
    organizations = db.relationship('Organization', secondary=user_organization, backref=db.backref('users', lazy='dynamic'))


class Organization(db.Model):
    """This class is the organization class where users can belong"""
    __tablename__ = 'organization'
    orgId = db.Column(db.String, primary_key=True, unique=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
