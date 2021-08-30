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
from tornado.utils import save_picture, save_pictures_s3


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
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'userが見つかりません'})
    

    profile = Profile.query.filter_by(user_id=user_id).first()
    posts = Post.query.filter_by(user_id=user_id).all()
    image_path = url_for('static', filename='profile_pictures/' + profile.image_data)

    return render_template('user/profile.html', user=user,  profile=profile, posts=posts, image_path=image_path)


# プロフィール編集
@app.route("/user/profile/<int:user_id>/edit", methods=['GET', 'POST'])
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

    return redirect(url_for('profile', user_id=user_id))


# フォローリスト
@app.route("/user/follow-list/<int:user_id>", methods=['GET'])
def user_followed_list(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'userが見つかりません'})

    followed_users = user.followed

    return render_template('user/user_list.html', users=followed_users)


# フォローワーリスト
@app.route("/user/follower-list/<int:user_id>", methods=['GET'])
def user_follower_list(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
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
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'userが見つかりません'})
    posts = user.posts
    return jsonify({'message': user.username, "userPostList": posts})


# 自分のいいねリスト
@app.route("/user/my-good-list", methods=['GET'])
@login_required
def my_good_list():
    
    posts = current_user.good_post

    return render_template('post/post_list.html', posts=posts, selectedTab="good")


# 投稿
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():

    if request.method == 'POST':
        
        category = request.form['category']
        title = request.form['title']
        content = request.form['content']
        if category == '':
            category = 'all'
        category = Category.query.filter_by(category_name=category).first()
        if category is None:
            print("無効なカテゴリーです。")
            return jsonify({'message': '無効なカテゴリーです。'})

        new_post = Post(title=title, content=content, user=current_user, category=category)

        # 1セット目
        spot_1_title = request.form['spot-1-title']
        spot_1_description = request.form['spot-1-description']
        spot_1_image = request.files['spot-1-image']

        # 2セット目
        spot_2_title = request.form['spot-2-title']
        spot_2_description = request.form['spot-2-description']
        spot_2_image = request.files['spot-2-image']

        # 3セット目
        spot_3_title = request.form['spot-3-title']
        spot_3_description = request.form['spot-3-description']
        spot_3_image = request.files['spot-3-image']

        # 4セット目
        spot_4_title = request.form['spot-4-title']
        spot_4_description = request.form['spot-4-description']
        spot_4_image = request.files['spot-4-image']

        # 5セット目
        spot_5_title = request.form['spot-5-title']
        spot_5_description = request.form['spot-5-description']
        spot_5_image = request.files['spot-5-image']

        # それぞれの情報をリスト化
        titles = [spot_1_title, spot_2_title, spot_3_title, spot_4_title, spot_5_title]        
        descriptions = [spot_1_description, spot_2_description, spot_3_description, spot_4_description, spot_5_description]
        images = [spot_1_image, spot_2_image, spot_3_image, spot_4_image, spot_5_image]


        count = 1
        for title, description, image in zip(titles,descriptions,images):
            # タイトルの有無で投稿があるか判断
            if title != '':

                # 投稿とタグを中間テーブルで結びつける
                words = description.split()
                for word in words:
                    if word[0] == "#":
                        tag = Tag.query.filter_by(tag_name=word).first()
                        if tag is None:
                            tag = Tag(tag_name=word[1:])
                        new_post.tags.append(tag)  

                PostChild(
                        title=title,
                        description =description,
                        image_data=save_pictures_s3(
                            picture=image,
                            user_id=current_user.id
                        ),
                        num=count,
                        post=new_post
                        )
                print(count)
                count += 1

        db.session.add(new_post)                        
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

    post.good_count = post.good_user.count()
    db.session.commit()
    return redirect(url_for('post_list'))



# 投稿の詳細画面
@app.route("/post/<int:post_id>", methods=['GET'])
def post_detail(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        print('投稿が見つかりません。')
        return redirect('post_list')

    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404

    return render_template('post/post_detail.html', post=post)


# 投稿リスト カテゴリー検索
@app.route("/post/list", methods=['GET', 'POST'])
def post_list():

    keyword = ''
    posts = None
    category=''

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
            category = Post.query.filter(Post.title.contains(keyword)).all()
            # category = PostChild.query.filter(PostChild.content.contains(keyword)).all()
            # category = Category.query.filter_by(category_name=keyword).first()　
            print(category)
            if category is not None:
                posts = category
                #posts = category.post
    else:
        category = request.args.get('category')
        if category is None:
          posts = Post.query.order_by(Post.timestamp.desc()).all()
        else:
          posts = Post.query.order_by(Post.timestamp.desc()).join(Category.query.filter_by(id=category)).all()
        

    return render_template('post/post_list.html', posts=posts, keyword=keyword, selectedTab=category if category is not None else '0')


# 投稿に対してのコメントリスト
@app.route("/post/comment/<int:post_id>/list", methods=['GET'])
@login_required
def comment_list(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        print('投稿が見つかりません。')
        return redirect('post_list')
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
            posts = category.post.order_by(Post.good_count.desc()).all()

    else:
        posts = Post.query.order_by(Post.good_count.desc()).all()

    print(posts)

    return render_template('post/ranking.html', posts=posts)
