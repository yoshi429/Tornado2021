from flask import request, jsonify, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from tornado import app, db, bcrypt 
from tornado.models import User


@app.route("/home")
def home():
    return 'Hello'




@app.route("/user-register", methods=['POST'])
def user_register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    if User.query.filter_by(username=username).first():
        return jsonify({'message': "このユーザーネームは既に登録されています。"}, )
    if User.query.filter_by(email=email).first():
        return jsonify({'message': "このメールアドレスは既に登録されています。"}, )
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': '登録されました'}, 200)


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
        return jsonify({'message': "ログインできました"}, )
    else:
        return jsonify({'message': "メールアドレスかパスワードが間違っています。確認しください。"}, )


@app.route("/user-logout", methods=['POST'])
def user_logout():
    username = current_user.username
    logout_user()
    return jsonify({'message': f"{username}さんログアウトできました"}, )