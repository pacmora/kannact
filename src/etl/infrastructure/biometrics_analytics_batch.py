from kink import di
from pandas import DataFrame
from psycopg2 import connect

from src.etl.application.biometrics_service import BiometricsService
from src.etl.application.dto import BiometricsAnalyticsDTO
from src.etl.domain.biometrics_repository import IBiometricsRepository
from src.etl.infrastructure.postgresql_biometrics_repository import \
    PostgreSQLBiometricsRepository


biometrics_repo = PostgreSQLBiometricsRepository()
di[IBiometricsRepository] = biometrics_repo
di[BiometricsService] = BiometricsService(
    biometrics_repo=di[IBiometricsRepository]
)


class BiometricsAnalyticsBatch:

    def __init__(self):
        self._biometrics_repo: IBiometricsRepository = di[IBiometricsRepository]
        self._biometrics_service: BiometricsService = di[BiometricsService]
        self._connection = connect(database="kannact", user="postgres",
                                   password="kannact", host="192.168.1.92",
                                   port=15432)

    def calculate_metrics(self):
        df: DataFrame = self._biometrics_repo.get_dataframe_biometrics()

        df = df.groupby(['patient_id'], as_index=False).agg(['mean', 'min', 'max'])
        df = flatten_cols(df=df)

        result: list[BiometricsAnalyticsDTO] = []
        for row in df.to_dict(orient='records'):
            b: BiometricsAnalyticsDTO = BiometricsAnalyticsDTO(**row)
            result.append(b)

        self._biometrics_service.upsert_biometrics_analytics(
            result
        )


def flatten_cols(df):
    df.columns = [
        '_'.join(tuple(map(str, t))).rstrip('_')
        for t in df.columns.values
        ]
    return df

