from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from dotenv import load_dotenv
import os

# load environment variables from .env
load_dotenv()
username = os.environ["USER_NAME"]
password = os.environ["PASSWORD"]

# Flask and SQLAlchemy Config
app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{username}:{password}@localhost:5432/perpustakaan"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Models
# User table
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.String, primary_key=True, unique=True, index=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False, default="member")

    def __repr__(self):
        return f"<User {self.name}>"


# Book table
class Book(db.Model):
    __tablename__ = "book"

    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    title = db.Column(db.String, nullable=False)
    pages = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Book {self.title}>"


# Author table
class Author(db.Model):
    __tablename__ = "author"

    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Author {self.name}>"


# Genre table
class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Genre {self.name}>"


# Transaction table
class Borrow(db.Model):
    __tablename__ = "borrow"

    id = db.Column(db.String, primary_key=True, unique=True, index=True)
    book_id = db.Column(db.String, db.ForeignKey("book.id"), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<Borrow status: {self.status}>"


# Book-Author table
class Book_Author(db.Model):
    book_id = db.Column(
        db.String, db.ForeignKey("book.id"), primary_key=True, nullable=False
    )
    author_id = db.Column(
        db.String, db.ForeignKey("author.id"), primary_key=True, nullable=False
    )

    def __repr__(self):
        return f"<Book-Author: {self.book_id}-{self.author_id}>"


# Book-Genre table
class Book_Genre(db.Model):
    book_id = db.Column(
        db.String, db.ForeignKey("book.id"), primary_key=True, nullable=False
    )
    genre_id = db.Column(
        db.String, db.ForeignKey("genre.id"), primary_key=True, nullable=False
    )

    def __repr__(self):
        return f"<Book-Genre: {self.book_id}-{self.genre_id}>"


# Auth
def login():
    data_email = request.authorization["username"]
    data_pwd = request.authorization["password"]
    user = User.query.filter_by(email=data_email).first()
    if not user:
        return "unauthorized"

    if user.password != data_pwd:
        return "Wrong pwd"

    if user.type == "admin":
        return "admin"
    else:
        return "member"


# Routes
@app.get("/")
def welcome():
    return {"message": "Welcome to API Perpustakaan"}


# Users
@app.get("/users")
def get_users():
    if login() == "admin":
        result = [{"name": user.name, "type": user.type} for user in User.query.all()]
        return {"users": result}
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 404
    else:
        return {"message": "Unauthorized"}, 401


@app.get("/user/<id>")
def get_user(id):
    if login() == "admin":
        user = User.query.get(id)
        result = {"name": user.name, "type": user.type, "email": user.email}
        return {"user details": result}
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 404
    else:
        return {"message": "Unauthorized"}, 401


@app.post("/user")
def create_user():
    data = request.get_json()

    nextval = db.session.execute(text("SELECT nextval('user_id_seq')")).scalar()
    u_id = "user" + str(nextval).zfill(3)

    new_user = User(
        id=u_id,
        name=data["name"],
        email=data["email"],
        password=data["password"],
        # type="admin",
    )
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User account successfully created"}, 201


if __name__ == "__main__":
    app.run(debug=True)
