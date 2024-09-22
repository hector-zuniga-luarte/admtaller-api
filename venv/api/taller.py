
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.taller import Taller
from models.producto_taller import ProductoTaller
from database import get_db_connection
from api.perfil import perfil_usuario


router = fastapi.APIRouter()


@router.get("/api/asignatura/{sigla}/taller/lista", summary="Recupera la lista de los talleres de una asignatura", tags=["Talleres"])
async def taller_lista(sigla: str):

    query = " \
        select t.id_taller as id_taller, \
            t.titulo_preparacion as titulo_preparacion, \
            t.detalle_preparacion as detalle_preparacion, \
            t.semana as semana, \
            t.sigla as sigla, \
            a.nom_asign as nom_asign, \
            round(sum(round(ct.cantidad * p.precio, 0)), 0) as costo_total \
        from taller t \
        join asign a on t.sigla = a.sigla \
        left outer join config_taller ct on t.id_taller = ct.id_taller \
        left outer join producto p on ct.id_producto = p.id_producto \
        where t.sigla = %s \
        group by id_taller, \
            titulo_preparacion, \
            detalle_preparacion, \
            semana, \
            sigla \
        order by t.semana asc"
    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = (sigla)
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
    taller: Taller = None
    talleres: List[Taller] = []
    for row in result:
        taller = Taller(id_taller=row[0],
                        titulo_preparacion=row[1],
                        detalle_preparacion=row[2],
                        semana=row[3],
                        sigla=row[4],
                        nom_asign = row[5],
                        costo_total=(0 if row[6] is None else row[6]),)
        talleres.append(taller)

    return talleres


@router.delete("/api/taller/eliminar/{id_taller}", response_model=dict, summary="Elimina un taller de una asignatura", tags=["Talleres"])
async def asignatura_eliminar(id_taller: int):

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = "delete from taller where id_taller = %s"

        values = (id_taller)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            await db.commit()

            return {
                "id_taller": id_taller,
                "eliminado": True,
                "msg_error": None
            }

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1451" in error_message:
            return {
                "id_taller": id_taller,
                "eliminado": False,
                "msg_error": "Taller no se puede eliminar por integridad de datos"
            }
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBerror {error_message}")

    finally:
        db.close()


@router.get("/api/taller/{id_taller}/{id_usuario}", response_model=Taller, summary="Recupera un taller en base a su ID", tags=["Talleres"])
async def taller_get(id_taller: int, id_usuario: int):
    taller: Taller = {
        "id_taller": 0,
        "titulo_preparacion": "",
        "detalle_preparacion": "",
        "semana": 0,
        "sigla": "",
        "costo_total": 0,
    }

    # Si id_taller = 0 se asume que es un usuario nuevo
    if id_taller == 0:
        return taller

    # Determinamos el perfil del usuario conectado para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return taller

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            select t.id_taller as id_taller, \
                t.titulo_preparacion as titulo_preparacion, \
                t.detalle_preparacion as detalle_preparacion, \
                t.semana as semana, \
                t.sigla as sigla, \
                a.nom_asign as nom_asign, \
				round(sum(round(ct.cantidad * p.precio, 0)), 0) as costo_total \
            from taller t \
            join asign a on t.sigla = a.sigla \
			left outer join config_taller ct on t.id_taller = ct.id_taller \
			left outer join producto p on ct.id_producto = p.id_producto \
            where t.id_taller = %s \
            group by t.id_taller, \
                t.titulo_preparacion, \
                t.detalle_preparacion, \
                t.semana, \
                t.sigla, \
                a.nom_asign"

        values = (id_taller)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()
            if not result:
                return taller

            taller = Taller(id_taller=result[0],
                            titulo_preparacion=result[1],
                            detalle_preparacion=result[2],
                            semana=result[3],
                            sigla=result[4],
                            nom_asign=result[5],
                            costo_total=(0 if result[6] is None else result[6]),)
            return taller

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBerror {error_message}")

    finally:
        db.close()


@router.put("/api/taller", response_model=Taller, summary="Modificar un taller", tags=["Talleres"])
async def taller_update(taller: Taller) -> Taller:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            update taller \
                set titulo_preparacion = %s, \
                    detalle_preparacion = %s, \
                    semana = %s, \
                    sigla = %s \
            where id_taller = %s"
        values = (taller.titulo_preparacion,
                  taller.detalle_preparacion,
                  taller.semana,
                  taller.sigla,
                  taller.id_taller)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    return taller


@router.post("/api/taller", response_model=Taller, summary="Agregar un taller", tags=["Talleres"])
async def taller_insertar(taller: Taller) -> Taller:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            insert into taller ( \
                titulo_preparacion, \
                detalle_preparacion, \
                semana, \
                sigla) \
            values ( \
                %s, \
                %s, \
                %s, \
                %s)"
        values = (taller.titulo_preparacion,
                  taller.detalle_preparacion,
                  taller.semana,
                  taller.sigla)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            taller.id_taller = cursor.lastrowid

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1062" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al insertar registro existente. DBerror {error_message}")

        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    return taller


