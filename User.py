import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session as DBSession
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

engine = create_engine("mysql+pymysql://root:Qq2584511473@localhost:3306/bookmanager?charset=utf8mb4")
Base = declarative_base()
SECRET_KEY = "119bb1ccd6e45fdefd2171b3cff39c7a6f7c157488e18bfe5cfd87aa58bfed9a"   # 签名密钥（生产环境要保密）
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True)
    hashed_password = Column(String(200))        # 存哈希，不存明文

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()

class UserRegister(BaseModel):
    username: str
    password: str                                # 用户传的是明文，服务器负责哈希

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_token(username: str) -> str:
    payload = {
        "sub": username,                                  # 主体：用户名
        "exp": datetime.utcnow() + timedelta(hours=24),   # 24 小时后过期
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register")
def register(user: UserRegister, db: DBSession = Depends(get_db)):
    # ① 用户名不能重复
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # ② 哈希密码
    hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # ③ 存数据库
    new_user = User(username=user.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ④ 返回时【绝不返回密码/哈希】！
    return {"id": new_user.id, "username": new_user.username}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: DBSession = Depends(get_db)):
    # ① 找用户
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if db_user is None:
        raise HTTPException(status_code=401, detail="Wrong username or password")

    # ② 验证密码（bcrypt 比对）
    if not bcrypt.checkpw(form_data.password.encode("utf-8"), db_user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Wrong username or password")

    # ③ 生成 JWT 并返回
    token = create_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/me")
def read_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}
