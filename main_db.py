

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session as DBSession

# ---------- 数据库 ----------
engine = create_engine("mysql+pymysql://root:Qq2584511473@localhost:3306/bookmanager?charset=utf8mb4")
Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    author = Column(String(100))
    isbn = Column(String(20), unique=True)
    available = Column(Boolean, default=True)

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

class CategoryCreate(BaseModel):
    name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def book_to_dict(b):              # 把 ORM 对象转成 dict（返回 JSON 用）
    return {"id": b.id, "title": b.title, "author": b.author, "isbn": b.isbn, "available": b.available}

def category_to_dict(c): return {"id": c.id, "name": c.name}

@app.post("/books")
def create_book(book: BookCreate, db: DBSession = Depends(get_db)):
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
def update_book(isbn: str, updated: BookCreate, db: DBSession = Depends(get_db)):
    book = db.query(Book).filter(Book.isbn == isbn).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    book.title = updated.title
    book.author = updated.author
    db.commit()
    return book_to_dict(book)

@app.delete("/books/{isbn}")
def delete_book(isbn: str, db: DBSession = Depends(get_db)):
    book = db.query(Book).filter(Book.isbn == isbn).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}

@app.post("/categories")
def create_category(category: CategoryCreate, db: DBSession = Depends(get_db)):
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return category_to_dict(new_category)

@app.get("/categories")
def list_categories(db: DBSession = Depends(get_db)):
    return [category_to_dict(c) for c in db.query(Category).all()]

