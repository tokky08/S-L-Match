import MySQLdb



# 接続する 
conn = MySQLdb.connect(
    unix_socket = '/Applications/MAMP/tmp/mysql/mysql.sock',
    user='root',
    passwd='root',
    host='localhost',
    db='flask'
)

# conn = mysql()

# カーソルを取得する
# cur = conn.cursor()
cur = conn.cursor(MySQLdb.cursors.DictCursor)

# user_select = "SELECT * FROM user;"
cur.execute("SELECT * FROM user;")
test = cur.fetchone()

print(test)

cur.execute("SELECT * FROM post;")
test1 = cur.fetchone()

print(test1)

# user_drop = "DROP TABLE IF EXISTS user"
# post_drop = "DROP TABLE IF EXISTS post"
# cur.execute(user_drop)
# cur.execute(post_drop)



cur.close
conn.close