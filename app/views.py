from flask import render_template, flash, redirect, request, session, url_for, get_flashed_messages
from app import app, db, models
from .forms import LoginForm, CreateForm

from functools import wraps

def logged_in(func):
    @wraps(func)
    def check_user(*args, **kwargs):
        if not 'username' in session:
            flash("You are not logged in")
            return redirect(url_for('login', prev_url = request.path))
        return func(*args, **kwargs)
    return check_user

def admin_auth(func):
    @wraps(func)
    def check_user(*args, **kwargs):
        if not 'username' in session:
            flash("You are not logged in")
            return redirect(url_for('login', prev_url = request.path))
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
    return render_template('index.html', title = 'Welcome')

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
    session.clear()
    flash('Logged out')
    return redirect('/index')

@app.route('/test')
@logged_in
def test():
    return "test"
