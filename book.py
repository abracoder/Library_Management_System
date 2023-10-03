from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime, timedelta

app = FastAPI()


class Book(BaseModel):
    isbn: str
    title: str
    author: str
    published_year: int
    quantity: int


class Borrowing(BaseModel):
    user: str
    book_isbn: str
    borrow_date: datetime
    return_date: datetime


# Database currently in dictionary foramat later i will use mongodb
books_db: Dict[str, Book] = {}

# List to track borrowed books (to be replaced with a real database)
borrowed_books: List[Borrowing] = []

# Function to create a new book
def create_book(book: Book):
    if book.isbn in books_db:
        raise HTTPException(status_code=400, detail="Book with the same ISBN already exists")
    books_db[book.isbn] = book
    return book

# Function to retrieve a book by ISBN
def get_book(isbn: str):
    if isbn not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[isbn]

# Function to update book details by ISBN
def update_book(isbn: str, updated_book: Book):
    if isbn not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    books_db[isbn] = updated_book
    return updated_book

# Function to delete a book by ISBN
def delete_book(isbn: str):
    if isbn not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    deleted_book = books_db.pop(isbn)
    return deleted_book



# Function to borrow a book
def borrow_book(username: str, book_isbn: str):
    # Check if the user has already borrowed 3 books
    user_borrow_count = sum(1 for borrow in borrowed_books if borrow.user == username)
    if user_borrow_count >= 3:
        raise HTTPException(status_code=400, detail="You cannot borrow more than 3 books")

    # Check if the book is available
    if book_isbn not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    if books_db[book_isbn].quantity <= 0:
        raise HTTPException(status_code=400, detail="The book is not available for borrowing")

    # Borrow the book
    borrow_date = datetime.utcnow()
    return_date = borrow_date + timedelta(days=14)  # Assume a 14-day borrowing period
    borrowed_books.append(Borrowing(user=username, book_isbn=book_isbn, borrow_date=borrow_date, return_date=return_date))

    # Decrement the book's quantity
    books_db[book_isbn].quantity -= 1

    return borrowed_books[-1]

# Function to return a book
def return_book(username: str, book_isbn: str):
    for i, borrow in enumerate(borrowed_books):
        if borrow.user == username and borrow.book_isbn == book_isbn:
            # Check if it's overdue
            if datetime.utcnow() > borrow.return_date:
                raise HTTPException(status_code=400, detail="The book is overdue")

            # Return the book
            returned_book = borrowed_books.pop(i)
            
            # Increment the book's quantity
            books_db[book_isbn].quantity += 1

            return returned_book
        
# Function to recommend books based on genres or authors
def recommend_books(username: str, by: str) -> List[Book]:
    user_borrow_history = [borrow.book_isbn for borrow in borrowed_books if borrow.user == username]
    recommended_books = []

    for book in books_db.values():
        if (
            book.isbn not in user_borrow_history
            and (
                (by == "genres" and any(genre in book.genres for genre in books_db[user]["genres"]))
                or (by == "authors" and book.author == books_db[user]["author"])
            )
        ):
            recommended_books.append(book)

    return recommended_books





