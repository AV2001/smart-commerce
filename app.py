import os
from dotenv import load_dotenv
from flask import Flask, flash, g, jsonify, redirect, render_template, request, session
from models import connect_db, db, User, Wishlist, Product, WishlistProduct
from forms import SignUpForm, LoginForm, WishlistForm
from sqlalchemy.exc import IntegrityError
from ebay import get_products_from_prompt

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

# Connect app to database
connect_db(app)

# Keep track of current user
CURR_USER_KEY = 'current_user_id'


# USER ROUTES
@app.before_request
def add_user_to_g():
    '''If we're logged in, add curr user to Flask global.'''
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def perform_login(user):
    '''Log in user.'''
    session[CURR_USER_KEY] = user.id


def perform_logout():
    '''Utility function to log out user.'''
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/get-current-user')
def get_current_user():
    '''Get current user.'''
    if not g.user:
        return jsonify(error='User not logged in!'), 401

    wishlists = [wishlist.serialize() for wishlist in g.user.wishlists]
    return jsonify(userId=g.user.id, wishlists=wishlists)


@app.route('/logout', methods=['POST'])
def logout():
    '''Log user out.'''
    perform_logout()
    flash('Logged out successfully!', 'success')
    return redirect('/')


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    '''Delete user.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    perform_logout()
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted successfully!', 'success')
    return redirect('/')


# PAGE ROUTES
@app.route('/')
def home_page():
    '''Show homepage.'''
    return render_template('index.html')


@app.route('/about')
def about_page():
    '''Show about page.'''
    return render_template('about.html')


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    '''Show signup form and handle form submission.'''
    if g.user:
        return redirect('/search')

    form = SignUpForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        profile_picture = form.profile_picture.data if form.profile_picture.data else None
        password = form.password.data

        new_user = User.create_account(
            first_name=first_name, last_name=last_name, email=email, profile_picture=profile_picture, password=password)

        db.session.add(new_user)

        # Check whether email is already taken
        try:
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect('/login')
        except IntegrityError:
            form.email.errors.append(
                'Email already taken. Please pick another.')

    return render_template('users/signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def log_in():
    '''Show login form and handle form submission.'''
    if g.user:
        return redirect('/search')

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.authenticate(email=email, password=password)

        if user:
            perform_login(user)
            flash(f'Welcome, {user.first_name.title()}!', 'success')
            return redirect('/search')
        else:
            form.email.errors = ['Invalid email/password.']

    return render_template('users/login.html', form=form)


@app.route('/search')
def search():
    '''Process form data and show search results.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    return render_template('users/search.html')


@app.route('/get-products')
def get_products():
    '''Get products from eBay API.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    prompt = request.args.get('search', None)
    products = get_products_from_prompt(prompt)

    # Check if products were found
    products_count = products['findItemsByKeywordsResponse'][0]['searchResult'][0]['@count']
    if products_count == '0':
        return jsonify(message='No products found!'), 404
    return jsonify(products=products)


@app.route('/profile', methods=['GET', 'POST'])
def show_user_profile():
    '''Show user profile.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    user = User.query.get_or_404(g.user.id)
    form = SignUpForm(obj=user)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.profile_picture = form.profile_picture.data if form.profile_picture.data else 'https://www.pinclipart.com/picdir/big/148-1486972_mystery-man-avatar-circle-clipart.png'

        db.session.commit()
        return redirect('/profile')

    return render_template('users/user-profile.html', form=form, user=user)


# WISHLIST ROUTES
@app.route('/users/<int:user_id>/wishlists')
def get_wishlists(user_id):
    '''Show user's wishlists.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    user = User.query.get_or_404(user_id)
    wishlists = user.wishlists

    return render_template('users/wishlists.html', user=user, wishlists=wishlists)


@app.route('/users/<int:user_id>/wishlists/create', methods=['GET', 'POST'])
def create_wishlist(user_id):
    '''Show form to create new wishlist.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    form = WishlistForm()
    if form.validate_on_submit():
        name = form.name.data.lower()
        description = form.description.data
        wishlist = Wishlist(
            name=name, description=description, user_id=user_id)
        db.session.add(wishlist)

        # Check whether wishlist name already exists
        try:
            db.session.commit()
            flash(
                f'Wishlist "{wishlist.name}" created successfully!', 'success')
            return redirect(f'/users/{user_id}/wishlists')
        except IntegrityError:
            db.session.rollback()
            form.name.errors.append(
                'A wishlist with this name already exists. Please pick another name.')

    return render_template('users/create-wishlist.html', form=form)


@app.route('/users/<int:user_id>/wishlists/<string:name>/products')
def get_wishlist_products(user_id, name):
    '''Show products in wishlist.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    wishlist = Wishlist.query.filter_by(name=name).first_or_404()
    products = wishlist.products
    return render_template('users/wishlist-products.html', wishlist=wishlist, products=products)


@app.route('/users/<int:user_id>/wishlists/<string:name>/add-product', methods=['POST'])
def add_product_to_wishlist(user_id, name):
    '''Add product to wishlist.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    user = User.query.get_or_404(user_id)
    wishlist = Wishlist.query.filter_by(name=name).first_or_404()
    user.wishlists.append(wishlist)
    product = request.json.get('product', None)

    # Check if product already exists in the wishlist
    existing_product = Product.query.filter_by(title=product['title']).first()
    if existing_product and existing_product in wishlist.products:
        return jsonify(message=f'Product already exists in {wishlist.name.title()}.'), 400

    new_product = Product(
        title=product['title'], currency=product['currency'], price=product['price'], image_url=product['imageURL'], product_url=product['productURL'])
    user.products.append(new_product)
    db.session.add(new_product)
    db.session.commit()
    wishlist_product = WishlistProduct(
        wishlist_id=wishlist.id, product_id=new_product.id)
    db.session.add(wishlist_product)
    db.session.commit()
    return jsonify(message=f'Product added successfully to {wishlist.name.title()}.')


@app.route('/users/<int:user_id>/wishlists/<string:name>/products/<int:product_id>/delete', methods=['POST'])
def delete_product_from_wishlist(user_id, name, product_id):
    '''Delete product from wishlist.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(f'/users/{g.user.id}/wishlists/{name}/products')


@app.route('/users/<int:user_id>/wishlists/<string:name>/delete', methods=['POST'])
def delete_wishlist(user_id, name):
    '''Delete a wishlist.'''
    if not g.user:
        flash('Unauthorized access! Please log in.', 'danger')
        return redirect('/login')

    wishlist = Wishlist.query.filter_by(name=name).first_or_404()
    db.session.delete(wishlist)
    db.session.commit()
    flash(f'Wishlist "{name}" deleted successfully!', 'success')
    return redirect(f'/users/{user_id}/wishlists')
