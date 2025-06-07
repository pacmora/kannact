from pydantic import BaseModel


class BiometricsAnalytics(BaseModel):
    patient_id: int
    glucose_mean: int
    glucose_min: int
    glucose_max: int
    systolic_mean: int
    systolic_min: int
    systolic_max: int
    diastolic_mean: int
    diastolic_min: int
    diastolic_max: int
    weight_mean: int
    weight_min: int
    weight_max: int
