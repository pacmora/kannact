from typing import Literal, Any, Optional

from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import date, datetime

allowed_gender = ["male", "female", "non-binary", "genderfluid", "transsexual"]
allowed_sex = ["male", "female"]


class PatientDTO(BaseModel):
    patient_id: int
    name: str = Field(min_length=2)
    date_of_birth: date
    gender: str = Literal[tuple(allowed_gender)]
    address: str = Field(min_length=5)
    email: EmailStr
    phone: str
    sex: str = Literal[tuple(allowed_sex)]


class PatientPaginationDTO(BaseModel):
    patients: list[PatientDTO] = []
    next_page_token: str


class BiometricsDTO(BaseModel):
    patient_id: int
    biometrics_id: Optional[int] = None
    test_date: datetime
    glucose: int = Field(None, gt=54, lt=300)  # mg/dl (outliers example)
    systolic: int = Field(None, gt=50,
                          lt=230)  # mm Hg (outliers example)
    diastolic: int = Field(None, gt=35,
                           lt=210)  # mm Hg (outliers example)
    weight: float = None

    @model_validator(mode="before")
    @classmethod
    def check_consistency(cls, data: Any) -> Any:
        """
        This method is an example of inconsistencies.
        """
        if isinstance(data, dict):
            systolic_missing = False
            diastolic_missing = False
            try:
                systolic = data["systolic"]
            except KeyError:
                systolic_missing = True

            try:
                diastolic = data["diastolic"]
            except KeyError:
                diastolic_missing = True

            if systolic_missing != diastolic_missing:
                missing = "diastolic" if systolic_missing else "systolic"
                provided = "systolic" if diastolic_missing else "diastolic"
                raise ValueError(
                   f"{provided} was provided but {missing}"
                )
            if systolic_missing and diastolic_missing:
                return data

            elif diastolic > systolic:
                raise ValueError(
                    "Blood pressure values inconsistency. (diastolic is greater than systolic)"
                )
            else:
                return data


class BiometricsPaginationDTO(BaseModel):
    biometrics_history: list[BiometricsDTO] = []
    next_page_token: str


class BiometricsAnalyticsDTO(BaseModel):
    patient_id: int
    glucose_mean: float
    glucose_min: float
    glucose_max: float
    systolic_mean: float
    systolic_min: float
    systolic_max: float
    diastolic_mean: float
    diastolic_min: float
    diastolic_max: float
    weight_mean: float
    weight_min: float
    weight_max: float





