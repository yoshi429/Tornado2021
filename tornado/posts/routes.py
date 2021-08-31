from flask import (
    request, jsonify, redirect, 
    url_for, render_template, request, 
    Blueprint)
from flask_login import (
    current_user, login_required)

from tornado import db 
from tornado.models import (
    User, post_tags,
    Post, PostChild, Comment, 
    post_goods, Category, Tag,
    )
from tornado.utils import save_pictures_s3


posts = Blueprint('posts', __name__)


# 投稿
@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():

    if request.method == 'POST':

        category = request.form['category'] 
        title = request.form['title']
        content = request.form['content']
        
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
        return redirect(url_for('posts.post_list'))

    else:
        return render_template('post/new_post.html')


# 投稿に対してのコメント
@posts.route("/post/comment/<int:post_id>", methods=['POST'])
@login_required
def new_comment(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404
    
    content = request.form['content']
    
    db.session.add(Comment(post=post, user=current_user, content=content))
    db.session.commit()
    return redirect(url_for('posts.post_list'))


# 投稿に対してのいいね
@posts.route("/post/good/<int:post_id>", methods=['POST'])
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
    return redirect(url_for('posts.post_list'))



# 投稿の詳細画面
@posts.route("/post/<int:post_id>", methods=['GET'])
def post_detail(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        print('投稿が見つかりません。')
        return redirect('posts.post_list')

    if post is None:
        return jsonify({'message': "この投稿は存在しません。", "status_code": 404}) ,404

    return render_template('post/post_detail.html', post=post)


# 投稿リスト カテゴリー検索
@posts.route("/", methods=['GET', 'POST'])
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
@posts.route("/post/comment/<int:post_id>/list", methods=['GET'])
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
@posts.route("/post/good/<int:post_id>/list", methods=['GET'])
@login_required
def good_user_list(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is None:
        print('投稿が見つかりません。')
        return redirect('post_list')

    users = post.good_user

    return render_template('user/user_list.html', users=users)


# 全体ランキング　カテゴリー別ランキング
@posts.route("/post/ranking", methods=['GET'])
@posts.route("/post/ranking/<int:category_id>", methods=['GET'])
def ranking_list(category_id=None):
    
    if category_id:
        category = Category.query.filter_by(id=category_id).first()
        if category is not None:
            posts = category.post.order_by(Post.good_count.desc()).all()

    else:
        posts = Post.query.order_by(Post.good_count.desc()).all()

    print(posts)

    return render_template('post/ranking.html', posts=posts)
