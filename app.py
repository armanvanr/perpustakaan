from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from datetime import date
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
    author_list = db.relationship("Book_Author", backref="written_book", lazy="dynamic")
    genre_list = db.relationship("Book_Genre", backref="book", lazy="dynamic")

    def __repr__(self):
        return f"<Book {self.title}>"


# Author table
class Author(db.Model):
    __tablename__ = "author"

    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False, unique=True)
    birth_year = db.Column(db.SmallInteger, nullable=True, default=1000)
    book_list = db.relationship("Book_Author", backref="writer", lazy="dynamic")

    def __repr__(self):
        return f"<Author {self.name}>"


# Genre table
class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False)
    book_list = db.relationship("Book_Genre", backref="genre", lazy="dynamic")

    def __repr__(self):
        return f"<Genre {self.name}>"


# Transaction table
class Borrow(db.Model):
    __tablename__ = "borrow"

    id = db.Column(db.String, primary_key=True, unique=True, index=True)
    book_id = db.Column(db.String, db.ForeignKey("book.id"), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    book_title = db.Column(db.String, nullable=True)
    member_name = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=True)
    approve_admin = db.Column(db.String, nullable=True)
    return_admin = db.Column(db.String, nullable=True)
    requested_date = db.Column(db.Date, nullable=True)
    approved_date = db.Column(db.Date, nullable=True)
    returned_date = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Borrow status: {self.status}>"


# Book-Author table
class Book_Author(db.Model):
    __tablename__ = "book_author"

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
    __tablename__ = "book_genre"

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
        return ["unauthorized", 401]

    if user.password != data_pwd:
        return ["Wrong pwd", 400]

    if user.type == "admin":
        return ["admin", user.id]
    else:
        return ["member", user.id]


# Routes
@app.get("/")
def welcome():
    return {"message": "Welcome to API Perpustakaan"}


# Users
# show all users, accessible only for admins
@app.get("/users")
def get_users():
    u_type = login()[0]
    if u_type == "admin":
        result = [
            {"name": user.name, "type": user.type, "id": user.id}
            for user in User.query.all()
        ]
        return {"users": result}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# show details of a user, accessible only for admins
@app.get("/user/<id>")
def user_details(id):
    u_type = login()[0]
    if u_type == "admin":
        user = User.query.get(id)
        result = {"name": user.name, "type": user.type, "email": user.email}
        return {"user details": result}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# create a new member account
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
    )
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User account successfully created"}, 201


# create a new admin or upgrade an existing member to become admin
@app.post("/admin")
def create_admin():
    u_type = login()[0]
    if u_type == "admin":
        data = request.get_json()
        user = User.query.filter_by(email=data["email"]).first()

        # upgrade member to admin
        if user:
            user.type = "admin"

        # add a new admin
        else:
            nextval = db.session.execute(text("SELECT nextval('user_id_seq')")).scalar()
            u_id = "user" + str(nextval).zfill(3)

            new_user = User(
                id=u_id,
                name=data["name"],
                email=data["email"],
                password=data["password"],
                type="admin",
            )
            db.session.add(new_user)
        db.session.commit()
        return {"message": "Admin added"}, 201
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# update user data
@app.put("/user/<id>")
def update_user(id):
    u_type, u_id = login()
    # users can change only their own data
    if u_type == "admin" or "member":
        user = User.query.get(id)
        if user.id == u_id:
            data = request.get_json()
            user.name = data.get("name", user.name)
            user.password = data.get("password", user.password)
            db.session.commit()
            return {"message": "User data updated"}
        return {"message": "Unauthorized"}, 401
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# delete user data
@app.delete("/user/<id>")
def delete_user(id):
    u_type, u_id = login()
    # users can delete only their own account
    if u_type == "admin" or "member":
        user = User.query.get(id)
        if user.id == u_id:
            db.session.delete(user)
            db.session.commit()
            return {"message": "User data deleted"}
        return {"message": "Unauthorized"}, 401
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.get("/books")
def get_books():
    result = [{"title": book.title, "id": book.id} for book in Book.query.all()]
    return {"books": result}


@app.get("/book/<id>")
def book_details(id):
    book = Book.query.get(id)
    details = {
        "title": book.title,
        "num_of_page": book.pages,
        "published_year": book.published_year,
        "publisher": book.publisher,
        "genre": [item.genre.name for item in book.genre_list.all()],
        "author": [item.writer.name for item in book.author_list.all()],
    }
    return {"book": details}


@app.post("/book")
def add_book():
    u_type = login()[0]
    if u_type == "admin":
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
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.put("/book/<id>")
def update_book(id):
    u_type = login()[0]
    if u_type == "admin":
        data = request.get_json()
        book = Book.query.get(id)
        book.title = data.get("title", book.title)
        book.pages = data.get("pages", book.pages)
        book.publisher = data.get("publisher", book.publisher)
        book.published_year = data.get("published_year", book.published_year)
        db.session.commit()
        return {"message": "Book updated"}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.get("/genres")
