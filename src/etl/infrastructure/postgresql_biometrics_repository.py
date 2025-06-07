from datetime import datetime

from pandas import DataFrame
from pandas.io import sql as panda_sql

from src.etl.domain.biometrics_analytics import BiometricsAnalytics
from src.etl.domain.biometrics_repository import IBiometricsRepository
from src.etl.domain.biometrics import Biometrics

from psycopg2 import sql, connect
from psycopg2.extras import RealDictCursor, execute_batch


class PostgreSQLBiometricsRepository(IBiometricsRepository):

    def __init__(self):
        self._connection = connect(database="kannact", user="postgres",
                                   password="kannact", host="192.168.1.92",
                                   port=15432)

    def get_biometrics(self, patient_id: int, biometrics_id: int = 0,
                       test_date: datetime = datetime(1970, 1, 1),
                       limit: int = 10
                       ) -> list[Biometrics]:

        biometrics_list: list[Biometrics] = []

        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        query = sql.SQL(
            """
            SELECT *
            FROM kannact.biometrics 
            WHERE patient_id=%s AND (biometrics_id, test_date) > (%s, %s) 
            ORDER BY biometrics_id, test_date LIMIT %s
            """
        )
        cursor.execute(query, (patient_id, biometrics_id, test_date, limit))
        rows = cursor.fetchall()

        for row in rows:
            biometrics: Biometrics = Biometrics(**row)
            biometrics_list.append(biometrics)

        return biometrics_list

    def get_dataframe_biometrics(self) -> DataFrame:
        return panda_sql.read_sql_query(
            """
            SELECT patient_id, glucose, systolic, diastolic, weight 
            FROM kannact.biometrics""", con=self._connection
        )

    def insert_biometrics(self, biometrics_list: list[Biometrics]):
        cursor = self._connection.cursor()
        query = sql.SQL(
            """
            INSERT INTO kannact.biometrics 
            (patient_id, test_date, glucose, systolic, diastolic, weight)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        )
        biometrics_batch = []

        for biometrics in biometrics_list:
            biometrics_batch.append(
                (biometrics.patient_id, biometrics.test_date,
                 biometrics.glucose, biometrics.systolic, biometrics.diastolic,
                 biometrics.weight))

        execute_batch(cur=cursor, sql=query, argslist=(*biometrics_batch,),
                      page_size=100)
        self._connection.commit()

    def update_biometrics(self, biometrics_list: list[Biometrics]):
        cursor = self._connection.cursor()
        query = sql.SQL(
            """
            UPDATE kannact.biometrics 
            SET test_date=%s, glucose=%s, systolic=%s, diastolic=%s, weight=%s
            WHERE patient_id=%s AND biometrics_id=%s
            """
        )
        biometrics_batch = []

        for biometrics in biometrics_list:
            biometrics_batch.append((biometrics.test_date, biometrics.glucose,
                                     biometrics.systolic, biometrics.diastolic,
                                     biometrics.weight, biometrics.patient_id,
                                     biometrics.biometrics_id))

        execute_batch(cur=cursor, sql=query, argslist=(*biometrics_batch,),
                      page_size=100)
        self._connection.commit()

    def upsert_biometrics(self, biometrics_list: list[Biometrics]):
        cursor = self._connection.cursor()
        query = sql.SQL(
            """
            MERGE INTO kannact.biometrics AS target
            USING
            (
                VALUES(%s, %s, %s, %s, %s, %s, %s)
            )
            AS source 
            (
            patient_id, biometrics_id, test_date, 
            glucose, systolic, diastolic, weight
            )
            ON target.patient_id = source.patient_id 
            AND target.biometrics_id = source.biometrics_id
            WHEN matched THEN
            UPDATE SET
            test_date=source.test_date, 
            glucose=source.glucose, 
            systolic=source.systolic, 
            diastolic=source.diastolic, 
            weight=source.weight
            WHEN NOT matched THEN
            INSERT
            (
            patient_id, test_date, glucose, systolic, diastolic, weight
            )
            VALUES
            (
            source.patient_id, source.test_date, source.glucose, 
            source.systolic, source.diastolic, source.weight
            )
            """
        )
        biometrics_batch = []

        for biometrics in biometrics_list:
            biometrics_batch.append(
                (biometrics.patient_id, biometrics.biometrics_id,
                 biometrics.test_date, biometrics.glucose,
                 biometrics.systolic, biometrics.diastolic, biometrics.weight))

        execute_batch(cur=cursor, sql=query, argslist=(*biometrics_batch,),
                      page_size=100)
        self._connection.commit()

    def delete_biometrics(self, biometrics_list: list[Biometrics]):
        cursor = self._connection.cursor()
        query = sql.SQL(
            """
            DELETE FROM kannact.biometrics
            WHERE patient_id=%s AND biometrics_id=%s
            """
        )
        biometrics_batch = []

        for biometrics in biometrics_list:
            biometrics_batch.append((
                biometrics.patient_id, biometrics.biometrics_id)
            )

        execute_batch(cur=cursor, sql=query, argslist=(*biometrics_batch,),
                      page_size=100)
        self._connection.commit()

    def get_biometrics_analytics(self, patient_id: int) -> BiometricsAnalytics:
        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        query = sql.SQL(
            """
            SELECT *
            FROM kannact.biometrics_analytics
            WHERE patient_id=%s
            """
        )
        cursor.execute(query, (patient_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        biometrics_analytics: BiometricsAnalytics = BiometricsAnalytics(**row)
        return biometrics_analytics

    def upsert_biometrics_analytics(
            self,
            biometrics_analytics_list: list[BiometricsAnalytics]
    ):
        cursor = self._connection.cursor()
        query = sql.SQL(
            """
            MERGE INTO kannact.biometrics_analytics AS target
            USING
            (
                VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ) 
            AS source
            (
            patient_id, 
            glucose_mean, glucose_min, glucose_max,
            systolic_mean, systolic_min, systolic_max, 
            diastolic_mean, diastolic_min, diastolic_max,
            weight_mean, weight_min, weight_max
            )
            ON target.patient_id=source.patient_id
            WHEN matched THEN
            UPDATE SET 
            glucose_mean=source.glucose_mean,
            glucose_min=source.glucose_min,
            glucose_max=source.glucose_max,
            systolic_mean=source.systolic_mean,
            systolic_min=source.systolic_min,
            systolic_max=source.systolic_max,
            diastolic_mean=source.diastolic_mean,
            diastolic_min=source.diastolic_min,
            diastolic_max=source.diastolic_max,
            weight_mean=source.weight_mean,
            weight_min=source.weight_min,
            weight_max=source.weight_max
            WHEN NOT matched THEN
            INSERT
            (
            patient_id, 
            glucose_mean, glucose_min, glucose_max,
            systolic_mean, systolic_min, systolic_max, 
            diastolic_mean, diastolic_min, diastolic_max,
            weight_mean, weight_min, weight_max
            )
            VALUES
            (
            source.patient_id, 
            source.glucose_mean, source.glucose_min, source.glucose_max,
            source.systolic_mean, source.systolic_min, source.systolic_max,
            source.diastolic_mean, source.diastolic_min, source.diastolic_max,
            source.weight_mean, source.weight_min, source.weight_max
            )            
            """
        )

        ba_batch = []
        for ba in biometrics_analytics_list:
            ba_batch.append(
                (
                    ba.patient_id,
                    ba.glucose_mean, ba.glucose_min, ba.glucose_max,
                    ba.systolic_mean, ba.systolic_min, ba.systolic_max,
                    ba.diastolic_mean, ba.diastolic_min, ba.diastolic_max,
                    ba.weight_mean, ba.weight_min, ba.weight_max
                )
            )
        execute_batch(cur=cursor, sql=query,
                      argslist=(*ba_batch,),
                      page_size=100)
        self._connection.commit()
