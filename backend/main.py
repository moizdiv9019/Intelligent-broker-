from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from models import AuthRequest , UpdateNameRequest
from auth import get_current_user
from config import supabase
from db import get_db
from models import User
from sqlalchemy.orm.session import Session
from sqlalchemy import update


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


@app.patch("/user")
def set_name(payload:UpdateNameRequest,current_user: Annotated[dict, Depends(get_current_user)],db:Annotated[Session,Depends(get_db)])->dict:
    user_id=current_user['id']
    stmt = (
        update(User)
        .where(User.uid == user_id)
        .values(displayname=payload.displayname.strip())
    )

    db.execute(stmt)
    db.commit()
    
    return {"message": "Display name updated", "displayname": payload.displayname.strip()}