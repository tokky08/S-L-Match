# coding: UTF-8
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

# from flaskr.db import get_db
from . import db_mysql
import MySQLdb


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():

    if request.method == 'POST':
        username = request.form['username'].encode("utf-8")
        password = request.form['password'].encode("utf-8")
        university = request.form['university'].encode("utf-8")
        course = request.form['course'].encode("utf-8")
        major = request.form['major'].encode("utf-8")
        grade = request.form['grade'].encode("utf-8")
        birthday = request.form['birthday'].encode("utf-8")
        mail = request.form['mail'].encode("utf-8")
        biography = request.form['biography'].encode("utf-8")
        judge = request.form['judge'].encode("utf-8")

        conn = db_mysql.mysql()
        db = conn.cursor(MySQLdb.cursors.DictCursor)
        
        error = None
        
        # db.execute('set names utf8')
        # db.execute('charset utf8')
        db.execute(
            'SELECT id FROM user WHERE username = %s',(username,)
        )
        result = db.fetchone()

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif result is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, university, course, major, grade, birthday, mail, biography, judge) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (username, generate_password_hash(password), university, course, major, grade, birthday, mail, biography, judge)
            )
            conn.commit()
            return redirect(url_for('auth.login', _external=True, _scheme='https'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username'].encode("utf-8")
        password = request.form['password'].encode("utf-8")
        conn = db_mysql.mysql()
        db = conn.cursor(MySQLdb.cursors.DictCursor)
        db.execute('set names utf8')
    
        error = None
        db.execute(
            'SELECT * FROM user WHERE username = %s', (username,)
        )
        user = db.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user["password"], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user["id"]
            return redirect(url_for('index', _external=True, _scheme='https'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    conn = db_mysql.mysql()
    get_db = conn.cursor(MySQLdb.cursors.DictCursor)

    if user_id is None:
        g.user = None
    else:
        get_db.execute(
            'SELECT * FROM user WHERE id = %s', (user_id,)
        )
        g.user = get_db.fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index', _external=True, _scheme='https'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', _external=True, _scheme='https'))

        return view(**kwargs)

    return wrapped_view