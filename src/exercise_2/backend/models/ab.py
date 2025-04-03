from pydantic import BaseModel


class Ad(BaseModel):
    title: str
    price: str
    address: str
    link: str

    def dict(self):
        return self.__dict__