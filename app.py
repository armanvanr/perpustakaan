from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text, or_
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
    is_show = db.Column(db.Boolean, nullable=True)
    book_list = db.relationship(
        "Borrow", backref="reader", lazy="select", cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.name}>"


# Book-Author table
book_author_table = db.Table(
    "book_author_table",
    db.Model.metadata,
    db.Column("book_id", db.String, db.ForeignKey("book.id"), primary_key=True),
    db.Column("author_id", db.String, db.ForeignKey("author.id"), primary_key=True),
)

# Book-Genre table
book_genre_table = db.Table(
    "book_genre_table",
    db.Model.metadata,
    db.Column("book_id", db.String, db.ForeignKey("book.id"), primary_key=True),
    db.Column("genre_id", db.String, db.ForeignKey("genre.id"), primary_key=True),
)


# Book table
class Book(db.Model):
    __tablename__ = "book"

    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    title = db.Column(db.String, nullable=False, unique=True)
    pages = db.Column(db.SmallInteger, nullable=False, default=1)
    publisher = db.Column(db.String, nullable=True)
    published_year = db.Column(db.SmallInteger, nullable=True, default=1000)
    is_show = db.Column(db.Boolean, nullable=True)
    authors = db.relationship(
        "Author",
        secondary=book_author_table,
        back_populates="books",
        cascade="all, delete",
    )
    genres = db.relationship(
        "Genre",
        secondary=book_genre_table,
        back_populates="books",
        cascade="all, delete",
    )
    reader_list = db.relationship(
        "Borrow", backref="borrowed_book", lazy="select", cascade="all, delete"
    )

    def __repr__(self):
        return f"<Book {self.title}>"


# Author table
class Author(db.Model):
    __tablename__ = "author"

    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False, unique=True)
    birth_year = db.Column(db.SmallInteger, nullable=True, default=1000)
    is_show = db.Column(db.Boolean, nullable=True)
    books = db.relationship(
        "Book",
        secondary=book_author_table,
        back_populates="authors",
        cascade="all, delete",
    )

    def __repr__(self):
        return f"<Author {self.name}>"


# Genre table
class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False)
    is_show = db.Column(db.Boolean, nullable=True)
    books = db.relationship(
        "Book",
        secondary=book_genre_table,
        back_populates="genres",
        cascade="all, delete",
    )

    def __repr__(self):
        return f"<Genre {self.name}>"


# Borrow transaction table
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
    is_show = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f"<Borrow status: {self.status}>"


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
            if user.is_show == True
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
        result = {
            "name": user.name,
            "type": user.type,
            "email": user.email,
            "password": user.password,
            "reading_list": [
                item.borrowed_book.title
                for item in user.book_list
                if item.status == "approved"
            ],
        }
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
        is_show=True,
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
                is_show=True,
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
            user.is_show = False
            db.session.commit()
            return {"message": "User data deleted"}
        return {"message": "Unauthorized"}, 401
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# Books
# show all books
@app.get("/books")
def get_books():
    result = [
        {"title": book.title, "id": book.id}
        for book in Book.query.all()
        if book.is_show == True
    ]
    return {"books": result}


# show a book details
@app.get("/book/<id>")
def book_details(id):
    book = Book.query.get(id)
    details = {
        "title": book.title,
        "num_of_page": book.pages,
        "published_year": book.published_year,
        "publisher": book.publisher,
        "genre": [item.genre.name for item in book.genre_list.all()],
        "genres": [genre.name for genre in book.genres],
        "author": [
            item.writer.name for item in book.author_list.all()
        ],  # from db.Model
        "authors": [author.name for author in book.authors],  # from db.Table
    }
    return {"book": details}


