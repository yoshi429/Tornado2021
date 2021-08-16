from flask import request, jsonify, redirect, url_for, render_template
from flask_login import login_user, current_user, logout_user, login_required
from tornado import app, db, bcrypt 
from tornado.models import User, Profile, followers


@app.route("/home")
def home():
    return 'Hello'



# ユーザー登録 プロフィール自動登録
@app.route("/user-register", methods=['POST'])
def user_register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
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
@app.route("/user-login", methods=['POST'])
def user_login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
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
@app.route("/user-logout", methods=['POST'])
def user_logout():
    username = current_user.username
    logout_user()
    return jsonify({'message': f"{username}さんログアウトできました"})


# プロフィール
@app.route("/user-profile/<int:user_id>", methods=['GET', 'POST'])
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
@app.route("/user-action/<int:user_id>", methods=['POST'])
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
@app.route("/user-follow-list/<int:user_id>", methods=['GET'])
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
@app.route("/user-follower-list/<int:user_id>", methods=['GET'])
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