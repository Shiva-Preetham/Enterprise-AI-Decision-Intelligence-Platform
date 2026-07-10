from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    role: str

SIMULATED_USERS = {
    "admin": {"password": "admin", "role": "admin"},
    "manager": {"password": "manager", "role": "manager"},
    "analyst": {"password": "analyst", "role": "analyst"},
    "viewer": {"password": "viewer", "role": "viewer"},
}

@router.post("/login", response_model=AuthToken)
async def login(request: LoginRequest):
    user = SIMULATED_USERS.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    import base64
    import json
    import time
    
    fake_payload = {"sub": request.username, "role": user["role"], "exp": int(time.time()) + 86400}
    fake_token = base64.b64encode(json.dumps(fake_payload).encode()).decode()
    
    return AuthToken(
        access_token=fake_token,
        token_type="bearer",
        role=user["role"]
    )