# add a book
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

        # create a new book instance
        new_book = Book(
            id=b_id,
            title=data.get("title", None),
            pages=data.get("pages", None),
            publisher=data.get("publisher", None),
            published_year=data.get("published_year", None),
            is_show=True,
        )

        # adding authors
        if "authors" in data.keys() and data["authors"]:
            # list of author names in format: [Author.name=val1, Author.name=val2, Author.name=val3]
            author_names = [getattr(Author, "name") == au for au in data["authors"]]

            # find existing author objects by filtering the name using "OR" operator
            author_objects = Author.query.filter(or_(*author_names)).all()

            # append any existing author into the list
            if author_objects:
                # append each author object into "authors" column
                for a_obj in author_objects:
                    new_book.authors.append(a_obj)
                    # remove found author from query params list
                    data["authors"].remove(a_obj.name)

            # by default, this will add any new author (which is not found in database)
            for a_name in data["authors"]:
                nextval = db.session.execute(
                    text("SELECT nextval('author_id_seq')")
                ).scalar()
                a_id = "au" + str(nextval).zfill(3)
                new_author = Author(id=a_id, name=a_name, is_show=True)
                new_book.authors.append(new_author)
                db.session.add(new_author)

        # adding genres
        if "genres" in data.keys() and data["genres"]:
            # list of genre names in format: [Genre.name=val1, Genre.name=val2, Genre.name=val3]
            genres_names = [getattr(Genre, "name") == ge for ge in data["genres"]]

            # find existing genre objects by filtering the name using "OR" operator
            genre_objects = Genre.query.filter(or_(*genres_names)).all()

            # append any existing genre into the list
            if genre_objects:
                # append each genre object into "genre" column
                for g_obj in genre_objects:
                    new_book.genres.append(g_obj)
                    # remove found genre from query params list
                    data["genres"].remove(g_obj.name)

                # by default, this will add any new genre (which is not found in database)
            for g_name in data["genres"]:
                nextval = db.session.execute(
                    text("SELECT nextval('genre_id_seq')")
                ).scalar()
                g_id = "au" + str(nextval).zfill(3)
                new_genre = Genre(id=g_id, name=g_name, is_show=True)
                new_book.genres.append(new_genre)
                db.session.add(new_genre)
        db.session.add(new_book)
        db.session.commit()
        return {"message": "Book added"}, 201
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# update a book details
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


# delete a book
@app.delete("/book/<id>")
def delete_book(id):
    u_type = login()[0]
    if u_type == "admin":
        book = Book.query.get(id)
        book.is_show = False
        db.session.commit()
        return {"message": "Book deleted"}
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# Genres
# show all genres
@app.get("/genres")
def get_genres():
    result = [
        {"genre": genre.name, "id": genre.id}
        for genre in Genre.query.all()
        if genre.is_show == True
    ]
    return {"Genres": result}


# show a genre and book lists
@app.get("/genre/<id>")
def genre_details(id):
    genre = Genre.query.get(id)
    result = {
        "genre": genre.name,
        "book_list": [item.book.title for item in genre.book_list.all()],
        "books": [book.title for book in genre.books],
    }
    return result


# add a genre
@app.post("/genre")
def add_genre():
    u_type = login()[0]
    if u_type == "admin":
        data = request.get_json()
        genre = Genre.query.filter_by(name=data["name"]).first()
        if genre:
            return {"message": "A genre already exists"}, 400

        nextval = db.session.execute(text("SELECT nextval('genre_id_seq')")).scalar()
        g_id = "ge" + str(nextval).zfill(3)

        new_genre = Genre(id=g_id, name=data["name"], is_show=True)
        db.session.add(new_genre)
        db.session.commit()
        return {"message": "Genre added"}, 201
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# update a genre name
@app.put("/genre/<id>")
def update_genre(id):
    u_type = login()[0]
    if u_type == "admin":
        data = request.get_json()
        genre = Genre.query.get(id)
        genre.name = data.get("name", genre.name)
        db.session.commit()
        return {"message": "Genre updated"}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# delete a genre
@app.delete("/genre/<id>")
def delete_genre(id):
    u_type = login()[0]
    if u_type == "admin":
        genre = Genre.query.get(id)
        genre.is_show = False
        db.session.commit()
        return {"message": "Genre deleted"}
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# Authors
# show all authors
@app.get("/authors")
def get_authors():
    result = [
        {"name": author.name, "id": author.id}
        for author in Author.query.all()
        if author.is_show == True
    ]
    return {"Authors": result}


# show an author details
@app.get("/author/<id>")
def author_details(id):
    author = Author.query.get(id)
    details = {
        "name": author.name,
        "birth_year": author.birth_year,
        "book_list": [item.written_book.title for item in author.book_list.all()],
        "books": [book.title for book in author.books],
    }
    return {"author details": details}


