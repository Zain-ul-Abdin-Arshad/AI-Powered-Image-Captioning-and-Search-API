from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION", "3600")) // 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin123"),
        "disabled": False,
    },
    "user": {
        "username": "user",
        "full_name": "Regular User",
        "email": "user@example.com",
        "hashed_password": pwd_context.hash("user123"),
        "disabled": False,
    }
}

class User:
    def __init__(self, username: str, full_name: str, email: str, disabled: bool = False):
        self.username = username
        self.full_name = full_name
        self.email = email
        self.disabled = disabled

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[User]:
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return User(
            username=user_dict["username"],
            full_name=user_dict["full_name"],
            email=user_dict["email"],
            disabled=user_dict["disabled"]
        )
    return None

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, fake_users_db[username]["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        token = credentials.credentials
        username = verify_token(token)
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = get_user(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        ) 