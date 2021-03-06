from flask import render_template, flash, redirect, request, session, url_for, get_flashed_messages
from app import app, db, models
from .forms import LoginForm, CreateForm, ADForm
from sqlalchemy import desc

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
@app.route('/classes/<int:sort>')
@logged_in
def classes(sort = 1):
    user = models.User.query.filter_by(username = session['username']).first()

    school_classes = models.SchoolClass.query

    if sort == 1:
        school_classes = school_classes.order_by(models.SchoolClass.period)
    elif sort == 2:
        school_classes = school_classes.order_by(models.SchoolClass.name)
    elif sort == 3:
        school_classes = school_classes.order_by(models.SchoolClass.teacher)
    elif sort == 4:
        school_classes = school_classes.order_by(models.SchoolClass.num_adds.desc())
    elif sort == 5:
        school_classes = school_classes.order_by(models.SchoolClass.num_drops.desc())
    elif sort == 6:
        school_classes = school_classes.order_by(models.SchoolClass.change.desc())
    
    school_classes = school_classes.all()
    
    return render_template("classes.html", user = user, school_classes = school_classes, sort = sort)

@app.route('/form', methods=['GET', 'POST'])
@logged_in
def form():
    user = models.User.query.filter_by(username = session['username']).first()
    
    ad_form = ADForm()

    classes = models.SchoolClass.query.all()
    select_choices = []
    for c in classes:
        string = c.name + ', Period ' + str(c.period) + ', ' + c.teacher
        select_choices.append((str(c.id), string))   
    ad_form.classname.choices = select_choices

    if ad_form.validate_on_submit():
        school_class = models.SchoolClass.query.filter_by(id = int(ad_form.classname.data)).first()
        if ad_form.choice.data == 'add':
            c = models.Add(user = user, school_class = school_class)
            school_class.num_adds += 1
            flash('Class added')
        else:
            c = models.Drop(user = user, school_class = school_class)
            school_class.num_drops += 1
            flash('Class dropped')
        db.session.add(c)
        db.session.commit()
        return redirect('/form')

    return render_template('ad_form.html', user = user, ad_form = ad_form)
