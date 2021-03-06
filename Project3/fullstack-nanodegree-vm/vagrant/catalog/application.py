# DAL/database imports and setup
from DAL import Base, Category, Item, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# OAuth imports and helpers
from oauth2client.client import flow_from_clientsecrets, \
								FlowExchangeError, OAuth2Credentials
import httplib2
import json
import requests
import random
import string

# Flask imports and setup
from flask import Flask, render_template, session as login_session, \
    make_response, request, flash, abort, redirect, url_for, jsonify, g

# For returning XML through APIs
import xml.etree.ElementTree as ET

# Used for image processing from database to site, and vice versa
from base64 import b64encode

# For decorators
from functools import wraps

app = Flask(__name__)
app.debug = True

ALLOWED_EXTENSIONS = set(['jpeg', 'png', 'jpg', 'bmp'])

CLIENT_ID = \
    json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to database and create a session
engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Decorate to make sure user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# Generate nonce for POST DELETE... code @ http://flask.pocoo.org/snippets/3/
# and wrap necessary functions
def csrf_protect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "POST":
            token = login_session.pop('_csrf_token', None)
            if not token or token != request.form.get('_csrf_token'):
                abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Generate CSRF token
def generate_csrf_token():
    if '_csrf_token' not in login_session:
        login_session['_csrf_token'] = \
            ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(12))
    return login_session['_csrf_token']


# When delete templates are requested, a new token is created
app.jinja_env.globals['csrf_token'] = generate_csrf_token


# Main
@app.route('/')
@app.route('/catalog/')
def main():
    # Get categories
    categories = session.query(Category).order_by(Category.name).all()
    return render_template('main.html', categories=categories)


# Category
@app.route('/catalog/<category>')
def category(category):
    # Get categories
    categories = session.query(Category).order_by(Category.name).all()

    # Make sure that chosen category exists in database
    if category in [c.name for c in categories]:
        # Get category chosen
        category = session.query(Category).filter_by(name=category).one()
        # Get category items
        items = session.query(Item).filter_by(category_id=category.id).all()
        return render_template('main.html',
                               category_picked=category,
                               categories=categories,
                               items=items)

    # Else return 404
    abort(404)


# Add a category - fix this for session
@app.route('/catalog/addcategory', methods=['GET', 'POST'])
@csrf_protect
@login_required
def addCategory():
    if request.method == 'POST':
        # First check to see if category name already exists
        if session.query(Category).filter_by(
                                name=request.form['name']).first() != None:
            flash('Category %s already exists' % request.form['name'])
            return redirect(url_for('main'))
        # Add new category from form name value
        new_category = Category(name=request.form['name'],
                                creator_id=login_session['user_id'])
        session.add(new_category)
        flash('New category %s successfully created' % new_category.name)
        session.commit()
        return redirect('/')
    else:
        # HTTP GET
        return render_template('addcategory.html')


# Edit a category
@app.route('/catalog/<category>/edit', methods=['GET', 'POST'])
@csrf_protect
@login_required
def editCategory(category):
    if request.method == 'POST':
        # First check to see if category name already exists
        if session.query(Category).filter_by(
                                    name=request.form['name']).first() != None:
            flash('Category %s already exists' % request.form['name'])
            return redirect(url_for('main'))
        edit_category = session.query(Category).filter_by(name=category).one()
        edit_category.name = request.form['name']
        session.commit()
        flash('Category %s successfully edited' % category)
        return redirect('/')
    else:
        # HTTP GET
        return render_template('editcategory.html', category_name=category)


# Delete a category - fix this for session
@app.route('/catalog/<category>/delete', methods=['GET', 'POST'])
@csrf_protect
@login_required
def deleteCategory(category):
    if request.method == 'POST':
        # Get selected category
        delete_category = session.query(
                            Category).filter_by(name=category).one()

        # Delete the category.. items are deleted with cascade in DAL.py
        session.delete(delete_category)
        flash('Category %s and its items have '
              'been successfully deleted.' % category)
        session.commit()
        return redirect('/')
    else:
        # HTTP GET
        return render_template('deletecategory.html', category_name=category)


