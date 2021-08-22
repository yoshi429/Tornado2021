import re
from flask import request, jsonify, redirect, url_for, render_template, request
from flask_login import login_user, current_user, logout_user, login_required

from tornado import app, db, bcrypt 
from tornado.models import (
                            User, Profile, followers, 
                            Post, PostChild, Comment, 
                            post_goods, Category, Tag,
                            post_tags
                            )
from tornado.utils import list_post, post_detail_list, save_picture


@app.route("/")
def test():
    return render_template('index.html')


@app.route("/home")
def home():
    return render_template('home.html')



# ユーザー登録 プロフィール自動登録
@app.route("/user/register", methods=['GET', 'POST'])
def user_register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

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
        return redirect(url_for('home'))

    else:
        return render_template('user/register.html')
    


# ログイン
@app.route("/user/login", methods=['POST', 'GET'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form['remember']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            return redirect(url_for('home'))
        else:
            print("メールアドレスかパスワードが間違っています。確認しください。")
            return jsonify({'message': "メールアドレスかパスワードが間違っています。確認しください。"}), 404
    else:
        return render_template('user/login.html')

# ログアウト
@app.route("/user/logout")
def user_logout():
    logout_user()
    return redirect(url_for('user_login'))


# プロフィール
@app.route("/user/profile/<int:user_id>", methods=['GET'])
def profile(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'userが見つかりません'})
    

    profile = Profile.query.filter_by(user_id=user_id).first()
    posts = Post.query.filter_by(user_id=user_id).all()
    image_path = url_for('static', filename='profile_pictures/' + profile.image_data)

    return render_template('user/profile.html', user=user,  profile=profile, posts=posts, image_path=image_path)


# プロフィール編集
@app.route("/user/profile/<int:user_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'userが見つかりません'})

    if request.method == 'POST':
        if user != current_user:
            print('ユーザーの編集はできません')
            return jsonify({'message': 'ユーザーの編集はできません'}), 404
    
        profile = Profile.query.filter_by(user_id=user_id).first()

        if request.files['image_data']:
            picture_file = save_picture(
                                        picture=request.files['image_data'], 
                                        picture_save_path='static/profile_pictures'
                                        )
            profile.image_data = picture_file

        profile.content = request.form['content']
        db.session.commit()
        return redirect(url_for('profile', user_id=user_id))

    elif request.method == 'GET':
        print('GET')
        profile = Profile.query.filter_by(user_id=user_id).first()
        image_path = url_for('static', filename='profile_pictures/' + profile.image_data)

        return render_template('user/edit_profile.html', user=user,  profile=profile, image_path=image_path)


# フォロー、フォロー外す機能
@app.route("/user/action/<int:user_id>", methods=['POST'])
@login_required
def user_handle_action(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'のユーザーは存在しません。'})

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

    return redirect(url_for('profile', user_id=user_id))


# フォローリスト
@app.route("/user/follow-list/<int:user_id>", methods=['GET'])
def user_followed_list(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'userが見つかりません'})

    followed_users = user.followed

    return render_template('user/user_list.html', users=followed_users)


# フォローワーリスト
@app.route("/user/follower-list/<int:user_id>", methods=['GET'])
def user_follower_list(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'userが見つかりません'})

    followers_users = user.followers

    return render_template('user/user_list.html', users=followers_users)


# 自分がフォローしている人の投稿リスト
@app.route("/user/follow-posts", methods=['GET'])
@login_required
def my_follow_user_posts():
    posts = current_user.followed_posts()
    print(posts)
    return render_template('post/post_list.html', posts=posts)


#　仮
# ユーザー個人の投稿
@app.route("/user/post-list/<int:user_id>", methods=['GET'])
def user_post_list(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'userが見つかりません'})
    posts = user.posts
    print(posts)
    return jsonify({'message': user.username, "userPostList": list_post(posts)})


# 自分のいいねリスト
@app.route("/user/my-good-list", methods=['GET'])
@login_required
def my_good_list():
    
    posts = current_user.good_post

    return render_template('post/post_list.html', posts=posts)


