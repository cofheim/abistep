from pydantic import BaseModel, EmailStr


class SUserBase(BaseModel):
    name: str
    email: EmailStr
    balance: float


class SUserCreate(SUserBase):
    pass


class SUser(SUserBase):
    id: int


class STransfer(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: float