# add an author
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
            id=a_id,
            name=data["name"],
            birth_year=data.get("birth_year", 1000, is_show=True),
        )
        db.session.add(new_author)
        db.session.commit()
        return {"message": "Author added"}, 201
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# update an author details
@app.put("/author/<id>")
def update_author(id):
    u_type = login()[0]
    if u_type == "admin":
        data = request.get_json()
        author = Author.query.get(id)
        author.name = data.get("name", author.name)
        author.birth_year = data.get("birth_year", author.birth_year)
        db.session.commit()
        return {"message": "Author updated"}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# delete an author
@app.delete("/author/<id>")
def delete_author(id):
    u_type = login()[0]
    if u_type == "admin":
        author = Author.query.get(id)
        author.is_show = False
        db.session.commit()
        return {"message": "Author deleted"}
    elif login() == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# Borrows
# show all borrow records
@app.get("/borrows")
def get_borrows():
    u_type = login()[0]
    if u_type == "admin":
        results = [
            {
                "id": borrow.id,
                "title": borrow.book_title,
                "member": borrow.member_name,
                "status": borrow.status,
            }
            for borrow in Borrow.query.all()
            if borrow.is_show == True
        ]
        return {"results": results}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# show details of borrow
@app.get("/borrow/<id>")
def get_borrow(id):
    u_type = login()[0]
    if u_type == "admin":
        borrow = Borrow.query.get(id)
        details = {
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
        # change the date format (15 Jun 2023) only for non-empty dates
        if details["date"]["approved_at"] != None:
            details["date"]["approved_at"] = borrow.approved_date.strftime("%d %b %Y")
        if details["date"]["requested_at"] != None:
            details["date"]["requested_at"] = borrow.requested_date.strftime("%d %b %Y")
        if details["date"]["returned_at"] != None:
            details["date"]["returned_at"] = borrow.returned_date.strftime("%d %b %Y")
        return {"details": details}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# create a borrow request
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
            is_show=True,
        )
        db.session.add(new_borrow)
        db.session.commit()

        return {"message": "Request successfully created"}, 201
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# approve a borrow request
@app.put("/borrow/approve/<id>")
def approve_request(id):
    u_type, u_id = login()
    if u_type == "admin":
        admin = User.query.get(u_id)
        borrow = Borrow.query.get(id)

        borrow.status = "approved"
        borrow.approve_admin = admin.name
        borrow.approved_date = date.today()
        db.session.commit()
        return {"message": "Request approved"}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# record a book return
@app.put("/borrow/return/<id>")
def return_book(id):
    u_type, u_id = login()
    if u_type == "admin":
        admin = User.query.get(u_id)
        borrow = Borrow.query.get(id)

        borrow.status = "returned"
        borrow.return_admin = admin.name
        borrow.returned_date = date.today()
        db.session.commit()
        return {"message": "Book returned"}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# delete a borrow record
@app.delete("/borrow/<id>")
def delete_borrow(id):
    u_type = login()[0]
    if u_type == "admin":
        borrow = Borrow.query.get(id)
        borrow.is_show = False
        db.session.commit()
        return {"message": "Record deleted"}
    elif u_type == "Wrong pwd":
        return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Unauthorized"}, 401


# Filter in book search
@app.get("/booksearch")
def search_books():
    args = request.args
    # Model1.query.join(Model2, Model1.rel_Model2).join(Model3, Model1.rel_Model3)
    q = Book.query.join(Author, Book.authors).join(Genre, Book.genres)

    # Query params 'key' Handler
    # search if book detail matches with keyword (any part of string)
    if "title" in args.keys():
        q = q.filter(Book.title.ilike(f"%{args['title']}%"))
    if "author" in args.keys():
        q = q.filter(Author.name.ilike(f"%{args['author']}%"))
    if "publisher" in args.keys():
        q = q.filter(Book.publisher.ilike(f"%{args['publisher']}%"))

    # search if book detail exactly matches keyword
    if "published_year" in args.keys():
        q = q.filter(Book.published_year == args["published_year"])
    if "genre" in args.keys():
        q = q.filter(Genre.name == args["genre"])

    books = q.all()
    result = [
        {
            "book_id": book.id,
            "title": book.title,
            "publisher": book.publisher,
            "authors": [author.name for author in book.authors],
            "published_year": book.published_year,
            "genres": [genre.name for genre in book.genres],
        }
        for book in books
    ]
    return {"result": result}


if __name__ == "__main__":
    app.run(debug=True)
