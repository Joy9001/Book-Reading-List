from flask import Flask, render_template, request, redirect, url_for
# import sqlite3
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

# Using SQLite
# db = sqlite3.connect("Books-Collection.db", check_same_thread=False)
# cursor = db.cursor()

# try:
#     cursor.execute(
#         "CREATE TABLE books (id INTEGER PRIMARY KEY AUTOINCREMENT, title varchar(250) NOT NULL UNIQUE, author varchar(250) NOT NULL, rating FLOAT NOT NULL)")
# except sqlite3.OperationalError as e:
#     print(e)

app = Flask(__name__)

# create a database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
db = SQLAlchemy()
db.init_app(app)


# Define model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)


# create table
with app.app_context():
    db.create_all()


def list_all_books():
    all_books_data = Book.query.all()

    all_books = []

    for bk in all_books_data:
        new_book = {
            "ID": bk.id,
            "Title": bk.title,
            "Author": bk.author,
            "Rating": bk.rating
        }
        all_books.append(new_book)
    return all_books


@app.route('/')
def home():
    # with app.app_context():
    #     all_books_data = db.session.execute(db.select(Book).order_by(Book.title)).scalars().all()

    all_books = list_all_books()

    return render_template("index.html", books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        b_id = request.form.get("id")
        title = request.form.get("title")
        author = request.form.get("author")
        rating = request.form.get("rating")

        try:
            new_book_entry = Book(id=b_id, title=title, author=author, rating=rating)
            db.session.add(new_book_entry)
            db.session.commit()
            return redirect(url_for('home'))
        except sqlalchemy.exc.IntegrityError as e:
            print(e)

        # new_book = {
        #     "Title": request.form.get("title"),
        #     "Author": request.form.get("author"),
        #     "Rating": request.form.get("rating")
        # }

        # try:
        #     cursor.execute('INSERT INTO books (title, author, rating) VALUES(?,?,?)',
        #                    (request.form.get("title"), request.form.get("author"), request.form.get("rating")))
        #     db.commit()
        #     all_books.append(new_book)
        #     print(all_books)
        #     return redirect(url_for('home'))
        # except sqlite3.IntegrityError as ex:
        #     print(ex)

    return render_template("add.html")


@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_rating(book_id):
    all_books = list_all_books()

    if request.method == "POST":
        new_rating = request.form.get("new_rating")
        with app.app_context():
            update_book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
            if update_book:
                update_book.rating = new_rating
                db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", bk_id=book_id, books=all_books)


@app.route("/delete")
def delete_book():
    b_id = request.args.get("book_id")
    with app.app_context():
        deleted_book = db.session.query(Book).filter_by(id=b_id).first()
        # deleted_book = db.get_or_404(Book, b_id)
        if deleted_book:
            db.session.delete(deleted_book)
            db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
