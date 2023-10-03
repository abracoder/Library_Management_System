from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timedelta
import jwt

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

