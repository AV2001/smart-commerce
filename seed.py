from app import app
from models import db, User, Wishlist

# Drop and create tables.
with app.app_context():
    db.drop_all()
    db.create_all()

    # Create user
    user = User.create_account(first_name='John', last_name='Doe',
                               email='johndoe@gmail.com', profile_picture=None, password='johnjohn')

    db.session.add(user)
    db.session.commit()

    # Create wishlist
    wishlist = Wishlist(
        name='Harry Potter', description='This is a wishlist containing all Harry Potter stuff.', user_id=user.id)

    db.session.add(wishlist)
    db.session.commit()
