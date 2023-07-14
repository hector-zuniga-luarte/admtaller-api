
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.producto import Producto
from models.usuario import Usuario
from database import get_db_connection
from api.perfil import perfil_usuario
from infrastructure.constants import Const

router = fastapi.APIRouter()


@router.get("/api/producto/lista/{id_usuario}", summary="Recupera los productos del sistema para un determinado usuario", tags=["Productos"])
async def productos(id_usuario: int):
    productos: List[Producto] = []    

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return productos
    
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return productos

    query = " \
        select p.id_producto as id_producto, \
            p.nom_producto as nom_producto, \
            p.precio as precio, \
            p.cod_unidad_medida as cod_unidad_medida, \
            p.cod_categ_producto as cod_categ_producto, \
            um.nom_unidad_medida as nom_unidad_medida, \
            cp.nom_categ_producto as nom_categ_producto \
        from producto p \
        join unidad_medida um on p.cod_unidad_medida = um.cod_unidad_medida \
        join categ_producto cp on p.cod_categ_producto = cp.cod_categ_producto \
        order by p.nom_producto asc"

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
    producto: Producto = None
    productos: List[Producto] = []
    for row in result:
        producto = Producto(id_producto=row[0],
                            nom_producto=row[1],
                            precio=row[2],
                            cod_unidad_medida=row[3],
                            cod_categ_producto=row[4],
                            nom_unidad_medida=row[5],
                            nom_categ_producto=row[6])
        productos.append(producto)

    return productos


@router.delete("/api/producto/eliminar/{id_producto}/{id_usuario}", response_model=dict, summary="Elimina un producto para un determinado usuario", tags=["Productos"])
async def asignatura_eliminar(id_producto: int, id_usuario: int):

    # Determinamos el perfil del usuario para determinar qué información puede borrar
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return {
            "id_producto": id_producto,
            "eliminado": False,
            "msg_error": "Usuario con perfil Docente no tiene acceso a eliminar"
        }

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = "delete from producto where id_producto = %s"

        values = (id_producto)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            await db.commit()

            return {
                "id_producto": id_producto,
                "eliminado": True,
                "msg_error": None
            }

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1451" in error_message:
            return {
                "id_producto": id_producto,
                "eliminado": False,
                "msg_error": "Producto no se puede eliminar por integridad de datos"
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
        "id_producto": id_producto,
        "eliminado": True
    }


@router.get("/api/producto/{id_producto}/{id_usuario}", response_model=Producto, summary="Recupera un producto en base a su Id", tags=["Productos"])
async def producto_get(id_producto: int, id_usuario: int):
    producto: Producto = {
        "id_producto": 0,
        "nom_producto": "",
        "precio": 0,
        "cod_unidad_medida": 0,
        "cod_categ_producto": 0,
        "nom_unidad_medida": "",
        "nom_categ_producto": "",
    }

    # Si id_producto = 0 se asume que es nuevo
    if id_producto == 0:
        return producto

    # Determinamos el perfil del usuario conectado para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return producto
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return producto

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            select p.id_producto as id_producto, \
                p.nom_producto as nom_producto, \
                p.precio as precio, \
                p.cod_unidad_medida as cod_unidad_medida, \
                p.cod_categ_producto as cod_categ_producto, \
                um.nom_unidad_medida as nom_unidad_medida, \
                cp.nom_categ_producto as nom_categ_producto \
            from producto p \
            join unidad_medida um on p.cod_unidad_medida = um.cod_unidad_medida \
            join categ_producto cp on p.cod_categ_producto = cp.cod_categ_producto \
            where p.id_producto = %s"

        values = (id_producto)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()
            if not result:
                return producto

            producto = Producto(id_producto=result[0],
                                nom_producto=result[1],
                                precio=result[2],
                                cod_unidad_medida=result[3],
                                cod_categ_producto=result[4],
                                nom_unidad_medida=result[5],
                                nom_categ_producto=result[6],)
            return producto

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


@router.put("/api/producto/{id_usuario}/", response_model=Producto, summary="Modificar un producto", tags=["Productos"])
async def usuario_modificar(producto: Producto, id_usuario: int) -> Producto:

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no tiene privilegios para ejecutar la acción")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            update producto \
                set nom_producto = %s, \
                    precio = %s, \
                    cod_unidad_medida = %s, \
                    cod_categ_producto = %s \
            where id_producto = %s"
        values = (producto.nom_producto,
                  producto.precio,
                  producto.cod_unidad_medida,
                  producto.cod_categ_producto,
                  producto.id_producto)
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


@router.post("/api/producto", response_model=Producto, summary="Agregar un producto", tags=["Productos"])
async def usuario_insertar(producto: Producto) -> Producto:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            insert into producto ( \
                nom_producto, \
                precio, \
                cod_unidad_medida, \
                cod_categ_producto) \
            values (%s, \
                %s, \
                %s, \
                %s)"
        values = (producto.nom_producto,
                  producto.precio,
                  producto.cod_unidad_medida,
                  producto.cod_categ_producto)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            producto.id_producto = cursor.lastrowid

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
