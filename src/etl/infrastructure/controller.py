import base64
import json
from typing import Annotated

from fastapi import APIRouter, Depends, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from kink import di

from src.building_blokcs.errors import APIErrorMessage
from src.etl.application.biometrics_service import BiometricsService
from src.etl.application.dto import PatientDTO, PatientPaginationDTO, \
    BiometricsPaginationDTO, BiometricsDTO, BiometricsAnalyticsDTO
from src.etl.application.patient_service import PatientService
from src.etl.infrastructure.postgresql_biometrics_repository import \
    PostgreSQLBiometricsRepository
from src.etl.infrastructure.postgresql_patient_repository import \
    PostgreSQLPatientRepository

patient_repo = PostgreSQLPatientRepository()
di[PatientService] = PatientService(patient_repo=patient_repo)

biometrics_repo = PostgreSQLBiometricsRepository()
di[BiometricsService] = BiometricsService(biometrics_repo=biometrics_repo)

router = APIRouter()


@router.get(
    "/patients",
    response_model=PatientPaginationDTO,
    responses={
        400: {"model": APIErrorMessage},
        401: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["Get list of patients"],
    description="Get list of patients. This resource can be paginated using the <b>next_page_token</b> parameter. The <b>limit parameter</b> controls the number of results starting from the next result pointed to by the <b>next_page_token</b>.",
)
async def patients(
        next_page_token: str = "0", limit: int = 10,
        service: PatientService = Depends(lambda: di[PatientService]),
) -> JSONResponse:
    patient_id = int(next_page_token)
    patients_dto: list[PatientDTO] = service.get_patients(patient_id=patient_id,
                                                          limit=limit)
    patient_pagination_dto = PatientPaginationDTO(patients=patients_dto,
                                                  next_page_token=str(
                                                      patients_dto[
                                                          -1].patient_id))
    if len(patients_dto):
        status_code = status.HTTP_200_OK
    else:
        status_code = status.HTTP_404_NOT_FOUND
    return JSONResponse(content=jsonable_encoder(patient_pagination_dto.dict()),
                        status_code=status_code)


@router.get(
    "/patient/{patient_id}/history",
    response_model=BiometricsPaginationDTO,
    responses={
        400: {"model": APIErrorMessage},
        401: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["Get history biometrics for a patient"],
    description="Get patient history biometrics. This resource can be paginated using the <b>next_page_token</b> parameter. The <b>limit</b> parameter controls the number of results starting from the next result pointed to by the <b>next_page_token</b>.<br/>The param <b>filter_by</b> is a list of columns.",
)
async def patients_history(
        patient_id: int,
        filter_by: Annotated[list[str] | None, Query()] = None,
        next_page_token: str | None = None, limit: int = 10,
        service: BiometricsService = Depends(lambda: di[BiometricsService]),
) -> JSONResponse:
    if next_page_token:
        token_decode = base64.urlsafe_b64decode(next_page_token)
        token_tuple = tuple(json.loads(token_decode.decode("utf-8")))
        biometrics_id = token_tuple[0]
        test_date = token_tuple[1]
        biometrics_dto: list[BiometricsDTO] = service.get_biometrics(
            patient_id=patient_id,
            weight_unit='metric',
            biometrics_id=biometrics_id,
            test_date=test_date,
            limit=limit
        )
    else:
        biometrics_dto: list[BiometricsDTO] = service.get_biometrics(
            patient_id=patient_id, weight_unit='metric', limit=limit
        )

    if len(biometrics_dto) == 0:
        # If no content, raise an exception to return only response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    status_code = status.HTTP_200_OK
    next_token_tuple = (
        biometrics_dto[-1].biometrics_id, biometrics_dto[-1].test_date
    )
    new_next_token_page = base64.urlsafe_b64encode(
        json.dumps(jsonable_encoder(next_token_tuple)).encode())

    biometrics_pagination_dto = BiometricsPaginationDTO(
        biometrics_history=biometrics_dto, next_page_token=new_next_token_page)

    result_dict = biometrics_pagination_dto.dict()

    if filter_by:
        available_columns = {"glucose", "systolic", "diastolic", "weight"}
        filter_columns = available_columns.symmetric_difference(filter_by)

        for b in result_dict['biometrics_history']:
            for column in filter_columns:
                del b[column]

    return JSONResponse(
        content=jsonable_encoder(result_dict),
        status_code=status_code)


@router.get(
    "/patient/{patient_id}/metrics",
    response_model=BiometricsAnalyticsDTO,
    responses={
        400: {"model": APIErrorMessage},
        401: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["Get derived metrics for a patient"],
    description="Get patient derived biometrics.",
)
async def patient_metrics(
        patient_id: int,
        service: BiometricsService = Depends(lambda: di[BiometricsService]),
) -> JSONResponse:
    biometrics_analytics_dto: BiometricsAnalyticsDTO = (
        service.get_patient_biometrics_analytics(patient_id=patient_id)
    )

    if biometrics_analytics_dto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return JSONResponse(
        content=jsonable_encoder(biometrics_analytics_dto.dict()),
        status_code=status.HTTP_200_OK)


@router.post(
    "/biometrics",
    response_model=BiometricsDTO,
    responses={
        400: {"model": APIErrorMessage},
        401: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["Add biometrics"],
    description="Add biometrics for patient.",
)
async def add_biometrics(
        model: BiometricsDTO,
        service: BiometricsService = Depends(lambda: di[BiometricsService]),
) -> JSONResponse:
    # weight_unit hardcode only for assessment
    service.insert_biometrics(weight_unit="metric", biometrics_dto_list=[model])
    return JSONResponse(status_code=status.HTTP_201_CREATED)


@router.put(
    "/biometrics",
    responses={
        400: {"model": APIErrorMessage},
        401: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["Upsert biometrics"],
    description="Upsert patient biometrics.",
    status_code=204,
)
async def upsert_biometrics(
        model: BiometricsDTO,
        service: BiometricsService = Depends(lambda: di[BiometricsService]),
) -> None:
    service.upsert_biometrics(weight_unit='metric', biometrics_dto_list=[model])
    return None


@router.delete(
    "/biometrics",
    responses={
        400: {"model": APIErrorMessage},
        401: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["Update biometrics"],
    description="Update one entry of patient biometrics.",
    status_code=204,
)
async def delete_biometrics(
        model: BiometricsDTO,
        service: BiometricsService = Depends(lambda: di[BiometricsService]),
) -> None:
    service.delete_biometrics(weight_unit='metric', biometrics_dto_list=[model])
    return None
