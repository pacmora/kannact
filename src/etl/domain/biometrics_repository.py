from abc import ABC, abstractmethod
from datetime import datetime

from pandas import DataFrame

from src.etl.domain.biometrics import Biometrics
from src.etl.domain.biometrics_analytics import BiometricsAnalytics


class IBiometricsRepository(ABC):

    @abstractmethod
    def get_biometrics(self, patient_id: int, biometrics_id: int = 0,
                       test_date: datetime = datetime(1970, 1, 1),
                       limit: int = 10
                       ) -> list[Biometrics]:
        pass

    @abstractmethod
    def insert_biometrics(self,
                          biometrics_list: list[Biometrics]) -> Biometrics:
        pass

    @abstractmethod
    def get_dataframe_biometrics(self) -> DataFrame:
        pass

    @abstractmethod
    def update_biometrics(self,
                          biometrics_list: list[Biometrics]):
        pass

    @abstractmethod
    def upsert_biometrics(self,
                          biometrics_list: list[Biometrics]):
        pass

    @abstractmethod
    def delete_biometrics(self, biometrics_list: list[Biometrics]):
        pass

    @abstractmethod
    def get_biometrics_analytics(self, patient_id: int) -> BiometricsAnalytics:
        pass

    @abstractmethod
    def upsert_biometrics_analytics(self,
                                    biometrics_analytics_list: list[
                                        BiometricsAnalytics]
                                    ):
        pass
