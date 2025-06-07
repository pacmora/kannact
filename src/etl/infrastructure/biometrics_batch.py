from kink import di

from src.etl.application.biometrics_service import BiometricsService
from src.etl.application.dto import BiometricsDTO
from src.etl.domain.biometrics_repository import IBiometricsRepository

from pandas import DataFrame, read_csv

from src.etl.infrastructure.postgresql_biometrics_repository import \
    PostgreSQLBiometricsRepository

biometrics_repo = PostgreSQLBiometricsRepository()
di[IBiometricsRepository] = biometrics_repo
di[BiometricsService] = BiometricsService(
    biometrics_repo=di[IBiometricsRepository]
)


def get_biometrics_batch(dp: DataFrame) -> list[BiometricsDTO]:

    biometrics_batch: list[BiometricsDTO] = []
    for row in dp.to_dict(orient='records'):
        try:
            biometrics: BiometricsDTO = BiometricsDTO(**row)
            biometrics_batch.append(biometrics)
        except ValueError:
            """
            rows not parsed must be stored into 
            a table or file to be checked later
            """
            pass

    return biometrics_batch


class BiometricsBatch:
    def __init__(self):
        self._biometrics_service = di[BiometricsService]

    def process_patient_file(self):
        dp: DataFrame = read_csv('./biometrics_data_sample.csv')
        biometrics_batch: list[BiometricsDTO] = get_biometrics_batch(dp)
        biometrics_error: list[BiometricsDTO] = self._biometrics_service.insert_biometrics(
            weight_unit='metric', biometrics_dto_list=biometrics_batch
        )
        if len(biometrics_error):
            """
            biometrics validation fails must be stored into 
            a table or file to be checked later
            """
            pass


