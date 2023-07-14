
import fastapi
from models.perfil import Perfil
from typing import List
from fastapi import HTTPException
from fastapi import status
import aiomysql

from database import get_db_connection
from infrastructure.constants import Const

router = fastapi.APIRouter()


@router.get("/api/perfil/usuario/{id_usuario}", response_model=Perfil, summary="Obtener el perfil de un usuario a través de su id", tags=["Perfiles"])
async def perfil_usuario(id_usuario: int):
    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            select p.cod_perfil as cod_perfil, \
                p.nom_perfil as nom_perfil, \
                p.descripcion as descripcion \
            from perfil p, \
                usuario u \
            where u.cod_perfil = p.cod_perfil and \
                u.id_usuario = %s"
        values = (id_usuario)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()

        if not result:
            return None

        perfil = Perfil(cod_perfil=result[0],
                        nom_perfil=result[1],
                        descripcion=result[2])
        return perfil

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        print(error_message)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBerror {error_message}")

    finally:
        db.close()


@router.get("/api/perfil/nom_carrera/{id_usuario}", response_model=dict, summary="Obtener el nombre de la carrera asignada al usuario respectivo", tags=["Perfiles"])
async def perfil_nom_carrera(id_usuario: int):
    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            select c.nom_carrera as nom_carrera \
            from carrera c, \
                usuario u \
            where u.cod_carrera = c.cod_carrera and \
                u.id_usuario = %s"
        values = (id_usuario)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()

        nom_carrera: str = None
        if result:
            nom_carrera = result[0]

        return {
            "nom_carrera": nom_carrera,
        }

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}.")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. {e}")

    finally:
        db.close()


@router.get("/api/perfil/cod_carrera/{id_usuario}", response_model=dict, summary="Obtener el código de la carrera asignada al usuario respectivo", tags=["Perfiles"])
async def perfil_cod_carrera(id_usuario: int):
    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            select u.cod_carrera as cod_carrera \
            from usuario u \
            where u.id_usuario = %s"
        values = (id_usuario)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()

        cod_carrera: int = None
        if result:
            cod_carrera = result[0]

        return {
            "cod_carrera": cod_carrera,
        }

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}.")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. {e}")

    finally:
        db.close()


@router.get("/api/perfil/lista/{id_usuario}", response_model=List[Perfil], summary="Obtener la lista de perfiles desde el sistema", tags=["Perfiles"])
async def perfil_lista(id_usuario: int) -> List[Perfil]:
    perfiles: List[Perfil] = []

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return perfiles
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return perfiles

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        query = " \
            select p.cod_perfil as cod_perfil, \
                p.nom_perfil as nom_perfil, \
                p.descripcion as descripcion \
            from perfil p \
            where cod_perfil <> 0 \
            order by p.cod_perfil asc"

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value:
        query = " \
            select p.cod_perfil as cod_perfil, \
                p.nom_perfil as nom_perfil, \
                p.descripcion as descripcion \
            from perfil p \
            order by p.cod_perfil asc"

    try:
        values = ()
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchall()

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}.")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. {e}")

    finally:
        db.close()

    # Armamos el diccionario de salida
    perfil: Perfil = None
    for row in result:
        perfil = Perfil(cod_perfil=row[0],
                        nom_perfil=row[1],
                        descripcion=row[2])
        perfiles.append(perfil)

    return perfiles
