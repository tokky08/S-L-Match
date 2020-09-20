import MySQLdb
import os

def mysql():

    # 接続する 
    # ローカルでのDB用
    # conn = MySQLdb.connect(
    #     unix_socket = '/Applications/MAMP/tmp/mysql/mysql.sock',
    #     user='root',
    #     passwd='root',
    #     host='localhost',
    #     db='flask'
    # )

    # RDB・本番環境DB用
    conn = MySQLdb.connect(
        user='admin',
        passwd='softbankf',
        # passwd='Fo3tVX9au',
        # host='private-db.c3zynucfwev6.us-east-1.rds.amazonaws.com',
        # host='testrds.c3zynucfwev6.us-east-1.rds.amazonaws.com',
        # host='localaccess.c3zynucfwev6.us-east-1.rds.amazonaws.com',
        # host='nysqlrds.c3zynucfwev6.us-east-1.rds.amazonaws.com',
        host='localaccess2.c3zynucfwev6.us-east-1.rds.amazonaws.com',
        # host='private-dbop.c3zynucfwev6.us-east-1.rds.amazonaws.com',
        db='flask',
        charset='utf8'
    )

    return conn

def create_table():

    conn = mysql()

    # カーソルを取得する
    cur = conn.cursor(MySQLdb.cursors.DictCursor)

    user_drop = "DROP TABLE IF EXISTS user"
    post_drop = "DROP TABLE IF EXISTS post"
    cur.execute(user_drop)
    cur.execute(post_drop)

    # テーブルの作成
    # sql = 'create table test (id int, content varchar(32))'
    user_table = """
        CREATE TABLE user (
        id INTEGER AUTO_INCREMENT,
        password TEXT NOT NULL,
        username VARCHAR(10) UNIQUE,
        university TEXT,
        course TEXT,
        major TEXT,
        grade INTEGER,
        birthday TEXT,
        mail VARCHAR(20) UNIQUE NOT NULL,
        biography TEXT,
        judge INTEGER,
        PRIMARY KEY (id)
        )
    """

    cur.execute(user_table)

    post_table = """
        CREATE TABLE post (
        id INTEGER AUTO_INCREMENT,
        lab TEXT NOT NULL,
        university TEXT NOT NULL,
        course TEXT ,
        video_url TEXT,
        major TEXT,
        area TEXT,
        teacher TEXT,
        author_id INTEGER NOT NULL,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        PRIMARY KEY (id)
        )
    """
    # FOREIGN KEY (author_id) REFERENCES user (id)

    cur.execute(post_table)

    cur.close
    conn.close