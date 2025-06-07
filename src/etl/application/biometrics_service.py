from datetime import datetime

from kink import inject

from src.building_blokcs.unit_conversor import pounds_to_grams, \
    kilograms_to_grams, grams_to_pounds, grams_to_kilograms
from src.etl.application.dto import BiometricsDTO, BiometricsAnalyticsDTO
from src.etl.domain.biometrics_analytics import BiometricsAnalytics
from src.etl.domain.biometrics_repository import IBiometricsRepository
from src.etl.domain.biometrics import Biometrics


@inject
class BiometricsService:

    def __init__(self, biometrics_repo: IBiometricsRepository):
        self._biometrics_repo = biometrics_repo

    def get_biometrics(self, patient_id, weight_unit: str,
                       biometrics_id: int = 0,
                       test_date: datetime = datetime(1970, 1, 1),
                       limit: int = 10
                       ) -> list[BiometricsDTO]:

        biometrics_list: list[
            Biometrics] = self._biometrics_repo.get_biometrics(
            patient_id=patient_id,
            biometrics_id=biometrics_id,
            test_date=test_date,
            limit=limit)

        biometrics_dto_list: list[BiometricsDTO] = []
        for biometrics in biometrics_list:
            if weight_unit != 'metric':
                weight = grams_to_pounds(biometrics.weight)
            else:
                weight = grams_to_kilograms(biometrics.weight)

            biometrics_dto: BiometricsDTO = BiometricsDTO(
                patient_id=biometrics.patient_id,
                biometrics_id=biometrics.biometrics_id,
                test_date=biometrics.test_date,
                glucose=biometrics.glucose,
                systolic=biometrics.systolic,
                diastolic=biometrics.diastolic,
                weight=weight
            )

            biometrics_dto_list.append(biometrics_dto)

        return biometrics_dto_list

    def insert_biometrics(
            self, weight_unit: str, biometrics_dto_list: list[BiometricsDTO]
    ) -> list[BiometricsDTO]:
        biometrics_list, biometrics_error = (
            self._map_biometrics_dto_to_biometrics(
                weight_unit=weight_unit, biometrics_dto_list=biometrics_dto_list
            )
        )

        self._biometrics_repo.insert_biometrics(biometrics_list=biometrics_list)

        return biometrics_error

    def update_biometrics(
            self, weight_unit: str, biometrics_dto_list: list[BiometricsDTO]
    ) -> BiometricsDTO:

        biometrics_list, biometrics_error = (
            self._map_biometrics_dto_to_biometrics(
                weight_unit=weight_unit, biometrics_dto_list=biometrics_dto_list
            )
        )
        self._biometrics_repo.update_biometrics(biometrics_list=biometrics_list)

    def upsert_biometrics(
            self, weight_unit: str, biometrics_dto_list: list[BiometricsDTO]
    ):
        biometrics_list, biometrics_error = (
            self._map_biometrics_dto_to_biometrics(
                weight_unit=weight_unit, biometrics_dto_list=biometrics_dto_list
            )
        )

        self._biometrics_repo.upsert_biometrics(biometrics_list=biometrics_list)

    def delete_biometrics(
            self, weight_unit: str, biometrics_dto_list: list[BiometricsDTO]
    ) -> Biometrics:

        biometrics_list, biometrics_error = (
            self._map_biometrics_dto_to_biometrics(
                weight_unit=weight_unit, biometrics_dto_list=biometrics_dto_list
            )
        )
        self._biometrics_repo.delete_biometrics(biometrics_list=biometrics_list)

    def get_patient_biometrics_analytics(
            self, patient_id: int
    ) -> BiometricsAnalyticsDTO:
        biometrics_analytics: BiometricsAnalytics = (
            self._biometrics_repo.get_biometrics_analytics(
                patient_id=patient_id
            )
        )

        if biometrics_analytics is None:
            return None

        biometrics_analytics.weight_mean = grams_to_kilograms(
            biometrics_analytics.weight_mean
        )
        biometrics_analytics.weight_min = grams_to_kilograms(
            biometrics_analytics.weight_min
        )
        biometrics_analytics.weight_max = grams_to_kilograms(
            biometrics_analytics.weight_max
        )

        biometrics_analytics_dto: BiometricsAnalyticsDTO = (
            BiometricsAnalyticsDTO(**biometrics_analytics.dict())
        )
        return biometrics_analytics_dto

    def upsert_biometrics_analytics(
            self,
            biometrics_analytics_dto_list: list[BiometricsAnalyticsDTO]
    ):
        biometrics_analytics_list: list[BiometricsAnalytics] = []
        for ba_dto in biometrics_analytics_dto_list:
            biometrics_analytics_list.append(
                BiometricsAnalytics(
                    patient_id=ba_dto.patient_id,
                    glucose_mean=int(ba_dto.glucose_mean),
                    glucose_min=int(ba_dto.glucose_min),
                    glucose_max=int(ba_dto.glucose_max),
                    systolic_mean=int(
                        ba_dto.systolic_mean),
                    systolic_min=int(
                        ba_dto.systolic_min),
                    systolic_max=int(
                        ba_dto.systolic_max),
                    diastolic_mean=int(
                        ba_dto.diastolic_mean),
                    diastolic_min=int(
                        ba_dto.diastolic_min),
                    diastolic_max=int(
                        ba_dto.diastolic_max),
                    weight_mean=int(ba_dto.weight_mean),
                    weight_min=int(ba_dto.weight_min),
                    weight_max=int(ba_dto.weight_max),
                )
            )
        self._biometrics_repo.upsert_biometrics_analytics(
            biometrics_analytics_list
        )

    def _map_biometrics_dto_to_biometrics(
            self, weight_unit: str, biometrics_dto_list: list[BiometricsDTO]
    ):

        biometrics_list: list[Biometrics] = []
        biometrics_error: list[BiometricsDTO] = []

        for biometrics_dto in biometrics_dto_list:
            if weight_unit != 'metric':
                weight = pounds_to_grams(biometrics_dto.weight)
            else:
                weight = kilograms_to_grams(biometrics_dto.weight)
            try:
                biometrics: Biometrics = Biometrics(
                    patient_id=biometrics_dto.patient_id,
                    biometrics_id=biometrics_dto.biometrics_id,
                    test_date=biometrics_dto.test_date,
                    glucose=biometrics_dto.glucose,
                    systolic=biometrics_dto.systolic,
                    diastolic=biometrics_dto.diastolic,
                    weight=weight
                )

                biometrics_list.append(biometrics)
            except ValueError:
                biometrics_error.append(biometrics_dto)

        return biometrics_list, biometrics_error
