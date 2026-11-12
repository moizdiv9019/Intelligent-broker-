from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from models import AuthRequest
from auth import get_current_user
from config import supabase

app = FastAPI(title="FastAPI")


@app.get("/")
def public_route():
    return {"message": "This is a public endpoint."}


@app.post("/signup")
def signup(payload: AuthRequest):
    """Helper route to register a test user in Supabase."""
    try:
        res = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
        })
        return {"message": "User created", "user_id": res.user.id if res.user else None}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/login")
def login(payload: AuthRequest):
    """Helper route to get a Bearer access_token for testing."""
    try:
        res = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })
        return {
            "access_token": res.session.access_token,
            "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.get("/protected/profile")
def read_protected_profile(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Protected endpoint: only accessible with a valid Supabase JWT."""
    return {
        "message": "Access granted!",
        "user": current_user,
    }
