from datetime import datetime

import pytest
from pydantic import ValidationError

from src.etl.domain.biometrics import Biometrics


def test_ok_biometrics_entity():
    biometrics: Biometrics = Biometrics(patient_id=1,
                                        test_date=datetime.now(),
                                        glucose=100,
                                        diastolic=70,
                                        systolic=120,
                                        weight=70000
                                        )

    assert biometrics.diastolic == 70
    assert biometrics.systolic == 120
    assert biometrics.glucose == 100
    assert biometrics.weight == 70000


def test_ok_biometric_blood_pressure_missing():
    # Blood pressure missing systolic and diastolic test
    biometrics: Biometrics = Biometrics(patient_id=1,
                                        test_date=datetime.now(),
                                        glucose=100,
                                        weight=70000
                                        )

    assert biometrics.glucose == 100
    assert biometrics.weight == 70000


def test_ko_biometrics_entity():
    with pytest.raises(ValidationError):
        # Blood pressure inconsistency test
        Biometrics(patient_id=1,
                   test_date=datetime.now(),
                   glucose=100,
                   diastolic=170,
                   systolic=120,
                   weight=70000
                   )

    with pytest.raises(ValidationError):
        # Blood pressure systolic outliers test
        Biometrics(patient_id=1,
                   test_date=datetime.now(),
                   glucose=100,
                   diastolic=70,
                   systolic=500,
                   weight=70000
                   )

    with pytest.raises(ValidationError):
        # Blood pressure diastolic outliers test
        Biometrics(patient_id=1,
                   test_date=datetime.now(),
                   glucose=100,
                   diastolic=210,
                   systolic=220,
                   weight=70000
                   )

    with pytest.raises(ValidationError):
        # Blood pressure missing diastolic test
        Biometrics(patient_id=1,
                   test_date=datetime.now(),
                   glucose=100,
                   systolic=120,
                   weight=70000
                   )

    with pytest.raises(ValidationError):
        # Blood pressure missing systolic test
        Biometrics(patient_id=1,
                   test_date=datetime.now(),
                   glucose=100,
                   diastolic=70,
                   weight=70000
                   )
