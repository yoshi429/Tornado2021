from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import backref
from tornado import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# followedの中間テーブル
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')), # フォローした側 
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')), # フォローされた側
    db.Column('timestamp', db.DateTime, nullable=False, default=datetime.utcnow),
)


# Tag と Post の中間テーブル
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
)

# goodテーブル
post_goods = db.Table('post_goods',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('timestamp', db.DateTime, nullable=False, default=datetime.utcnow),
)


class User(db.Model, UserMixin):
    """
    ユーザー
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    profile_id = db.relationship("Profile", backref='user', uselist=False)
    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

    followed = db.relationship(
                                'User', secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id), 
                                backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
                                )
    good_post = db.relationship(
                            'Post', secondary=post_goods,
                            backref=db.backref('good_user', lazy='dynamic')
                            )

    def __repr__(self):
        return f"{self.username}-{self.email}"

    def follow(self, user):
        """
        フォローメソッド
        """
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """
        フォローを外す
        """
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """
        フォローしているかどうか
        """
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """
        フォローしている人の投稿
        """
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Post.timestamp.desc())


class Profile(db.Model):
    """
    ユーザープロフィール
    """
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    image_data = db.Column(db.String(255), nullable=False, default='default.jpg')
    content = db.Column(db.String(255), nullable=False, default='')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"{self.user.username}-Profile"


class Category(db.Model):
    """
    カテゴリー
    """
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True) 
    category_name = db.Column(db.String(255), nullable=False)

    post = db.relationship('Post', backref='category', lazy=True)

    def __repr__(self):
        return self.category_name


class Tag(db.Model):
    """
    タグ
    """
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True) 
    tag_name = db.Column(db.String(255), nullable=False)

    post = db.relationship(
                            'Post', secondary=post_tags,
                            backref=db.backref('tags', lazy='dynamic')
                            )

    def __repr__(self):
        return self.tag_name


class Post(db.Model):
    """
    投稿　タイトルなど
    """
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    good_count = db.Column(db.Integer, nullable=False, default=0)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 

    comment = db.relationship('Comment', backref='post', lazy=True)
    post_child = db.relationship('PostChild', backref='post', lazy=True)

    def __repr__(self):
        return f"{self.title}-{self.user.username}"


class PostChild(db.Model):
    """
    投稿内容
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_data = db.Column(db.String(255), nullable=False)
    num = db.Column(db.Integer, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    

    def __repr__(self):
        return f"{self.post.title}-{self.num}"


class Comment(db.Model):
    """
    投稿に対するコメント
    """
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    

    def __repr__(self):
        return f"{self.post.title}-{self.content}"


