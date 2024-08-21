from pydantic import BaseModel

class Url(BaseModel):
    orginalUrl:str
    shortUrl:str

    class ConfigDict:
        from_attributes  = True