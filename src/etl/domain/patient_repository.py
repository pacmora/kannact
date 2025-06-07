from abc import ABC, abstractmethod

from src.etl.domain.patient import Patient


class IPatientRepository(ABC):

    @abstractmethod
    def get_patients(self, patient_id: int, limit: int = 10) -> list[Patient]:
        pass

    @abstractmethod
    def insert_patient(self, patients: list[Patient]):
        pass
