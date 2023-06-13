from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
import itertools

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
    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"


# Book table
class Book(db.Model):
    __tablename__ = "book"
    id = db.Column(db.String, primary_key=True, nullable=False, unique=True, index=True)
    title = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=True)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)

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


# Routes
@app.get("/")
def welcome():
    return {"message": "Welcome to API Perpustakaan"}

if __name__ == "__main__":
    app.run(debug=True)
