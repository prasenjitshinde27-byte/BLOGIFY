from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous.exc import BadData
from flask import current_app
from flaskblog import db, login_manager 
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin): 
    id  = db.Column(db.Integer , primary_key=True)
    username = db.Column(db.String(20) , unique=True , nullable=False)
    email  = db.Column(db.String(100) , unique=True , nullable=False)
    image_file = db.Column(db.String(20), nullable=False , unique=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)   
    posts = db.relationship('Post', backref='author' , lazy=True)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps( { 'user_id' : self.id})
    

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except BadData:
            # Invalid, tampered, or expired token — treat as no user.
            return None
        except Exception:
            # Unexpected failure (e.g. misconfigured SECRET_KEY): log and
            # re-raise so it is not silently swallowed as an invalid token.
            current_app.logger.exception('Failed to verify password reset token')
            raise
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.username}' , '{self.email}' , '{self.image_file}')"
    
class Post(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100) , nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False , default=lambda: datetime.now(timezone.utc))
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

    @property
    def like_count(self):
        return len(self.likes)

    def is_liked_by(self, user):
        return any(like.user_id == user.id for like in self.likes)

    def __repr__(self):
        return f"Post('{self.title}' , '{self.date_posted}')"


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

    def __repr__(self):
        return f"Like(user={self.user_id}, post={self.post_id})" 
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author = db.relationship('User', backref='comments', lazy=True)

    def __repr__(self):
      return f"Comment('{self.body}, {self.date_posted})"