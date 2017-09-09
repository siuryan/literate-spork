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

@app.route('/')
@app.route('/index')
def index():
    user = models.User.query.filter_by(username = session['username']).first()
    return render_template('index.html', title = 'Welcome', user = user)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    user = models.User.query.filter_by(username = session['username']).first()
    
    login_form = LoginForm()

    if login_form.validate_on_submit():
        session['username'] = login_form.username.data
        if models.User.query.filter_by(username = login_form.username.data).first().admin:
            session['admin'] = 'true'
        else:
            session['admin'] = 'false'

        flash('Logged in')
        return redirect('/index')
    
    return render_template('login.html', title = 'Login', login_form = login_form, user = user)

@app.route('/create', methods = ['GET', 'POST'])
def create():
    user = models.User.query.filter_by(username = session['username']).first()
    
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
    
    return render_template('create.html', title = 'Create an Account', create_form = create_form, user = user)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.clear()
    flash('Logged out')
    return redirect('/index')

@app.route('/test')
@logged_in
def test():
    return "test"
