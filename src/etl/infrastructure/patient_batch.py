from kink import di

from src.etl.application.dto import PatientDTO
from src.etl.application.patient_service import PatientService
from src.etl.domain.patient import Patient
from src.etl.domain.patient_repository import IPatientRepository

from pandas import DataFrame, read_json

from src.etl.infrastructure.postgresql_patient_repository import \
    PostgreSQLPatientRepository

patient_repo = PostgreSQLPatientRepository()
di[IPatientRepository] = patient_repo
di[PatientService] = PatientService(patient_repo=di[IPatientRepository])


def get_patient_batch(dp: DataFrame) -> list[Patient]:

    patient_batch: list[PatientDTO] = []
    for row in dp.to_dict(orient='records'):
        try:
            patient: PatientDTO = PatientDTO(**row)
            patient_batch.append(patient)
        except ValueError:
            """
            rows not parsed must be stored into 
            a table or file to be checked later
            """
            pass

    return patient_batch


class PatientBatch:
    def __init__(self):
        self._patient_service = di[PatientService]

    def process_patient_file(self):
        dp: DataFrame = read_json('./patient_data_sample_20.json',
                                  orient="records")

        patient_batch: list[PatientDTO] = get_patient_batch(dp)
        errors: list[PatientDTO] = self._patient_service.insert_patient(patient_dto_list=patient_batch)

        if len(errors):
            """
            patients validation fails must be stored into 
            a table or file to be checked later
            """
            pass
