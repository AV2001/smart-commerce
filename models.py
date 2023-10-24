from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    '''Connect to database.'''

    db.app = app
    db.init_app(app)


class User(db.Model):
    '''User Model'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    profile_picture = db.Column(
        db.Text, nullable=False, default='https://www.pinclipart.com/picdir/big/148-1486972_mystery-man-avatar-circle-clipart.png')
    password = db.Column(db.Text, nullable=False)

    # Relationship to wishlist
    wishlists = db.relationship(
        'Wishlist', backref='user', cascade='all, delete-orphan')

    # Relationship to product
    products = db.relationship(
        'Product', backref='user', cascade='all, delete-orphan')

    # Properties
    @property
    def full_name(self):
        '''Return full name of user.'''
        return f'{self.first_name} {self.last_name}'

    # Methods
    @classmethod
    def create_account(cls, first_name, last_name, email, profile_picture, password):
        '''Create a new user account.'''

        hashed_password = bcrypt.generate_password_hash(
            password).decode('utf-8')
        user = cls(first_name=first_name, last_name=last_name,
                   email=email, profile_picture=profile_picture, password=hashed_password)
        return user

    @classmethod
    def authenticate(cls, email, password):
        '''
        Authenticate a user.
        Return user if auth is successful, otherwise return False.
        '''
        user = cls.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return False


class Wishlist(db.Model):
    '''Wishlist Model'''

    __tablename__ = 'wishlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationship to product
    products = db.relationship(
        'Product', secondary='wishlist_products', backref='wishlists', cascade='all, delete')

    def serialize(self):
        '''Serialize wishlist data.'''
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id
        }


class WishlistProduct(db.Model):
    '''WishlistProduct Model'''

    __tablename__ = 'wishlist_products'

    wishlist_id = db.Column(db.Integer, db.ForeignKey(
        'wishlists.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.id'), primary_key=True)


class Product(db.Model):
    '''Product Model'''

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    currency = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    product_url = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
