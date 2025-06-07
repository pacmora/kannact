from src.etl.application.dto import PatientDTO
from src.etl.domain.patient import Patient
from src.etl.domain.patient_repository import IPatientRepository
from kink import inject


@inject
class PatientService:

    def __init__(self, patient_repo: IPatientRepository) -> None:
        self._patient_repo = patient_repo

    def get_patients(
            self, patient_id: int, limit: int = 10
    ) -> list[PatientDTO]:
        patients: list[Patient] = self._patient_repo.get_patients(
            patient_id=patient_id, limit=limit)
        patients_dto: list[PatientDTO] = []

        for patient in patients:
            patients_dto.append(PatientDTO(**patient.dict()))

        return patients_dto

    def insert_patient(
            self, patient_dto_list: list[PatientDTO]
    ) -> list[PatientDTO]:

        patient_batch: list[Patient] = []
        patient_error: list[PatientDTO] = []

        for p_dto in patient_dto_list:
            try:
                patient_batch.append(Patient(**p_dto.dict()))
            except ValueError:
                patient_error.append(p_dto)

        self._patient_repo.insert_patient(patients=patient_batch)

        return patient_error

    def is_patient(self, patient_id: int) -> bool:
        return self.get_patient(patient_id=patient_id) is not None

    def delete_patient(self, patient_id: int) -> Patient:
        return self._patient_repo.delete_patient(patient_id=patient_id)
