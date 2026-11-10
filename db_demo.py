from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# ① 连接 MySQL
engine = create_engine(
    "mysql+pymysql://root:Qq2584511473@localhost:3306/bookmanager?charset=utf8mb4"
)

# ② 定义 Base（所有模型的父类）
Base = declarative_base()

# ③ 定义模型：每个 class 对应数据库里的一张表
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)   # 主键，自增
    title = Column(String(100))                                  # 书名
    author = Column(String(100))                                 # 作者
    isbn = Column(String(20), unique=True)                       # 编号，唯一
    available = Column(Boolean, default=True)                    # 是否在库

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    student_id = Column(String(20), unique=True)

# ④ 建表（把所有模型映射成真实的表，已存在就跳过）
Base.metadata.create_all(engine)

# ⑤ Session：操作数据的工作单元
Session = sessionmaker(bind=engine)
session = Session()

# ⑥ 增：加一本书
book = Book(title="Python入门", author="张三", isbn="111")
session.add(book)
session.commit()

# ⑦ 查：把所有书查出来
for b in session.query(Book).all():
    print(b.id, b.title, b.author, "available:", b.available)

session.close()