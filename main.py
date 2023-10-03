from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict ,List
from datetime import datetime, timedelta
import jwt
from book import Book, Borrowing, borrow_book, create_book, delete_book, get_book, recommend_books, return_book, update_book

app = FastAPI()

# Secret key for JWT 
SECRET_KEY = "my-secret-key"

# User database (currently using dictionary as database)
users_db: Dict[str, Dict[str, str]] = {}

# User model for registration
class UserRegistration(BaseModel):
    username: str
    password: str

# User model for authentication
class UserAuth(BaseModel):
    username: str
    password: str

# Token model for JWT
class Token(BaseModel):
    access_token: str
    token_type: str

# Function to create a new user
def create_user(user: UserRegistration):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    users_db[user.username] = {"username": user.username, "password": user.password}

# User registration endpoint
@app.post("/users", response_model=Token)
def register_user(user: UserRegistration):
    create_user(user)
    print(users_db)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Function to create JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


# Function to authenticate a user
def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if user and user["password"] == password:
        return user

# Login endpoint
@app.post("/login", response_model=Token)
def login_user(user_auth: UserAuth):
    user = authenticate_user(user_auth.username, user_auth.password)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    access_token = create_access_token(data={"sub": user_auth.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint to create a new book (POST /books)
@app.post("/books/", response_model=Book)
def create_new_book(book: Book):
    return create_book(book)


# Endpoint to retrieve a book by ISBN (GET /books/{isbn})
@app.get("/books/{isbn}", response_model=Book)
def get_book_by_isbn(isbn: str):
    return get_book(isbn)

# Endpoint to update book details by ISBN (PUT /books/{isbn})
@app.put("/books/{isbn}", response_model=Book)
def update_book_by_isbn(isbn: str, updated_book: Book):
    return update_book(isbn, updated_book)

# Endpoint to delete a book by ISBN (DELETE /books/{isbn})
@app.delete("/books/{isbn}", response_model=Book)
def delete_book_by_isbn(isbn: str):
    return delete_book(isbn)


# Endpoint to borrow a book (POST /borrow)
@app.post("/borrow/", response_model=Borrowing)
def borrow_a_book(username: str, book_isbn: str):
    return borrow_book(username, book_isbn)

# Endpoint to return a book (POST /return)
@app.post("/return/", response_model=Borrowing)
def return_a_book(username: str, book_isbn: str):
    return return_book(username, book_isbn)


# Endpoint to search for books by title, author, or ISBN (GET /search)
@app.get("/search/", response_model=List[Book])
def search_books(
    title: str = None,
    author: str = None,
    isbn: str = None,
):
    results = []

    for book in books_db.values():
        if (
            (title is None or title.lower() in book.title.lower())
            and (author is None or author.lower() in book.author.lower())
            and (isbn is None or isbn == book.isbn)
        ):
            results.append(book)

    if not results:
        raise HTTPException(status_code=404, detail="No matching books found")

    return results


# Endpoint to get book recommendations for a user based on genres or authors (GET /recommendations/{username})
@app.get("/recommendations/{username}", response_model=List[Book])
def get_recommendations(username: str, by: str = "genres"):
    recommended_books = recommend_books(username, by)
    return recommended_books

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