# 投稿
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():

    if request.method == 'POST':

        title = request.form['title']
        contents=request.form['content'] 
        location=request.form['location']
        lat=request.form['lat']
        lng=request.form['lng'] 
        image_data=request.files['image_data'] 
        category=request.form['category']

        
        category = Category.query.filter_by(category_name=category).first()
        if category is None:
            print("無効なカテゴリーです。")
            return jsonify({'message': '無効なカテゴリーです。'})


        new_post = Post(title=title, user=current_user, category=category)
        # 投稿とタグを中間テーブルで結びつける
        
        words = contents.split()
        for word in words:
            if word[0] == "#":
                tag = Tag.query.filter_by(tag_name=word).first()
                if tag is None:
                    tag = Tag(tag_name=word[1:])
                new_post.tags.append(tag)  #


        post_child = PostChild(
                                content=contents, 
                                location=location,
                                lat=float(lat),
                                lng=float(lng), 
                                image_data=save_picture(
                                    picture=image_data, 
                                    picture_save_path='static/post_pictures'
                                            ), 
                                num=1,
                                post=new_post
                                )
        
        db.session.add(new_post)                        
        db.session.add(post_child)
        db.session.commit()
        return redirect(url_for('post_list'))

    else:
        return render_template('post/new_post.html')


# 投稿に対してのコメント
@app.route("/post/comment/<int:post_id>", methods=['POST'])
@login_required
def new_comment(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404
    
    content = request.form['content']
    
    db.session.add(Comment(post=post, user=current_user, content=content))
    db.session.commit()
    return redirect(url_for('post_list'))


# 投稿に対してのいいね
@app.route("/post/good/<int:post_id>", methods=['POST'])
@login_required
def post_handle_good(post_id):
    post = Post.query.filter_by(id=post_id).first()
    print(post.title)
    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404

    # 既にいいねしているかどうか
    if  post.good_user.filter(post_goods.c.user_id == current_user.id).count() > 0:
        # remove good
        current_user.good_post.remove(post)
    else:
        # add good
        current_user.good_post.append(post)

    db.session.commit()
    return redirect(url_for('post_list'))


# 投稿の詳細画面
@app.route("/post/<int:post_id>", methods=['GET'])
def post_detail(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404
    
    post_childs = post.post_child
    print(post_childs)

    return jsonify({"post_detail": post_detail_list(post_childs)})


# 投稿リスト カテゴリー検索
@app.route("/post/list", methods=['GET', 'POST'])
def post_list():

    keyword = ''
    posts = None

    if request.method == 'POST':
        keyword = request.form['keyword']
        print(keyword)
        if keyword[0] == '#':
            tag = Tag.query.filter_by(tag_name=keyword[1:]).first()
            if tag is not None:
                posts = tag.post
        elif keyword[0] == '@':
            user = User.query.filter_by(username=keyword[1:]).first()
            if user is not None:
                posts = user.posts
        else:
            category = Category.query.filter_by(category_name=keyword).first()
            if category is not None:
                posts = category.post
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    print(posts)

    return render_template('post/post_list.html', posts=posts, keyword=keyword)


# 投稿に対してのコメントリスト
@app.route("/post/comment/<int:post_id>/list", methods=['GET'])
@login_required
def comment_list(post_id):
    post = Post.query.filter_by(id=post_id).first()
    comments = post.comment
    print(comments)
    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404
    
    if comments is None:
        return jsonify({'message': "この投稿に対するコメントは存在しません。", "status_code": 404}) ,404

    comments_list = []
    for comment in comments:
        d = {
            "userId": comment.user.id,
            "userName": comment.user.username,
            "content": comment.content
        }
        comments_list.append(d)
    
    return jsonify({'commentsList': comments_list})


# 投稿に対してのいいねのユーザーリスト
@app.route("/post/good/<int:post_id>/list", methods=['GET'])
@login_required
def good_user_list(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        print('投稿が見つかりません。')
        return redirect('post_list')

    users = post.good_user

    return render_template('user/user_list.html', users=users)


# 全体ランキング　カテゴリー別ランキング
@app.route("/post/ranking", methods=['GET'])
@app.route("/post/ranking/<int:category_id>", methods=['GET'])
def ranking_list(category_id=None):
    
    if category_id:
        category = Category.query.filter_by(id=category_id).first()
        if category is not None:
            posts = category.post.order_by(Post.timestamp.desc()).all()

    else:
        posts = Post.query.order_by(Post.timestamp.desc()).all()

    print(posts)

    return render_template('post/ranking.html', posts=posts)
