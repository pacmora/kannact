from src.etl.domain.patient import Patient
from src.etl.domain.patient_repository import IPatientRepository

from psycopg2 import sql, connect
from psycopg2.extras import RealDictCursor, execute_batch


class PostgreSQLPatientRepository(IPatientRepository):

    def __init__(self):
        self._connection = connect(database="kannact", user="postgres",
                                   password="kannact", host="192.168.1.92",
                                   port=15432)

    def get_patients(self, patient_id: int, limit: int = 10) -> list[Patient]:
        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        query = sql.SQL(
            "SELECT * FROM kannact.patients WHERE patient_id>%s LIMIT %s")
        cursor.execute(query, (patient_id, limit))
        rows = cursor.fetchall()

        patient_list: list[Patient] = []
        for row in rows:
            patient_list.append(Patient(**row))

        return patient_list

    def insert_patient(self, patients: list[Patient]):
        cursor = self._connection.cursor()
        query = sql.SQL(
            """
            INSERT INTO kannact.patients 
            (name, date_of_birth, gender, email, address, phone, sex)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        )
        patients_batch = []
        for patient in patients:
            patients_batch.append((patient.name, patient.date_of_birth,
                                   patient.gender, patient.email,
                                   patient.address, patient.phone, patient.sex))

        execute_batch(cur=cursor, sql=query, argslist=(*patients_batch,),
                      page_size=100)
        self._connection.commit()
