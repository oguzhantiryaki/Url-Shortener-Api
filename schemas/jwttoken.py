from pydantic import BaseModel

class JWTtoken(BaseModel):
    access_token:str
    token_type:str