@router.get("/api/taller/{id_taller}/producto/lista", response_model=List[ProductoTaller], summary="Recupera la lista de los productos de un taller específico", tags=["Talleres"])
async def taller_producto_lista(id_taller: int):

    query = " \
        select ct.id_producto as id_producto, \
            ct.id_taller as id_taller, \
            ct.cod_agrupador as cod_agrupador, \
            ct.cantidad as cantidad, \
            um.nom_unidad_medida as nom_unidad_medida, \
            p.nom_producto as nom_producto, \
            p.cod_categ_producto as cod_categ_producto, \
            cp.nom_categ_producto as nom_categ_producto, \
            a.nom_agrupador as nom_agrupador, \
            p.precio as precio, \
            round(p.precio * ct.cantidad, 0) as total, \
            case \
				when ct.cod_agrupador = 1 then cp.cod_categ_producto \
                else 0 \
			end as orden \
        from config_taller ct \
        join producto p on ct.id_producto = p.id_producto \
        join categ_producto cp on cp.cod_categ_producto = p.cod_categ_producto \
        join agrupador a on ct.cod_agrupador = a.cod_agrupador \
        join unidad_medida um on um.cod_unidad_medida = p.cod_unidad_medida \
        where ct.id_taller = %s \
        order by ct.cod_agrupador asc, \
            orden asc, \
            p.nom_producto asc"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = (id_taller)
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
    producto: ProductoTaller = None
    productos: List[ProductoTaller] = []
    for row in result:
        producto = ProductoTaller(id_producto=row[0],
                                  id_taller=row[1],
                                  cod_agrupador=row[2],
                                  cantidad=row[3],
                                  nom_unidad_medida=row[4],
                                  nom_producto=row[5],
                                  cod_categ_producto=row[6],
                                  nom_categ_producto=row[7],
                                  nom_agrupador=row[8],
                                  precio=row[9],
                                  total=row[10],)

        productos.append(producto)

    return productos


@router.get("/api/taller/{id_taller}/producto/{id_producto}/agrupador/{cod_agrupador}", summary="Recupera la especificación del uso de un producto para un taller específico y su agrupación", tags=["Talleres"])
async def taller_producto_get(id_taller: int, id_producto: int, cod_agrupador: int):
    producto: ProductoTaller = {
        "id_producto": 0,
        "id_taller": 0,
        "cod_agrupador": 0,
        "cantidad": 0,
        "nom_unidad_medida": None,
        "nom_producto": None,
        "cod_categ_producto": None,
        "nom_categ_producto": None,
        "nom_agrupador": None,
        "precio": 0,
        "total": 0
    }
    query = " \
        select ct.id_producto as id_producto, \
            ct.id_taller as id_taller, \
            ct.cod_agrupador as cod_agrupador, \
            ct.cantidad as cantidad, \
            um.nom_unidad_medida as nom_unidad_medida, \
            p.nom_producto as nom_producto, \
            p.cod_categ_producto as cod_categ_producto, \
            cp.nom_categ_producto as nom_categ_producto, \
            a.nom_agrupador as nom_agrupador, \
            p.precio as precio, \
            p.precio * ct.cantidad as total \
        from config_taller ct \
        join producto p on ct.id_producto = p.id_producto \
        join categ_producto cp on cp.cod_categ_producto = p.cod_categ_producto \
        join agrupador a on ct.cod_agrupador = a.cod_agrupador \
        join unidad_medida um on um.cod_unidad_medida = p.cod_unidad_medida \
        where ct.id_taller = %s and \
            ct.id_producto = %s and \
            ct.cod_agrupador = %s"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = (id_taller, id_producto, cod_agrupador)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()

            if not result:
                return producto

            producto = ProductoTaller(id_producto=result[0],
                                      id_taller=result[1],
                                      cod_agrupador=result[2],
                                      cantidad=result[3],
                                      nom_unidad_medida=result[4],
                                      nom_producto=result[5],
                                      cod_categ_producto=result[6],
                                      nom_categ_producto=result[7],
                                      nom_agrupador=result[8],
                                      precio=result[9],
                                      total=result[10],)

            return producto

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


@router.delete("/api/taller/eliminar/{id_taller}/producto/{id_producto}/agrupador/{cod_agrupador}", response_model=dict, summary="Elimina un producto de taller en particular asociado a un agrupador", tags=["Talleres"])
async def producto_taller_eliminar(id_taller: int, id_producto: int, cod_agrupador: int):

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = "delete from config_taller where id_taller = %s and id_producto = %s and cod_agrupador = %s"

        values = (id_taller, id_producto, cod_agrupador)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            await db.commit()

            return {
                "id_taller": id_taller,
                "id_producto": id_producto,
                "cod_agrupador": cod_agrupador,
                "eliminado": True,
                "msg_error": None
            }

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1451" in error_message:
            return {
                "id_taller": id_taller,
                "eliminado": False,
                "msg_error": "Taller no se puede eliminar por integridad de datos"
            }
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBerror {error_message}")

    finally:
        db.close()

    return {
        "id_taller": id_taller,
        "id_producto": id_producto,
        "cod_agrupador": cod_agrupador,
        "eliminado": True
    }


@router.put("/api/taller/producto/agrupador", response_model=ProductoTaller, summary="Modificar un producto de un taller específico por un tipo de agrupador", tags=["Talleres"])
async def producto_taller_update(producto: ProductoTaller) -> ProductoTaller:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            update config_taller \
                set cantidad = %s \
            where id_taller = %s and \
                id_producto = %s and \
                cod_agrupador = %s"
        values = (producto.cantidad,
                  producto.id_taller,
                  producto.id_producto,
                  producto.cod_agrupador)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    return producto


@router.post("/api/taller/producto/agrupador", response_model=ProductoTaller, summary="Agregar un producto de un taller específico con su agrupador respectivo", tags=["Talleres"])
async def producto_taller_insertar(producto: ProductoTaller) -> ProductoTaller:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            insert into config_taller ( \
                id_taller, \
                id_producto, \
                cod_agrupador, \
                cantidad) \
            values ( \
                %s, \
                %s, \
                %s, \
                %s)"
        values = (producto.id_taller,
                  producto.id_producto,
                  producto.cod_agrupador,
                  producto.cantidad)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1062" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al insertar registro existente. DBerror {error_message}")

        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    return producto
