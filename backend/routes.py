# from fastapi import FastAPI

# app=FastAPI()

# @app.patch("/user{uid}")
# def set_name(uid):
#     pass

# @app.get("/user/dashboard{uid}")
# def user_dashboard(uid):
#     pass


# @app.get("/inventory{uid}")
# def all_inventory(uid):
#     pass

# @app.get("/inventory{uid}{inventory_id}")
# def specific_inventory(uid,inventory_id):
#     pass


# @app.put("/inventory{uid}{inventory_id}")
# def update_inventory(uid,inventory_id):
#     pass

# @app.delete("/inventory{uid}{inventory_id}")
# def delete_inventoy(uid,inventory_id):
#     pass


# @app.post("/inventory{uid}{inventory_id}/media")
# def attact_media(uid,inventory_id):
#     pass


# @app.delete("/inventory{uid}{inventory_id}/media")
# def attact_media(uid,inventory_id):
#     pass

# #adds an new customer
# @app.post("/customer{uid}")
# def add_customer(uid,data):
#     pass


# #return all customer's data
# @app.get("/customer{uid}")
# def add_customer(uid):
#     pass


# #deletes existing customer
# @app.delete("/customer{uid}")
# def add_customer(uid,data):
#     pass

# @app.get("/quries{uid}")
# def get_quries(uid):
#     pass

# @app.post("/quries{uid}")
# def add_qurey(uid):
#     pass

from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from auth import get_current_user
from config import supabase

app = FastAPI(title="FastAPI + Supabase Auth")


class AuthRequest(BaseModel):
    email: str
    password: str


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
