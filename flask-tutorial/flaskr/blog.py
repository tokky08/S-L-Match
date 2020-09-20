# coding: UTF-8
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
# from flaskr.db import get_db
from . import db_mysql
import MySQLdb

bp = Blueprint('blog', __name__)

from werkzeug.utils import secure_filename
from flaskr.upload import upload_file_to_s3
import os

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'])
S3_BUCKET = os.environ.get('S3_BUCKET')

@bp.route('/detail', methods=('GET', 'POST'))
def detail():
    
    post_id = request.args.get("post_id")
    
    conn = db_mysql.mysql()
    db = conn.cursor(MySQLdb.cursors.DictCursor)
    db.execute(
        'SELECT *'
        ' FROM post'
        ' WHERE post.id = %s',  
        (post_id)
    )
    posts = db.fetchone()
    
    return render_template('blog/detail.html', posts=posts)

@bp.route('/', methods=('GET', 'POST'))
def index():
    conn = db_mysql.mysql()
    db = conn.cursor(MySQLdb.cursors.DictCursor)
    # db = get_db()
    # posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).fetchall()

    if request.method == 'POST':
        want_lab = request.form["lab"]
        want_university = request.form['university']
        want_teacher = request.form['teacher']
        want_course = request.form['course']
        want_major = request.form['major']
        want_area = request.form['area']#.encode("utf-8")
        want_teacher = request.form['teacher']
        want_course = request.form['course']
        want_major = request.form['major']
        error = None
        if error is not None:
            flash(error)
        else:
            # db.execute(
            #     'SELECT p.id, title, body, created, author_id, username'
            #     ' FROM post p JOIN user u ON p.author_id = u.id'
            #     ' WHERE p.lab=%s OR p.university=%s OR'
            #     ' teacher=%s OR p.course=%s OR'
            #     ' p.major=%s OR p.area=%s'
            #     ' ORDER BY created DESC',(want_lab, want_university, want_teacher, want_course, want_major, want_area)
            #)
            posts = [] 
            db.execute('SELECT p.id, title, body, created, author_id, username, lab, p.university, p.teacher, p.course, p.major, p.area, video_url'
                       ' FROM post p JOIN user u ON p.author_id = u.id')
            pre_posts = db.fetchall()
            for post in pre_posts:
                lab_check = want_lab in post['lab'] and want_lab != ''
                university_check = want_university in post['university'] and want_university != ''
                teacher_check = want_teacher in post['teacher'] and want_teacher != ''
                course_check = want_course in post['course'] and want_course != ''
                major_check = want_major in post['major'] and want_major != ''
                area_check = want_area in post['area'] and want_area != ''
                if (lab_check or university_check or teacher_check or course_check or major_check or area_check):
                    posts.append(post)
 
            num = len(posts)
            return render_template('blog/index.html', posts=posts, num=num)


    else:
        db.execute(
            'SELECT p.id, title, body, created, author_id, username, lab, p.university, p.teacher, p.course, p.major, p.area, video_url'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        )
        posts = db.fetchall()
        num = len(posts)
        return render_template('blog/index.html', posts=posts, num=num)

# ROUTES
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title'].encode("utf-8")
        body = request.form['body'].encode("utf-8")
        lab = request.form['lab'].encode("utf-8")
        university = request.form['university'].encode("utf-8")
        course = request.form['course'].encode("utf-8")
        major = request.form['major'].encode("utf-8")
        file = request.files["user_file"]
        video = file.filename
        area = request.form['area'].encode("utf-8")
        teacher = request.form['teacher'].encode("utf-8")
        video_name = video.split('.')[0]
        print(video_name)
        video_url = 'https://lab-ken-video.com/media-convert/' + video_name + '-converted.mp4'
        print(type(video_url))
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            # S3へのアップロード
            if "user_file" not in request.files:
                return "No user_file key in request.files"

            file = request.files["user_file"]
            print(file)

            # There is no file selected to upload
            if file.filename == "":
                return "Please select a file"

            # File is selected, upload to S3 and show S3 URL
            if file and allowed_file(file.filename):
                file.filename = secure_filename(file.filename)
                print(file.filename)
                output = upload_file_to_s3(file, S3_BUCKET)
            
            conn = db_mysql.mysql()
            db = conn.cursor(MySQLdb.cursors.DictCursor)
            # print("g.user:{}".format(g.user))
            # db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, lab, university, course, major, area, teacher, video_url)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (title, body, g.user["id"], lab, university, course, major, area, teacher, video_url)
                # (title, body, g.user['id'])
            )
            # db.commit()
            conn.commit()
            return redirect(url_for('blog.index', _external=True, _scheme='https'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    conn = db_mysql.mysql()
    db = conn.cursor(MySQLdb.cursors.DictCursor)
    db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    post = db.fetchone()
    # post = get_db().execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' WHERE p.id = ?',
    #     (id,)
    # ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title'].encode("utf-8")
        body = request.form['body'].encode("utf-8")
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            conn = db_mysql.mysql()
            db = conn.cursor(MySQLdb.cursors.DictCursor)
            # db = get_db()
            db.execute(
                'UPDATE post SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, id)
            )
            # db.commit()
            conn.commit()
            return redirect(url_for('blog.index', _external=True, _scheme='https'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    conn = db_mysql.mysql()
    db = conn.cursor(MySQLdb.cursors.DictCursor)
    # db = get_db()
    db.execute('DELETE FROM post WHERE id = %s', (id,))
    # db.commit()
    conn.commit()
    return redirect(url_for('blog.index', _external=True, _scheme='https'))
    
@bp.route('/question', methods=('GET', 'POST'))
def question():
    return render_template('blog/question.html')