import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session as DBSession
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
# ---------- 数据库 ----------
engine = create_engine("mysql+pymysql://root:Qq2584511473@localhost:3306/bookmanager?charset=utf8mb4")
Base = declarative_base()

SECRET_KEY = "f8271afa29767d5fdae0c9abb38b99f71aa6a5fc51ee729366b8236c7b154359"
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    author = Column(String(100))
    isbn = Column(String(20), unique=True)
    available = Column(Boolean, default=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100))
    hashed_password = Column(String(100))

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# ---------- FastAPI ----------
app = FastAPI()

class BookCreate(BaseModel):      # 请求模型：用户创建时传的
    title: str
    author: str
    isbn: str

class UserRegister(BaseModel):
    username: str
    password: str

class CategoryCreate(BaseModel):
    name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def book_to_dict(b):              # 把 ORM 对象转成 dict（返回 JSON 用）
    return {"id": b.id, "title": b.title, "author": b.author, "isbn": b.isbn, "available": b.available}

def user_to_dict(u):
    return {"username": u.username}

def category_to_dict(c):
    return {"id": c.id, "name": c.name}

@app.post("/register")
def register_user(user: UserRegister, db: DBSession = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = bcrypt.hashpw(user.password.encode('utf-8'),bcrypt.gensalt()).decode()

    new_user = User(username = user.username, hashed_password = hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return user_to_dict(new_user)

@app.post("/login")
def login_user(from_data:OAuth2PasswordRequestForm = Depends(), db: DBSession = Depends(get_db)):
    db_user = db.query(User).filter(User.username == from_data.username).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not bcrypt.checkpw(from_data.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_token(from_data.username)
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/books")
def create_book(book: BookCreate, db: DBSession = Depends(get_db),current_user: str = Depends(get_current_user)):
    new_book = Book(title=book.title, author=book.author, isbn=book.isbn)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return book_to_dict(new_book)

@app.get("/books")
def list_books(db: DBSession = Depends(get_db)):
    return [book_to_dict(b) for b in db.query(Book).all()]

@app.get("/books/{isbn}")
def get_book(isbn: str, db: DBSession = Depends(get_db)):
    book = db.query(Book).filter(Book.isbn == isbn).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book_to_dict(book)

@app.put("/books/{isbn}")
def update_book(isbn: str, updated: BookCreate, db: DBSession = Depends(get_db),current_user: str = Depends(get_current_user)):
    book = db.query(Book).filter(Book.isbn == isbn).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    book.title = updated.title
    book.author = updated.author
    db.commit()
    return book_to_dict(book)

@app.delete("/books/{isbn}")
def delete_book(isbn: str, db: DBSession = Depends(get_db),current_user: str = Depends(get_current_user)):
    book = db.query(Book).filter(Book.isbn == isbn).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}

@app.post("/categories")
def create_category(category: CategoryCreate, db: DBSession = Depends(get_db),current_user: str = Depends(get_current_user)):
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return category_to_dict(new_category)

@app.get("/categories")
def list_categories(db: DBSession = Depends(get_db)):
    return [category_to_dict(c) for c in db.query(Category).all()]

