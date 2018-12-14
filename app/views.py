from flask import render_template, flash, Flask, request, redirect, url_for, make_response, send_from_directory
from app import app, models, db
from .forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, EditPassworldForm
from datetime import datetime
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash

#display all the posts of current user and user he followed
@app.route('/myposts')
@login_required
def myposts():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('myposts', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('myposts', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('myposts.html',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

#edit the profile for the current user
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your have changed the profile')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

#edit the password
@app.route('/edit_password', methods=['GET', 'POST'])
@login_required
#it means the function is protected, it would not let use who are not authenticated to use
def edit_password():
    form = EditPassworldForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_password'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_password.html', title='Edit password',
                           form=form)

#it will show posts from all users
@app.route('/community')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id.desc())
    return render_template("Community.html", title='community',
                           users=users)

#add a new post
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(('You add a new post!'))
        return redirect(url_for('myposts'))
    return render_template('index.html',form=form)

#the personal profile
@app.route('/user/<username>')
@login_required
def user(username):
    #404, which avoids the 404 result
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('other_user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

#the login interface
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

#the register interface
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#when user log out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#decorator from Flask register the decorated function to be executed right before the view function
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#follow a user
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

#unfollow a user
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

#These for tutorial and cw1
'''
@app.route('/fruit')
def displayFruit():
    fruits = ["Apple", "Banana", "Orange", "Kiwi"]
    return render_template("fruit.html", fruits=fruits)

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    form = CalculatorForm()
    if form.validate_on_submit():
        flash('Succesfully received form data. %s + %s  = %s'%(form.number1.data, form.number2.data, form.number1.data+form.number2.data))
    return render_template('calculator.html',
                           title='Calculator',
                           form=form)


#this is used to create a new task
@app.route('/createTask.html')
def createTask():

    return render_template('createTask.html')

#this is for editing the existing task
@app.route('/edit/<id>')
def edit(id):
    task0 = models.Property.query.filter_by(id=int(id)).first()
    db.session.delete(task0)
    db.session.commit()
    task = task0
    return render_template('edit.html',task=task)

#this is for deleting the task on completed tasks part
@app.route('/delete0/<id>')
def delete0(id):
    task = models.Property.query.filter_by(id=int(id)).first()
    db.session.delete(task)
    db.session.commit()
    flash("You delete the current task susscessfully")

    return redirect(url_for('allCompletedtask'))

#this is to mark the task completed
@app.route('/complete/<id>')
def complete(id):

    task = models.Property.query.filter_by(id=int(id)).first()
    task.complete = True
    db.session.commit()
    flash("You complete the current task susscessfully")

    return redirect(url_for('allTasks'))

#this is for deleting the task
@app.route('/delete/<id>')
def delete(id):
    task = models.Property.query.filter_by(id=int(id)).first()
    db.session.delete(task)
    db.session.commit()
    flash("You delete the current task susscessfully")

    return redirect(url_for('allTasks'))

#this would show all incompleted tasks
@app.route('/alltasks.html')
def allTasks():
    incomplete = models.Property.query.filter_by(complete=False).all()

    return render_template('alltasks.html', incomplete=incomplete)

#this is to submit the form in the form of records and store them in databse
@app.route('/add', methods=['POST'])
def add():
    time = datetime.now()
    task = models.Property(title=request.form['title'], text=request.form['text'], complete=False, time=time)
    db.session.add(task)
    db.session.commit()
    flash("You create a task susscessfully")

    return redirect(url_for('createTask'))

@app.route('/')
def index():
    return redirect(url_for('createTask'))


@app.route('/')
@app.route('/index')
def index():
    posts = models.Post.query.all()
    return render_template("index.html", title='Home Page', posts=posts)
    '''
