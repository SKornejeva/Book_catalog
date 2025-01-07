# Server (Flask) setup
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    copies = db.Column(db.Integer, nullable=False, default=1)

# Initialize database
def init_db():
    db.create_all()
    # Test data
    if not Book.query.first():
        test_books = [
            Book(title="Book 1", author="Author A", genre="Fiction", year=2020, description="Description 1", copies=3),
            Book(title="Book 2", author="Author B", genre="Non-fiction", year=2018, description="Description 2", copies=5),
            Book(title="Book 3", author="Author C", genre="Sci-fi", year=2021, description="Description 3", copies=2)
        ]
        db.session.add_all(test_books)
        db.session.commit()

# Routes
@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        data = request.json
        new_book = Book(
            title=data['title'],
            author=data['author'],
            genre=data['genre'],
            year=data['year'],
            description=data.get('description', ""),
            copies=data['copies']
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message": "Book added successfully!"}), 201

    books = Book.query.all()
    return jsonify([{
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "year": book.year,
        "description": book.description,
        "copies": book.copies
    } for book in books])

@app.route('/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
def book_details(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'GET':
        return jsonify({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "year": book.year,
            "description": book.description,
            "copies": book.copies
        })

    if request.method == 'PUT':
        data = request.json
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.genre = data.get('genre', book.genre)
        book.year = data.get('year', book.year)
        book.description = data.get('description', book.description)
        book.copies = data.get('copies', book.copies)
        db.session.commit()
        return jsonify({"message": "Book updated successfully!"})

    if request.method == 'DELETE':
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted successfully!"})

@app.route('/books/search', methods=['GET'])
def search_books():
    query_params = request.args
    filters = []

    if 'author' in query_params:
        filters.append(Book.author.ilike(f"%{query_params['author']}%"))
    if 'title' in query_params:
        filters.append(Book.title.ilike(f"%{query_params['title']}%"))
    if 'genre' in query_params:
        filters.append(Book.genre.ilike(f"%{query_params['genre']}%"))
    if 'year' in query_params:
        filters.append(Book.year == int(query_params['year']))

    results = Book.query.filter(*filters).all()
    return jsonify([{
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "year": book.year,
        "description": book.description,
        "copies": book.copies
    } for book in results])

@app.route('/books/stats', methods=['GET'])
def book_stats():
    total_books = Book.query.count()
    genres = db.session.query(Book.genre, db.func.count(Book.genre)).group_by(Book.genre).all()
    stats = {
        "total_books": total_books,
        "genre_distribution": {genre: count for genre, count in genres}
    }
    return jsonify(stats)

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)

# Client (Console)
import requests

def main_menu():
    print("Welcome to the Book Catalog Console Client")
    while True:
        print("\nOptions:")
        print("1. View all books")
        print("2. Add a new book")
        print("3. Update a book")
        print("4. Delete a book")
        print("5. Search books")
        print("6. View stats")
        print("0. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            view_books()
        elif choice == "2":
            add_book()
        elif choice == "3":
            update_book()
        elif choice == "4":
            delete_book()
        elif choice == "5":
            search_books()
        elif choice == "6":
            view_stats()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Define functions for each option here (e.g., view_books, add_book, etc.)
# These functions will send appropriate HTTP requests to the Flask server.

if __name__ == "__main__":
    main_menu()
