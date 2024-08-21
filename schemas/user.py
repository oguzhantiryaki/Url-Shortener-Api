from pydantic import BaseModel

class User(BaseModel):
    username:str
    password:str
    email:str

    class ConfigDict :
        from_attributes  = True
    