
# from fastapi import FastAPI 
# app=FastAPI()

# @app.get("/home")
# def user():
#     return("well come all working")

# from db import session
# from sqlalchemy import cast
# from sqlalchemy.dialects.postgresql import UUID
# import models
# from sqlalchemy import text
from db import session ,engine
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel 
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker ,Session
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import  declarative_base
from sqlalchemy import Column,Integer,String,Float,ForeignKey



# 1. Force python-dotenv to find and load the .env file contents
load_dotenv()

# 2. Retrieve the variable securely from memory
data_base_url = os.getenv("local_db_url")

# 3. Add a safety check to print a clear message if it fails
if not data_base_url:
    raise ValueError("CRITICAL ERROR: DATBASE_URL was not found in your environment variables. Check your .env file syntax!")

# 4. Create the engine safely
engine = create_engine(data_base_url, poolclass=NullPool)
session=sessionmaker(engine)

def get_db():
   db=session()
   try: 
      yield db
   finally:
      db.close()



class pydantic_user(BaseModel):
    id:int
    name:str
    email:str
    money:float

class mul_user(BaseModel):
    users:list[pydantic_user]



class Product(BaseModel):
    id:int
    product_name:str
    price:float
    uid:int


base=declarative_base()

class User(base):
    __tablename__ = "user"
    
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(25))
    email=Column(String(30))
    money=Column(Float)

    # Products=Column()

class Products(base):
    __tablename__ = "products"

    id=Column(Integer,primary_key=True,index=True)
    product_name=Column(String(25))
    price=Column(Float)
    uid=Column(Integer,ForeignKey("user.id"))






# addusers(multiple_user)
# def get_users(db:Session=Depends(get_db())):
#    print(db)
# #    users=db.query(User).all
# #    if users:
# #       print(users)
# #    else:
# #       print("not found")
   
# get_users()
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] ,      # Allows requests from the URLs listed above (use ["*"] to allow all during testing)
    allow_credentials=True,      # Required if your frontend sends cookies or Authorization headers
    allow_methods=["*"],         # Allows all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],         # Allows all headers (Content-Type, Authorization, etc.)
)





@app.post("/Add_users")
def addusers(user:pydantic_user,db:Session=Depends(get_db)):
      user=user.model_dump()
      db.add(User(**user))
      db.commit()


@app.get("/users")
def get_users(db:Session=Depends(get_db)):
    u=db.query(User).all()
    return u


@app.get("/users{uid}")
def get_users(uid:int,db:Session=Depends(get_db)):
    u=db.query(User).filter(User.id==uid).first()
    if u:
        return u
    return "user not fuond"


@app.post("/product")
def add_product(product:Product,db:Session=Depends(get_db)):
    product=product.model_dump()
    user_exist=db.query(User.id).filter(User.id==product["uid"]).all()
    if user_exist:
     db.add(Products(**product))
     db.commit()
     return "insertion done"
    return "user not found"

@app.get("/product")
def get_products(uid:int,db:Session=Depends(get_db)):
    user_exsists=db.query(User).filter(User.id==uid).all()
    if user_exsists:
       products=db.query(Products).filter(Products.uid==uid).all()
       if products:
         return products
       return "no product listing"

    return "user not found"

@app.put("/users")
def update_user(user_data:pydantic_user,db:Session=Depends(get_db)):
    user_data=user_data.model_dump()
    user=db.query(User).filter(User.id==user_data['id']).first()
    if user:
        user.name=user_data['name']
        user.email=user_data['email']
        user.money=user_data['money']
        db.commit()
        updated_user=db.query(User).filter(User.id==user_data['id']).first()
        return updated_user
    else:
        return "user not found"



@app.delete("/product")
def delete_user(id:int,db:Session=Depends(get_db)):
    product=db.query(Products).filter(Products.id==id).first()
    if product:
        db.delete(product)
        db.commit()
        return "Product DELEETED"
    else:
        return "product not found"