
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.asignatura import Asignatura
from models.usuario import Usuario
from database import get_db_connection
from api.perfil import perfil_usuario
from infrastructure.constants import Const

router = fastapi.APIRouter()


@router.get("/api/asignatura/lista/{id_usuario}", summary="Retorna la lista de asignaturas de acuerdo al perfil del usuario", tags=["Asignaturas"])
async def asignatura_lista(id_usuario: int):

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    asignaturas: List[Asignatura] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return asignaturas

    # Dependiendo del perfil, filtramos por carrera o no
    query: str = None
    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value or perfil.cod_perfil == Const.K_JEFE_BODEGA.value:
        query = " \
            select a.sigla as sigla, \
                a.nom_asign as nom_asign, \
                a.nom_asign_abrev as nom_asign_abrev, \
                a.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                round(sum(round(ct.cantidad * p.precio, 0)), 0) as costo_total \
            from asign a \
            join carrera c on a.cod_carrera = c.cod_carrera \
            left outer join taller t on a.sigla = t.sigla \
            left outer join config_taller ct on t.id_taller = ct.id_taller \
            left outer join producto p on ct.id_producto = p.id_producto \
            group by a.sigla, \
                a.nom_asign, \
                a.nom_asign_abrev, \
                a.cod_carrera, \
                c.nom_carrera \
            order by c.cod_carrera asc, \
                a.sigla"

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

        except Exception as e:
            error_message = str(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBerror {error_message}")

        finally:
            db.close()

    if perfil.cod_perfil in (Const.K_ADMINISTRADOR_CARRERA.value, Const.K_DOCENTE.value):
        query = " \
            select a.sigla as sigla, \
                a.nom_asign as nom_asign, \
                a.nom_asign_abrev as nom_asign_abrev, \
                a.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                round(sum(round(ct.cantidad * p.precio, 0)), 0) as costo_total \
            from asign a \
            join carrera c on a.cod_carrera = c.cod_carrera \
            join usuario u on c.cod_carrera = u.cod_carrera \
            left outer join  taller t on a.sigla = t.sigla \
            left outer join  config_taller ct on t.id_taller = ct.id_taller \
            left outer join  producto p on ct.id_producto = p.id_producto \
            where u.id_usuario = %s \
            group by a.sigla, \
                a.nom_asign, \
                a.nom_asign_abrev, \
                a.cod_carrera, \
                c.nom_carrera \
            order by c.cod_carrera asc, \
                a.sigla"

        db = await get_db_connection()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

        try:
            values = (id_usuario)
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
    asignatura: Asignatura = None
    for row in result:
        asignatura = Asignatura(sigla=row[0],
                                nom_asignatura=row[1],
                                nom_asignatura_abrev=row[2],
                                cod_carrera=row[3],
                                nom_carrera=row[4],
                                costo_total=(0 if row[5] is None else row[5]),)
        asignaturas.append(asignatura)

    return asignaturas


@router.delete("/api/asignatura/eliminar/{sigla}/{id_usuario}", response_model=dict, summary="Elimina una asignatura", tags=["Asignaturas"])
async def asignatura_eliminar(sigla: str, id_usuario: int):

    # Determinamos el perfil del usuario para determinar qué información puede borrar
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return {
            "sigla": sigla,
            "eliminado": False,
            "msg_error": "Usuario con perfil Docente no tiene acceso a eliminar"
        }

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = "delete from asign where sigla = %s"

        values = (sigla)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            await db.commit()

            return {
                "sigla": sigla,
                "eliminado": True,
                "msg_error": None
            }

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1451" in error_message:
            return {
                "sigla": sigla,
                "eliminado": False,
                "msg_error": "Asignatura no se puede eliminar por integridad de datos"
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


@router.get("/api/asignatura/{sigla}/{id_usuario}", response_model=Asignatura, summary="Recupera una asignatura en base a su sigla", tags=["Asignaturas"])
async def usuario_get(sigla: str, id_usuario: int):
    asignatura: Asignatura = {
            "sigla": "None",
            "nom_asignatura": "",
            "nom_asignatura_abrev": "",
            "cod_carrera": 0,
            "nom_carrera": "",
            "costo_total": 0,
        }

    # Si id_usuario_get = 0 se asume que es un usuario nuevo
    if sigla == "None":
        return asignatura

    # Determinamos el perfil del usuario conectado para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return asignatura

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            select a.sigla as sigla, \
                a.nom_asign as nom_asign, \
                a.nom_asign_abrev as nom_asign_abrev, \
                a.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                round(sum(round(ct.cantidad * p.precio, 0)), 0) as costo_total \
            from asign a \
            join carrera c on a.cod_carrera = c.cod_carrera \
            left outer join taller t on a.sigla = t.sigla \
            left outer join config_taller ct on t.id_taller = ct.id_taller \
			left outer join producto p on ct.id_producto = p.id_producto \
            where a.sigla = %s \
            group by a.sigla, \
                a.nom_asign, \
                a.nom_asign_abrev, \
                a.cod_carrera, \
                c.nom_carrera"

        values = (sigla)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()
            if not result:
                return asignatura

            asignatura = Asignatura(sigla=result[0],
                                    nom_asignatura=result[1],
                                    nom_asignatura_abrev=result[2],
                                    cod_carrera=result[3],
                                    nom_carrera=result[4],
                                    costo_total=(0 if result[5] is None else result[5]),)
            return asignatura

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


@router.put("/api/asignatura", response_model=Asignatura, summary="Modificar una asignatura", tags=["Asignaturas"])
async def asignatura_update(asignatura: Asignatura) -> Asignatura:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            update asign \
            set nom_asign = %s, \
                nom_asign_abrev = %s, \
                cod_carrera = %s \
            where sigla = %s"
        values = (asignatura.nom_asignatura,
                  asignatura.nom_asignatura_abrev,
                  asignatura.cod_carrera,
                  asignatura.sigla)
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

    return asignatura


@router.post("/api/asignatura", response_model=Asignatura, summary="Agregar una asignatura", tags=["Asignaturas"])
async def asignatura_insertar(asignatura: Asignatura) -> Asignatura:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = "insert into asign ( \
                    sigla, \
                    nom_asign, \
                    nom_asign_abrev, \
                    cod_carrera) \
                values (%s, \
                    %s, \
                    %s, \
                    %s)"
        values = (asignatura.sigla,
                  asignatura.nom_asignatura,
                  asignatura.nom_asignatura_abrev,
                  asignatura.cod_carrera)
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

    return asignatura
