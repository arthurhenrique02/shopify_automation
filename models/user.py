import typing

from pydantic import BaseModel


class TrelloUserData(BaseModel):
    name: str
    email: str
    password: str | None
    country: typing.Literal["es", "it"] | None
    phone: str
    store_name: str | None
    colors: typing.List[str] | None
