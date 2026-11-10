import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="Qq2584511473",   # ← 换成你刚设的
    charset="utf8mb4"
)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS bookmanager")
print("数据库 bookmanager 建好了")
conn.close()