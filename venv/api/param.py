
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql
from database import get_db_connection

from models.param import Param
from models.periodo_academico import PeriodoAcademico
import datetime
from typing import List


router = fastapi.APIRouter()


@router.get("/api/param/lista", response_model=List[Param], summary="Obtener la lista de parámetros desde el sistema", tags=["Parámetros"])
async def param_lista():

    query = " \
        select p.cod_param as cod_param, \
            p.nom_param as nom_param, \
            p.valor as valor \
        from param p \
        order by p.cod_param asc"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = ()
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchall()

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

    finally:
        db.close()

    # Armamos el diccionario de salida
    params: List[Param] = []
    param: Param = None
    for row in result:
        param = Param(cod_param=row[0],
                      nom_param=row[1],
                      valor=row[2])
        params.append(param)

    return params


@router.get("/api/param/{cod_param}", response_model=Param, summary="Obtener un parámetro específico en base a su código", tags=["Parámetros"])
async def param_get(cod_param: int):

    query = " \
        select p.cod_param as cod_param, \
            p.nom_param as nom_param, \
            p.valor as valor \
        from param p \
        where p.cod_param = %s"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = (cod_param)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

    finally:
        db.close()

    # Armamos el diccionario de salida
    param: Param = Param(cod_param=0, nom_param="", valor="")
    if result:
        param = Param(cod_param=result[0],
                      nom_param=result[1],
                      valor=result[2])

    return param


@router.get("/api/param/ano_academ/valor", response_model=dict, summary="Obtener el valor del parámetro año académico vigente", tags=["Parámetros"])
async def param_ano_academ_valor():
    ano_academ: str = str(datetime.datetime.now().year)
    K_ANOACADEMVIGENTE: int = 1

    try:
        param: param = await param_get(K_ANOACADEMVIGENTE)
        ano_academ = param.valor
    except Exception:
        pass

    return {
        "ano_academ": ano_academ,
    }


@router.put("/api/param", response_model=Param, summary="Modificar un parámetro del sistema", tags=["Parámetros"])
async def param_update(param: Param) -> Param:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            update param \
                set valor = %s \
            where cod_param = %s"
        values = (param.valor,
                  param.cod_param)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            affected_rows = cursor.rowcount

        if affected_rows == 0:
            param.cod_param = 0
            param.nom_param = ""
            param.valor = ""

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    # Recuperamos el resto del objeto para retornarlo completo
    param_aux = await param_get(param.cod_param)
    param.nom_param = param_aux.nom_param
    return param


@router.get("/api/param/periodo/lista", response_model=List[PeriodoAcademico], summary="Obtener la lista de períodos académicos para programación", tags=["Parámetros"])
async def periodo_lista():

    query = " \
        select pa.cod_periodo_academ as cod_periodo_academ, \
            pa.nom_periodo_academ as nom_periodo_academ, \
            pa.nom_periodo_academ_abrev as nom_periodo_academ_abrev \
        from periodo_academ pa \
        order by pa.cod_periodo_academ"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = ()
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchall()

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

    finally:
        db.close()

    # Armamos el diccionario de salida
    periodos: List[PeriodoAcademico] = []
    periodo: PeriodoAcademico = None
    for row in result:
        periodo = PeriodoAcademico(cod_periodo_academ=row[0],
                                   nom_periodo_academ=row[1],
                                   nom_periodo_academ_abrev=row[2])
        periodos.append(periodo)

    return periodos


@router.get("/api/param/periodo/{cod_periodo_academ}", response_model=PeriodoAcademico, summary="Obtener un periodo académico en base a su código", tags=["Parámetros"])
async def periodo_get(cod_periodo_academ: int):

    query = " \
        select pa.cod_periodo_academ as cod_periodo_academ, \
            pa.nom_periodo_academ as nom_periodo_academ, \
            pa.nom_periodo_academ_abrev as nom_periodo_academ_abrev \
        from periodo_academ pa \
        where cod_periodo_academ = %s"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = (cod_periodo_academ)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

    finally:
        db.close()

    # Armamos el diccionario de salida
    periodo = PeriodoAcademico(cod_periodo_academ=result[0],
                               nom_periodo_academ=result[1],
                               nom_periodo_academ_abrev=result[2])

    return periodo
