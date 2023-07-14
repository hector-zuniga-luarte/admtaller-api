
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.categoria_producto import CategoriaProducto
from database import get_db_connection

router = fastapi.APIRouter()


@router.get("/api/categoria_producto/lista", summary="Recupera las categorías posibles para los productos del sistema", tags=["Categorías de productos"])
async def categoria_producto_lista():

    query = " \
        select cp.cod_categ_producto as cod_categ_producto, \
            cp.nom_categ_producto as nom_categ_producto \
        from categ_producto cp \
        order by cp.cod_categ_producto asc"

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
    categoria_producto: CategoriaProducto = None
    categorias_producto: List[CategoriaProducto] = []
    for row in result:
        categoria_producto = CategoriaProducto(cod_categ_producto=row[0],
                                               nom_categ_producto=row[1],)
        categorias_producto.append(categoria_producto)

    return categorias_producto
