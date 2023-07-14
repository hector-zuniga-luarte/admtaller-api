
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.unidad_medida import UnidadMedida
from database import get_db_connection

router = fastapi.APIRouter()


@router.get("/api/unidad_medida/lista", summary="Recupera las unidades de medida de los productos", tags=["Unidades de medida"])
async def unidad_medida_lista():

    query = " \
        select um.cod_unidad_medida as cod_unidad_medida, \
            um.nom_unidad_medida as nom_unidad_medida, \
            um.nom_unidad_medida_abrev as nom_unidad_medida_abrev \
        from unidad_medida um \
        order by um.nom_unidad_medida asc"

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
    unidad_medida: UnidadMedida = None
    unidades_medida: List[UnidadMedida] = []
    for row in result:
        unidad_medida = UnidadMedida(cod_unidad_medida=row[0],
                                     nom_unidad_medida=row[1],
                                     nom_unidad_medida_abrev=row[2])
        unidades_medida.append(unidad_medida)

    return unidades_medida