# Item for category
@app.route('/catalog/<category>/<item>')
def item(category, item):
    # Get categories
    categories = session.query(Category).order_by(Category.name).all()
    # Get category chosen
    category = session.query(Category).filter_by(name=category).one()
    # Get category items
    items = session.query(Item).filter_by(category_id=category.id).all()
    # Get category and item
    item = session.query(Item).filter_by(
                    name=item, category_id=category.id).one()
    # If image exists

    # Init image to None and update if it exists for the item
    image = None
    if item.image is not None:
        # Encode to string to be transmitted
        image = b64encode(item.image)

    return render_template('main.html',
                           item_picked=item,
                           category_picked=category,
                           categories=categories,
                           items=items,
                           image=image)


# Add an item to a category
@app.route('/catalog/<category>/additem', methods=['GET', 'POST'])
@csrf_protect
@login_required
def addItem(category):
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=category).first()
        # See if item already exists for the category
        if session.query(Item).filter_by(
                   name=request.form['name'],
                   category_id=category.id).first() != None:

            flash('Item %s for category %s '
                  'already exists' % (request.form['name'], category.name))
            return redirect(url_for('main'))
        # Create and add new item
        new_item = Item(name=request.form['name'],
                        description=request.form['description'],
                        category_id=category.id)

        # Add image to item if user uploaded one
        if request.files['image']:
            file = request.files['image']
            new_item.image = file.read()

        session.add(new_item)
        flash('New item %s successfully created' % new_item.name)
        session.commit()
        return redirect(url_for('category', category=category.name))
    # HTTP GET
    else:
        return render_template('additem.html', category_name=category)


# Edit an item in a category
@app.route('/catalog/<category>/<item>/edit', methods=['GET', 'POST'])
@csrf_protect
@login_required
def editItem(category, item):
    # Get related category
    category = session.query(Category).filter_by(name=category).first()

    if request.method == 'POST':
        # See if item already exists for the category
        current_item = session.query(Item).filter_by(
                                      name=item,
                                      category_id=category.id).first()
        found_item = session.query(Item).filter_by(
                                      name=request.form['name'],
                                      category_id=category.id).first()

        # Edit item if name matches what we're working on or
        # if name does not exist yet
        if found_item is None or current_item.id == found_item.id:
            edit_item = current_item
            edit_item.name = request.form['name']
            edit_item.description = request.form['description']
            session.commit()
            flash('Item %s in category %s successfully edited' %
                  (item, category.name))
            return redirect(url_for('main'))
        else:
            flash('Item %s for category %s already exists' %
                  (request.form['name'], category.name))
            return redirect('/')
    # HTTP GET
    else:
        item = session.query(Item).filter_by(
                    name=item, category_id=category.id).first()
        # Init image to None and set if image exists for item
        image = None
        if item.image is not None:
            # Encode to string to be transmitted
            image = b64encode(item.image)
        return render_template('edititem.html',
                               category_name=category.name,
                               item_picked=item,
                               image=image)


# Delete an item from a category
@app.route('/catalog/<category>/<item>/delete', methods=['GET', 'POST'])
@csrf_protect
@login_required
def deleteItem(category, item):
    if request.method == 'POST':
        # Get category for item
        category = session.query(Category).filter_by(name=category).first()
        # Get item and delete
        delete_item = session.query(Item).filter_by(
                                name=item, category_id=category.id).one()

        session.delete(delete_item)
        flash('Item %s been successfully deleted.' % item)
        session.commit()
        return redirect('/')
    else:
        # HTTP GET
        return render_template('deleteitem.html',
                               category_name=category,
                               item_name=item)


# Return catalog (categories) in JSON
@app.route('/catalog/api')
@app.route('/catalog/api/json')
def getCatalogJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


