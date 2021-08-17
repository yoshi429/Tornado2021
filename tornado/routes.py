from flask import request, jsonify, redirect, url_for, render_template
from flask_login import login_user, current_user, logout_user, login_required
from tornado import app, db, bcrypt 
from tornado.models import User, Profile, followers, Post, PostChild, Comment, Good
from tornado.utils import list_post, post_detail_list


@app.route("/")
def test():
    return render_template('index.html')


@app.route("/home")
def home():
    return render_template('home.html')



# ユーザー登録 プロフィール自動登録
@app.route("/user/register", methods=['POST'])
def user_register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

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
    
    return jsonify({'message': '登録されました'})


# ログイン
@app.route("/user/login", methods=['POST'])
def user_login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user, remember=data['remember'])
        return jsonify({'message': "ログインできました"})
    else:
        return jsonify({'message': "メールアドレスかパスワードが間違っています。確認しください。"}), 404



# ログアウト
@app.route("/user/logout", methods=['POST'])
def user_logout():
    username = current_user.username
    logout_user()
    return jsonify({'message': f"{username}さんログアウトできました"})


# プロフィール
@app.route("/user/profile/<int:user_id>", methods=['GET', 'POST'])
@login_required
def profile(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'userが見つかりません'})

    if request.method == 'POST':
        if user != current_user:
            return jsonify({'message': 'ユーザーの編集はできません'}), 404
        profile = Profile.query.filter_by(user_id=user_id).first()
        data = request.get_json()
        profile.image_data = data['image_data'] or "default.jpg"
        profile.location = data['location']
        profile.content = data['content']
        db.session.commit()
        return jsonify({'message': f"{current_user.username}さんのプロフィールを変更しました"})

    elif request.method == 'GET':
        profile = Profile.query.filter_by(user_id=user_id).first()
        return jsonify({
                        'username': profile.user.username, 'email': profile.user.email, 'content': profile.content, 
                        'image_data': profile.image_data, 'location': profile.location, "follower": profile.user.followers.count(),
                        "follewed": user.followed.count(),
                        })


# フォロー、フォロー外す機能
@app.route("/user/action/<int:user_id>", methods=['POST'])
@login_required
def user_handle_action(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'のユーザーは存在しません。'})
    data = request.get_json()
    action = data['action']

    if user == current_user:
        return jsonify({'message': '自分をフォローすることは出来ません'})

    if action == 'follow':
        current_user.follow(user)
        db.session.commit()
        return jsonify({'message': f"{current_user.username}が{user.username}をフォローしました"})

    elif action == 'unfollow':
        current_user.unfollow(user)
        db.session.commit()
        return jsonify({'message': f"{current_user.username}が{user.username}をフォローを外しました"})    
    
    else:
        return jsonify({'message': "無効なアクションです。"})


# フォローリスト
@app.route("/user/follow-list/<int:user_id>", methods=['GET'])
def user_followed_list(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'userが見つかりません'})

    followList = []
    for user_query in user.followed:
        d = {
            "userName": user_query.username,
            "userId": user_query.id,
            "imageData": user_query.profile_id.image_data
        }
        followList.append(d)

    return jsonify({'message': user.username, "follow_count": user.followed.count(), "followList": followList})


# フォローワーリスト
@app.route("/user/follower-list/<int:user_id>", methods=['GET'])
def user_follower_list(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        print(user)
    except:
        return jsonify({'message': 'userが見つかりません'})

    followerList = []
    for user_query in user.followers:
        print(user_query.username)
        d = {
            "userName": user_query.username,
            "userId": user_query.id,
            "imageData": user_query.profile_id.image_data
        }
        followerList.append(d)
    
    return jsonify({'message': user.username, "follower_count": user.followers.count(), "followerList": followerList})


#　仮
# 自分がフォローしている人の投稿リスト
@app.route("/user/follow-posts", methods=['GET'])
@login_required
def my_follow_user_posts():
    posts = current_user.followed_posts()
    print(posts)
    return jsonify({'message': current_user.username, "followPostList": list_post(posts)})


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


#　仮
# 自分のいいねリスト
@app.route("/user/my-good-list", methods=['GET'])
@login_required
def my_good_list():
    goods = Good.query.filter_by(user=current_user)
    
    my_good_post_list = []
    for good in goods:
        post = good.post
        main_post = post.post_child[0]
        d = {
            'postId': post.id,
            'title': post.title,
            'timeStamp': post.timestamp,
            'userName': post.user.username,
            'userId': post.user.id,
            'goodCount': Good.query.filter_by(post=post).count(),
            'imageData': main_post.image_data,
            'content': main_post.content,
            'location': main_post.location,
            'lat': main_post.lat,
            'lng': main_post.lng
            }
        my_good_post_list.append(d)

    return jsonify({'message': current_user.username, "myGoodPostList": my_good_post_list})


# 投稿
@app.route("/post/new", methods=['POST'])
@login_required
def new_post():
    data = request.get_json()
    title = data['title']
    post = Post(title=title, user=current_user)
    db.session.add(post)
    
    for i, child_data in enumerate(data['postChild'], start=1):
        db.session.add(PostChild(
                content=child_data['content'], 
                location=child_data['location'],
                lat=child_data['lat'],
                lng=child_data['lng'], 
                image_data=child_data['image_data'], 
                category=child_data['category'], 
                num=int(child_data['num']),
                post=post
                ))
        
    db.session.commit()
    return jsonify({'message': current_user.username,})


# 投稿に対してのコメント
@app.route("/post/comment/<int:post_id>", methods=['POST'])
@login_required
def new_comment(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404
    
    data = request.get_json()
    content = data['content']
    
    db.session.add(Comment(post=post, user=current_user, content=content))
    db.session.commit()
    return jsonify({'message': f"{current_user.username}-{content}",})


# 投稿に対してのいいね
@app.route("/post/good/<int:post_id>", methods=['POST'])
@login_required
def post_handle_good(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404
    
    good = Good.query.filter_by(user=current_user, post=post).first()
    
    if good is None:
        db.session.add(Good(user=current_user, post=post))
        db.session.commit()
        return jsonify({'message': f"{current_user.username}が{post.title}にいいねしました。",})
    elif good:
        db.session.delete(good)
        db.session.commit()
        return jsonify({'message': f"{current_user.username}が{post.title}にいいねを外しました。",})    
    else:
        return jsonify({'message': "無効なアクションです。",})


# 投稿の詳細画面
@app.route("/post/<int:post_id>", methods=['GET'])
def post_detail(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404
    
    post_childs = post.post_child
    print(post_childs)

    return jsonify({"post_detail": post_detail_list(post_childs)})


# 投稿リスト
@app.route("/post/list", methods=['GET'])
def post_list():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    print(posts)
    return jsonify({"postList": list_post(posts)})


