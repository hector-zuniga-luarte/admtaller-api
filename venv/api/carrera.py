
import fastapi
from models.carrera import Carrera
from typing import List
from fastapi import HTTPException
from fastapi import status
import aiomysql
from api.perfil import perfil_usuario

from database import get_db_connection
from infrastructure.constants import Const

router = fastapi.APIRouter()


@router.get("/api/carrera/lista/{id_usuario}", summary="Obtener la lista de carreras desde el sistema", tags=["Carreras"])
async def carrera_lista(id_usuario: int):
    carreras: List[Carrera] = []

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return carreras
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return carreras

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        query = " \
            select c.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                c.nom_carrera_abrev as nom_carrera_abrev \
            from carrera c \
            where c.cod_carrera = (select u.cod_carrera \
                                    from usuario u \
                                    where u.id_usuario = %s) \
            order by c.cod_carrera asc"

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value:
        query = " \
            select c.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                c.nom_carrera_abrev as nom_carrera_abrev \
            from carrera c \
            where 0 = (select 0 \
                    from usuario u \
                    where u.id_usuario = %s) \
            order by c.cod_carrera asc"

    try:
        values = (id_usuario)
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

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. {e}")

    finally:
        db.close()

    # Armamos el diccionario de salida
    carrera: Carrera = None
    for row in result:
        carrera = Carrera(cod_carrera=row[0],
                          nom_carrera=row[1],
                          nom_carrera_abrev=row[2])
        carreras.append(carrera)

    return carreras
