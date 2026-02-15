from typing import  TypedDict
class UserDTO(TypedDict):
    name: str
    email: str


class LoginResponse(TypedDict):
    access_token: str
    refresh_token: str
    expires_in: int
    user: UserDTO
