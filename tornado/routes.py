from flask import request, jsonify, redirect, url_for, render_template
from flask_login import login_user, current_user, logout_user, login_required
from tornado import app, db, bcrypt 
from tornado.models import User, Profile


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


# プロフィール編集
@app.route("/user-profile/<int:user_id>", methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
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
                        'image_data': profile.image_data, 'location': profile.location, "follower": profile.user.followers.count()
                        })
    return jsonify({})