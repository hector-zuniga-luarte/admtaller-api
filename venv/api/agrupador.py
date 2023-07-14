
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.agrupador import Agrupador
from database import get_db_connection

router = fastapi.APIRouter()


@router.get("/api/agrupador/lista", summary="Recupera los agrupadores para asociar a los productos de un taller", tags=["Agrupadores"])
async def agrupadores():

    query = " \
        select ag.cod_agrupador as cod_agrupador, \
            ag.nom_agrupador as nom_agrupador \
        from agrupador ag \
        order by ag.cod_agrupador asc"

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
    agrupador: Agrupador = None
    agrupadores: List[Agrupador] = []
    for row in result:
        agrupador = Agrupador(cod_agrupador=row[0],
                              nom_agrupador=row[1])
        agrupadores.append(agrupador)

    return agrupadores
