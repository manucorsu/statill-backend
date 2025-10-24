from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