# Return catalog in XML
@app.route('/catalog/api/xml')
def getCatalogXML():
    # Get categories and create root element 'categories'
    categories = session.query(Category).all()
    xml_categories = ET.Element('categories')
    for c in categories:
        # Create elements for each category and add id, name, and items
        xml_category = ET.SubElement(xml_categories, 'category')
        xml_id = ET.SubElement(xml_category, 'id').text = str(c.id)
        xml_name = ET.SubElement(xml_category, 'name').text = c.name
        # Get items and create subelements
        items = session.query(Item).filter_by(category_id=c.id).all()
        for i in items:
            xml_item = ET.SubElement(xml_category, 'item')
            xml_item_name = ET.SubElement(xml_item, 'name').text = i.name
            # If description exists, insert it
            if i.description is not None:
                xml_item_description = ET.SubElement(
                            xml_item, 'description').text = i.description
    return ET.tostring(xml_categories)


# Return category in JSON
@app.route('/catalog/<category>/api')
@app.route('/catalog/<category>/api/json')
def getCategoryJSON(category):
    category = session.query(Category).filter_by(name=category).first()
    if category is not None:
        items = session.query(Item).filter_by(category_id=category.id).all()
        return jsonify(items=[i.serialize for i in items])
    else:
        return 'Category not found'


# Return category in XML
@app.route('/catalog/<category>/api/xml')
def getCategoryXML(category):
    category = session.query(Category).filter_by(name=category).first()
    if category is None:
        return 'Category not found'
    xml_category = ET.Element('category')
    xml_id = ET.SubElement(xml_category, 'id').text = str(category.id)
    xml_name = ET.SubElement(xml_category, 'name').text = str(category.name)
    # Get items and create subelements
    items = session.query(Item).filter_by(category_id=category.id).all()
    for i in items:
        xml_item = ET.SubElement(xml_category, 'item')
        xml_item_name = ET.SubElement(xml_item, 'name').text = i.name
        # If description exists, insert it
        if i.description is not None:
            xml_item_description = ET.SubElement(
                            xml_item, 'description').text = i.description
    return ET.tostring(xml_category)


# Return item in JSON
@app.route('/catalog/<category>/<item>/api')
@app.route('/catalog/<category>/<item>/api/json')
def getItemJSON(category, item):
    category = session.query(Category).filter_by(name=category).first()
    if category is not None:
        item = session.query(Item).filter_by(name=item,
                                      category_id=category.id).first()
        if item is not None:
            return jsonify(item.serialize)
        else:
            return 'Item not found'
    else:
        return 'Category not found'


# Return item in XML
@app.route('/catalog/<category>/<item>/api/xml')
def getItemXML(category, item):
    category = session.query(Category).filter_by(name=category).first()
    if category is not None:
        item = session.query(Item).filter_by(
                            name=item, category_id=category.id).first()

        if item is not None:
            xml_item = ET.Element('item')
            xml_id = ET.SubElement(xml_item, 'id').text = str(item.id)
            xml_name = ET.SubElement(xml_item, 'name').text = item.name
            if item.description:
                xml_item_description = ET.SubElement(
                    xml_item, 'description').text = item.description
            return ET.tostring(xml_item)
        else:
            return 'Item not found'
    else:
        return 'Category not found'


# Login
@app.route('/login')
def login():
    state = ''.join(random.choice(
            string.ascii_uppercase + string.digits)
            for x in xrange(32))

    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Logout
@app.route('/logout')
def logout():
    if 'username' in login_session:
        gdisconnect()
        del login_session['gplus_id']
        del login_session['credentials']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        flash('Successfully logged out')
        return redirect('/')
    else:
        flash('You were not logged in')
        return redirect('/')


# Google OAuth
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
                    json.dumps('Current user is already connected.'), 200)

        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    'border-radius: 150px;-webkit-border-radius: 150px;'
    '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# Disconnect Google OAuth
@app.route("/gdisconnect")
def gdisconnect():
    # Only disconnect a connected user
    credentials = OAuth2Credentials(login_session.get('credentials'))
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid
        response = make_response(
                    json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions
# Create User
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Get User ID
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'super secret key'
    app.run(host='0.0.0.0')
