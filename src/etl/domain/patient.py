from typing import Literal

from pydantic import BaseModel, Field, EmailStr
from datetime import date

allowed_gender = ["male", "female", "non-binary", "genderfluid", "transsexual"]
allowed_sex = ["male", "female"]


class Patient(BaseModel):
    patient_id: int = None
    name: str = Field(min_length=2)
    date_of_birth: date
    gender: str = Literal[tuple(allowed_gender)]
    address: str = Field(min_length=5)
    email: EmailStr
    phone: str
    sex: str = Literal[tuple(allowed_sex)]
