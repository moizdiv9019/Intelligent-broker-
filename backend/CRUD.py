from db import session
import models



def set_username(**data:models.UserSetName):
     db=session()
     try:
         data=models.UserSetName(**data)
         data=models.User(**data.model_dump())
         
         user = db.query(models.User).filter(
        models.User.uid == data.uid,
         ).first()
         if not user:
            print("User not found.")
            return False
            
         print("no")

     except Exception as e:
       print(e)



l={"uid":"1","displayname":"ismail"}


set_username(**l)
     