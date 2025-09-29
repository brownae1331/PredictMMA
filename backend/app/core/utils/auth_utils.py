from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
import hashlib
import secrets

SECRET_KEY = "6821AF91D3A176D8E8E6E5C344327"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    # Use SHA-256 with salt for now as bcrypt is having issues on Railway
    try:
        salt, stored_hash = hashed_password.split('$')
        test_hash = hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
        return test_hash == stored_hash
    except (ValueError, AttributeError):
        return False

def get_password_hash(password):
    # Use SHA-256 with salt for now as bcrypt is having issues on Railway
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}${password_hash}"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None