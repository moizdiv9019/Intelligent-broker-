from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status,File,UploadFile as FastAPIUploadFile
from models import AuthRequest , UpdateNameRequest,InventoryMedia
from auth import get_current_user
from config import supabase
from db import get_db
from models import User ,InventoryCreate,Inventory
from sqlalchemy.orm.session import Session
from sqlalchemy import update
import uuid
import os
from dotenv import load_dotenv
from pydantic import WithJsonSchema

app = FastAPI(title="FastAPI")


# Wrap UploadFile so Swagger UI renders a "Choose File" button
BinaryUploadFile = Annotated[
    FastAPIUploadFile, WithJsonSchema({"type": "string", "format": "binary"})
]


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
    " endpoint to set user name on the system"
    user_id=current_user['id']
    stmt = (
        update(User)
        .where(User.uid == user_id)
        .values(displayname=payload.displayname.strip())
    )
    db.execute(stmt)
    db.commit()
    
    return {"message": "Display name updated", "displayname": payload.displayname.strip()}


@app.post("/inventory")
def upload_inventory(payload:InventoryCreate,current_user: Annotated[dict, Depends(get_current_user)],db:Annotated[Session,Depends(get_db)]):
    "endpoin to upload new inventory listing data"
    raw_id = current_user["id"]
    broker_uuid = raw_id if isinstance(raw_id, uuid.UUID) else uuid.UUID(raw_id)
    inventory_data=Inventory(**payload.model_dump(),broker_id=broker_uuid)
    db.add(inventory_data)
    db.commit()
    db.refresh(inventory_data)
    return inventory_data

load_dotenv()
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET_NAME")
if not SUPABASE_BUCKET:
  raise RuntimeError("SUPABASE_BUCKET_NAME is not set in .env")

@app.post("/inventory/{inventory_id}/media")
async def upload_inventory_media(
    inventory_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    files: list[BinaryUploadFile] = File(...),
):
  inventory = (
      db.query(Inventory).filter(Inventory.inventory_id == inventory_id).first()
  )
  if not inventory:
    raise HTTPException(status_code=404, detail="Inventory not found")

  raw_id = current_user["id"]
  broker_uuid = raw_id if isinstance(raw_id, uuid.UUID) else uuid.UUID(raw_id)
  if inventory.broker_id != broker_uuid:
    raise HTTPException(
        status_code=403, detail="Not authorized to modify this inventory"
    )

  saved_media = []
  uploaded_paths = []

  try:
    for file in files:
      if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail=f"{file.filename} is not an image"
        )

      file_bytes = await file.read()
      file_ext = (
          file.filename.rsplit(".", 1)[-1]
          if "." in (file.filename or "")
          else "jpg"
      )
      file_path = f"inventory/{inventory_id}/{uuid.uuid4()}.{file_ext}"

      supabase.storage.from_("inventory images").upload(
          path=file_path,
          file=file_bytes,
          file_options={"content-type": file.content_type},
      )
      uploaded_paths.append(file_path)

      public_url = supabase.storage.from_("inventory images").get_public_url(
          file_path
      )

      media_record = InventoryMedia(
          inventory_id=inventory_id, media_url=public_url
      )
      db.add(media_record)
      saved_media.append(media_record)

    db.commit()
    for item in saved_media:
      db.refresh(item)

    return saved_media

  except HTTPException:
    db.rollback()
    if uploaded_paths:
      supabase.storage.from_("inventory images").remove(uploaded_paths)
    raise
  except Exception as e:
    db.rollback()
    if uploaded_paths:
      supabase.storage.from_("inventory images").remove(uploaded_paths)
    raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


