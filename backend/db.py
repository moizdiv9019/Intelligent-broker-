import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

#loading the data url 
load_dotenv()
data_base_url=os.getenv("DATABASE_URL")

#creating an engine to connect database
engine=create_engine(data_base_url,poolclass=NullPool)

#creating an session
session =sessionmaker(autoflush=False,bind=engine)






