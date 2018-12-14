from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, login, db
from hashlib import md5

#association table that has no data, many to many relationship, the follower_id is following the followed_id
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

#hash the password for the security
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

#check the password users input the is the same with that stored in
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#relationship,user instance to the user instance
    followed = db.relationship(
        'User', secondary=followers,
        #link the left side with the association table
        primaryjoin=(followers.c.follower_id == id),
        #link the right side
        secondaryjoin=(followers.c.followed_id == id),
        #when the relationship be accessed by the right side
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    #to follow a user
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    #to stop following a user
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    #is_following to check if the followed relationship exists, the result is 0 or 1
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

#flask user session, get the id of the user from the session
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
