from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def get_current_admin_user(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this resource",
        )
    return user

def role_required(role: str):
    def dependency(user: dict = Depends(get_current_user)):
        if user.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return dependency
