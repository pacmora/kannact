from typing import Any, Optional

from pydantic import Field, BaseModel, model_validator
from datetime import datetime


class Biometrics(BaseModel):
    patient_id: int
    biometrics_id: Optional[int] = None
    test_date: datetime
    glucose: int = Field(None, gt=54, lt=300)  # mg/dl (outliers example)
    systolic: int = Field(None, gt=50,
                          lt=230)  # mm Hg (outliers example)
    diastolic: int = Field(None, gt=35,
                           lt=210)  # mm Hg (outliers example)
    weight: int = Field(None, gt=1000,
                        lt=400000)  # grams (outliers example)

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