def get_genres():
    result = [{"genre": genre.name, "id": genre.id} for genre in Genre.query.all()]
    return {"Genres": result}


@app.get("/genre/<id>")
def genre_details(id):
    genre = Genre.query.get(id)
    result = {
        "genre": genre.name,
        "books": [item.book.title for item in genre.book_list.all()],
    }
    return result


@app.post("/genre")
def add_genre():
    u_type = login()[0]
    if u_type == "admin":
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
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.put("/genre/<id>")
def update_genre(id):
    u_type = login()[0]
    if u_type == "admin":
        data = request.get_json()
        genre = Genre.query.get(id)
        genre.name = data.get("genre_name", genre.name)
        db.session.commit()
        return {"message": "Genre updated"}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.get("/authors")
def get_authors():
    result = [{"name": author.name, "id": author.id} for author in Author.query.all()]
    return {"Authors": result}


@app.get("/author/<id>")
def author_details(id):
    author = Author.query.get(id)
    print("aaaaaa", author)
    details = {
        "name": author.name,
        "birth_year": author.birth_year,
        "books": [item.written_book.title for item in author.book_list.all()],
    }
    return {"author details": details}


@app.post("/author")
def add_author():
    u_type = login()[0]
    if u_type == "admin":
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
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# Junction Tables' Endpoints
@app.get("/bookauthors")
def get_book_author():
    u_type = login()[0]
    if u_type == "admin":
        result = [
            {"book_id": ba.book_id, "author_id": ba.author_id}
            for ba in Book_Author.query.all()
        ]
        return {"book-author": result}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.post("/bookauthor")
def add_book_author():
    u_type = login()[0]
    if u_type == "admin":
        data = request.get_json()
        ba = Book_Author.query.filter_by(
            book_id=data["book_id"], author_id=data["author_id"]
        ).first()
        if ba:
            return {"message": "Data already inserted"}, 400

        new_input = Book_Author(book_id=data["book_id"], author_id=data["author_id"])
        db.session.add(new_input)
        db.session.commit()
        print(new_input)
        return {"message": "Book-Author data inserted"}, 201
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.get("/bookgenres")
def get_book_genre():
    u_type = login()[0]
    if u_type == "admin":
        result = [
            {"book_id": bg.book_id, "genre_id": bg.genre_id}
            for bg in Book_Genre.query.all()
        ]
        return {"book-genre": result}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.post("/bookgenre")
def add_book_genre():
    u_type = login()[0]
    if u_type == "admin":
        data = request.get_json()
        bg = Book_Genre.query.filter_by(
            book_id=data["book_id"], genre_id=data["genre_id"]
        ).first()
        if bg:
            return {"message": "Data already inserted"}, 400

        new_input = Book_Genre(book_id=data["book_id"], genre_id=data["genre_id"])
        db.session.add(new_input)
        db.session.commit()
        print(new_input)
        return {"message": "Book-Genre data inserted"}, 201
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.get("/borrows")
def get_borrows():
    u_type = login()[0]
    if u_type == "admin":
        result = [
            {
                "id": borrow.id,
                "title": borrow.book_title,
                "member": borrow.member_name,
                "status": borrow.status,
                "admins": {
                    "approved_by": borrow.approve_admin,
                    "returned_by": borrow.return_admin,
                },
                "date": {
                    "approved_at": borrow.approved_date,
                    "requested_at": borrow.requested_date,
                    "returned_at": borrow.returned_date,
                },
            }
            for borrow in Borrow.query.all()
        ]
        return {"result": result}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.post("/borrow/<bk_id>")
def request_borrow(bk_id):
    u_type, u_id = login()
    if u_type == "admin" or "member":
        book = Book.query.get(bk_id)
        user = User.query.get(u_id)

        nextval = db.session.execute(text("SELECT nextval('borrow_id_seq')")).scalar()
        brw_id = "brw" + str(nextval).zfill(3)

        new_borrow = Borrow(
            id=brw_id,
            book_id=bk_id,
            user_id=u_id,
            book_title=book.title,
            member_name=user.name,
            status="requested",
            requested_date=date.today(),
        )
        db.session.add(new_borrow)
        db.session.commit()

        return {"message": "Request successfully created"}, 201
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.put("/borrow/approve/<id>")
def approve_request(id):
    u_type, u_id = login()
    if u_type == "admin":
        admin = User.query.get(u_id)
        borrow = Borrow.query.get(id)

        borrow.status = "approved"
        borrow.approve_admin = admin.name
        borrow.approved_date = date(2023, 6, 16)
        db.session.commit()
        return {"message": "Request approved"}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


@app.put("/borrow/return/<id>")
def return_book(id):
    u_type, u_id = login()
    if u_type == "admin":
        admin = User.query.get(u_id)
        borrow = Borrow.query.get(id)

        borrow.status = "returned"
        borrow.return_admin = admin.name
        borrow.returned_date = date(2023, 6, 22)
        db.session.commit()
        return {"message": "Book returned"}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


if __name__ == "__main__":
    app.run(debug=True)
