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
    title = db.Column(db.String, nullable=False, unique=True)
    pages = db.Column(db.SmallInteger, nullable=False, default=1)
    publisher = db.Column(db.String, nullable=True)
    published_year = db.Column(db.SmallInteger, nullable=True, default=1000)

    def __repr__(self):
        return f"<Book {self.title}>"


# Author table
class Author(db.Model):
    __tablename__ = "author"

    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False, unique=True)
    birth_year = db.Column(db.SmallInteger, nullable=True, default=1000)

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
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.get("/user/<id>")
def user_details(id):
    if login() == "admin":
        user = User.query.get(id)
        result = {"name": user.name, "type": user.type, "email": user.email}
        return {"user details": result}
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.post("/user")
def create_user():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()
    if user:
        return {"message": "Account with that email already exists"}
    
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


@app.get("/books")
def get_books():
    result = [{"title": book.title} for book in Book.query.all()]
    return {"books": result}


@app.get("/book/<id>")
def book_details(id):
    book = Book.query.get(id)
    details = {
        "title": book.title,
        "num_of_page": book.pages,
        "published_year": book.published_year,
        "publisher": book.publisher,
    }
    return {"book": details}


@app.post("/book")
def add_book():
    if login() == "admin":
        data = request.get_json()
        book = Book.query.filter_by(title=data["title"]).first()
        if book:
            return {"message": "Book with that title already exists"}

        nextval = db.session.execute(text("SELECT nextval('book_id_seq')")).scalar()
        b_id = "bk" + str(nextval).zfill(3)

        new_book = Book(
            id=b_id,
            title=data["title"],
            pages=data["pages"],
        )
        db.session.add(new_book)
        db.session.commit()
        return {"message": "Book added"}, 201
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.put("/book/<id>")
def update_book(id):
    if login() == "admin":
        data = request.get_json()
        book = Book.query.get(id)
        book.title = data.get("title", book.title)
        book.pages = data.get("pages", book.pages)
        book.publisher = data.get("publisher", book.publisher)
        book.published_year = data.get("published_year", book.published_year)
        db.session.commit()
        return {"message": "Book updated"}
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.get("/genres")
def get_genres():
    result = [genre.name for genre in Genre.query.all()]
    return {"Genres": result}


@app.post("/genre")
def add_genre():
    if login() == "admin":
        data = request.get_json()
        genre = Genre.query.filter_by(name=data["genre_name"]).first()
        if genre:
            return {"message": "A genre already exists"}, 400

        nextval = db.session.execute(text("SELECT nextval('genre_id_seq')")).scalar()
        g_id = "ge" + str(nextval).zfill(3)

        new_genre = Genre(id=g_id, name=data["genre_name"])
        db.session.add(new_genre)
        db.session.commit()
        return {"message": "Genre added"}, 201
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.put("/genre/<id>")
def update_genre(id):
    if login() == "admin":
        data = request.get_json()
        genre = Genre.query.get(id)
        genre.name = data.get("genre_name", genre.name)
        db.session.commit()
        return {"message": "Genre updated"}
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.get("/authors")
def get_authors():
    result = [author.name for author in Author.query.all()]
    return {"Authors": result}


@app.get("/author/<id>")
def author_details(id):
    author = Author.query.get(id)
    print("aaaaaa", author)
    details = {"name": author.name, "birth_year": author.birth_year}
    return {"author details": details}


@app.post("/author")
def add_author():
    if login() == "admin":
        data = request.get_json()
        author = Author.query.filter_by(name=data["name"]).first()
        if author:
            return {"message": "Author already exists"}
        
        nextval = db.session.execute(text("SELECT nextval('author_id_seq')")).scalar()
        a_id = "au" + str(nextval).zfill(3)

        new_author = Author(
            id=a_id, name=data["name"], birth_year=data.get("birth_year", 1000)
        )
        db.session.add(new_author)
        db.session.commit()
        return {"message": "Author added"}, 201
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


if __name__ == "__main__":
    app.run(debug=True)
