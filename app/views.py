from flask import render_template, flash, redirect, request, session, url_for, get_flashed_messages
from app import app, db, models
from .forms import LoginForm, CreateForm

from functools import wraps

def logged_in(func):
    @wraps(func)
    def check_user(*args, **kwargs):
        if not 'username' in session:
            flash("You are not logged in")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return check_user

def admin_auth(func):
    @wraps(func)
    def check_user(*args, **kwargs):
        if not 'username' in session:
            flash("You are not logged in")
            return redirect(url_for('login'))
        user = models.User.query.filter_by(username = session['username']).first()
        if not user:
            flash("Authentication did not check out")
            return redirect('index')
        if not user.admin:
            flash("You must be an administrator to view this page")
            return redirect('index')
        return func(*args, **kwargs)
    return check_user

def user_auth():
    if not 'username' in session:
        return False
    user = models.User.query.filter_by(username = session['username']).first()
    if not user:
        return False
    return True

@app.route('/')
@app.route('/index')
def index():
    user = None
    if user_auth():
        user = models.User.query.filter_by(username = session['username']).first()
    return render_template('index.html', title = 'Welcome', user = user)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        session['username'] = login_form.username.data
        if models.User.query.filter_by(username = login_form.username.data).first().admin:
            session['admin'] = 'true'
        else:
            session['admin'] = 'false'

        flash('Logged in')
        return redirect('/index')
    
    return render_template('login.html', title = 'Login', login_form = login_form)

@app.route('/create', methods = ['GET', 'POST'])
def create():
    create_form = CreateForm()

    if create_form.validate_on_submit():
        session['username'] = create_form.username.data
        session['admin'] = 'false'

        user = models.User(username = create_form.username.data,
                    nickname = create_form.nickname.data,
                    email = create_form.email.data)
        user.set_password(create_form.password.data)
        db.session.add(user)
        db.session.commit()                    

        flash('Logged in')
        return redirect('/index')
    
    return render_template('create.html', title = 'Create an Account', create_form = create_form)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.pop('username', None)
    flash('Logged out')
    return redirect('/index')

@app.route('/classes')
@logged_in
def classes():
    user = models.User.query.filter_by(username = session['username']).first()

    school_classes = models.SchoolClass.query.all()
    
    return render_template("classes.html", user = user, school_classes = school_classes)

@app.route('/ad')
@logged_in
def ad():
    ad_form = ADForm()
    ad_form.classname.choices = 
