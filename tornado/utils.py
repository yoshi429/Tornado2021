import os
import secrets
from PIL import Image
from flask import current_app
from tornado.models import Good


def save_picture(json_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(json_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pictures', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(json_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn



def list_post(posts):
    post_list = []
    for post in posts:
        print(post)
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
        post_list.append(d)
        print(post_list)
    return post_list


def post_detail_list(post_childs):
    post_detail = []
    for post_child in post_childs:
        d = {
            "content": post_child.content,
            "image_data": post_child.image_data,
            "location": post_child.location,
            "lat": post_child.lat,
            "lng": post_child.lng,
            "category": post_child.category,
            "num": post_child.num
        }
        post_detail.append(d)
    return post_detail