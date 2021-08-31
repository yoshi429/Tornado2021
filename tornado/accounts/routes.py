from flask import (
    request, jsonify, redirect, url_for, 
    render_template, request, Blueprint)
from flask_login import (
    login_user, current_user, 
    logout_user, login_required)

from tornado import db, bcrypt 
from tornado.models import (
    User, Profile, followers, 
    Post)
from tornado.utils import save_pictures_s3


accounts = Blueprint('accounts', __name__)


# ユーザー登録 プロフィール自動登録
@accounts.route("/user/register", methods=['GET', 'POST'])
def user_register():
    if current_user.is_authenticated:
        return redirect(url_for('posts.post_list'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return jsonify({'message': "このユーザーネームは既に登録されています。"}), 404

        if User.query.filter_by(email=email).first():
            return jsonify({'message': "このメールアドレスは既に登録されています。"}), 404
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(username=username, email=email, password=hashed_password)
        profile = Profile(user=user)
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        print('登録されました')
        return redirect(url_for('posts.post_list'))

    else:
        return render_template('user/register.html')
    


# ログイン
@accounts.route("/user/login", methods=['POST', 'GET'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('posts.post_list'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form['remember']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            return redirect(url_for('posts.post_list'))
        else:
            print("メールアドレスかパスワードが間違っています。確認しください。")
            return jsonify({'message': "メールアドレスかパスワードが間違っています。確認しください。"}), 404
    else:
        return render_template('user/login.html')

# ログアウト
@accounts.route("/user/logout")
def user_logout():
    logout_user()
    return redirect(url_for('accounts.user_login'))


# プロフィール
@accounts.route("/user/profile/<int:user_id>", methods=['GET'])
def profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'userが見つかりません'})
    

    profile = Profile.query.filter_by(user_id=user_id).first()
    posts = Post.query.filter_by(user_id=user_id).all()
    image_path = url_for('static', filename='profile_pictures/' + profile.image_data)

    return render_template('user/profile.html', user=user,  profile=profile, posts=posts, image_path=image_path)


# プロフィール編集
@accounts.route("/user/profile/<int:user_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'userが見つかりません'})

    if request.method == 'POST':
        if user != current_user:
            print('ユーザーの編集はできません')
            return jsonify({'message': 'ユーザーの編集はできません'}), 404
    
        profile = Profile.query.filter_by(user_id=user_id).first()

        if request.files['image_data']:
            picture_file = image_data=save_pictures_s3(
                            picture=request.files['image_data'],
                            user_id=current_user.id
                        ),
            profile.image_data = picture_file

        profile.content = request.form['content']
        db.session.commit()
        return redirect(url_for('accounts.profile', user_id=user_id))

    elif request.method == 'GET':
        print('GET')
        profile = Profile.query.filter_by(user_id=user_id).first()
        image_path = url_for('static', filename='profile_pictures/' + profile.image_data)

        return render_template('user/edit_profile.html', user=user,  profile=profile, image_path=image_path)


# フォロー、フォロー外す機能
@accounts.route("/user/action/<int:user_id>", methods=['POST'])
@login_required
def user_handle_action(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'userが見つかりません'})

    if user == current_user:
        return jsonify({'message': '自分をフォローすることは出来ません'})

    # 既にフォローしている場合
    if current_user.is_following(user):
        current_user.unfollow(user)
        db.session.commit()
    # フォローしていない場合
    else: 
        current_user.follow(user)
        db.session.commit()

    return redirect(url_for('accounts.profile', user_id=user_id))


# フォローリスト
@accounts.route("/user/follow-list/<int:user_id>", methods=['GET'])
def user_followed_list(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'userが見つかりません'})

    followed_users = user.followed

    return render_template('user/user_list.html', users=followed_users)


# フォローワーリスト
@accounts.route("/user/follower-list/<int:user_id>", methods=['GET'])
def user_follower_list(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'userが見つかりません'})

    followers_users = user.followers

    return render_template('user/user_list.html', users=followers_users)


# 自分がフォローしている人の投稿リスト
@accounts.route("/user/follow-posts", methods=['GET'])
@login_required
def my_follow_user_posts():
    posts = current_user.followed_posts()
    print(posts)
    return render_template('post/post_list.html', posts=posts)


#　仮
# ユーザー個人の投稿
@accounts.route("/user/post-list/<int:user_id>", methods=['GET'])
def user_post_list(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'userが見つかりません'})
    posts = user.posts
    return jsonify({'message': user.username, "userPostList": posts})


# 自分のいいねリスト
@accounts.route("/user/my-good-list", methods=['GET'])
@login_required
def my_good_list():
    
    posts = current_user.good_post

    return render_template('post/post_list.html', posts=posts, selectedTab="good")