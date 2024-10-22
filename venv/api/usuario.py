
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.usuario import Usuario
from database import get_db_connection
from api.perfil import perfil_usuario
from infrastructure.constants import Const

router = fastapi.APIRouter()


@router.get("/api/usuario/id_usuario/{login}", response_model=dict, summary="Recupera el ID de un usuario en base a su login", tags=["Usuarios"])
async def usuario_id_usuario(login: str):
    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        login = login.strip()
        query = "select id_usuario as id_usuario \
                from usuario \
                where login = %s"
        values = (login)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()

        return {
            "id_usuario": result[0],
        }

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


@router.get("/api/usuario/lista/{id_usuario}", response_model=List[dict], summary="Recupera la lista de usuarios del sistema de acuerdo al usuario que consulta", tags=["Usuarios"])
async def usuario_lista(id_usuario: int):

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return usuarios

    # Dependiendo del perfil, filtramos por carrera o no
    query: str = None
    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        query = " \
            select u.id_usuario as id_usuario, \
                u.login as login, \
                null as password, \
                u.primer_apellido as primer_apellido, \
                u.segundo_apellido as segundo_apellido, \
                u.nom as nom, \
                u.nom_preferido as nom_preferido, \
                u.cod_perfil as cod_perfil, \
                u.cod_carrera as nom_carrera, \
                p.nom_perfil as nom_perfil, \
                c.nom_carrera as nom_carrera \
            from usuario u \
            join perfil p on u.cod_perfil = p.cod_perfil \
            left join carrera c on u.cod_carrera = c.cod_carrera \
            where u.cod_carrera = (select us.cod_carrera \
                                from usuario us \
                                where us.id_usuario = %s) and \
                p.cod_perfil <> " + str(Const.K_ADMINISTRADOR_TI.value) + " \
            order by u.cod_carrera asc, \
                u.cod_perfil asc, \
                u.primer_apellido asc, \
                u.segundo_apellido asc, \
                u.nom_preferido asc"

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value:
        query = " \
        select u.id_usuario as id_usuario, \
                u.login as login, \
                null as password, \
                u.primer_apellido as primer_apellido, \
                u.segundo_apellido as segundo_apellido, \
                u.nom as nom, \
                u.nom_preferido as nom_preferido, \
                u.cod_perfil as cod_perfil, \
                u.cod_carrera as nom_carrera, \
                p.nom_perfil as nom_perfil, \
                c.nom_carrera as nom_carrera \
            from usuario u \
            join perfil p on u.cod_perfil = p.cod_perfil \
            left join carrera c on u.cod_carrera = c.cod_carrera \
            order by u.cod_carrera asc, \
                u.cod_perfil asc, \
                u.primer_apellido asc, \
                u.segundo_apellido asc, \
                u.nom_preferido asc"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
            values = (id_usuario)
        if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value:
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
    usuario: Usuario = None
    for row in result:
        usuario = Usuario(id_usuario=row[0],
                          login=row[1],
                          hash_password=None,
                          primer_apellido=row[3],
                          segundo_apellido=row[4],
                          nom=row[5],
                          nom_preferido=row[6],
                          cod_perfil=row[7],
                          cod_carrera=row[8],
                          nom_perfil=row[9],
                          nom_carrera=row[10])
        usuarios.append(usuario)

    return usuarios


@router.get("/api/usuario/{id_usuario_get}/{id_usuario}", response_model=Usuario, summary="Recupera un usuario en base a su ID", tags=["Usuarios"])
async def usuario_get(id_usuario_get: int, id_usuario: int):
    usuario: Usuario = {
        "id_usuario": 0,
        "login": "",
        "hash_password": "",
        "primer_apellido": "",
        "segundo_apellido": "",
        "nom": "",
        "nom_preferido": "",
        "cod_perfil": 0,
        "cod_carrera": 0,
        "nom_perfil": "",
        "nom_carrera": "",
    }

    # Si id_usuario_get = 0 se asume que es un usuario nuevo
    if id_usuario_get == 0:
        return usuario

    # Determinamos el perfil del usuario conectado para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuario

    # Perfil docente solo puede ver su propio usuario
    if perfil.cod_perfil == Const.K_DOCENTE.value and id_usuario_get != id_usuario:
        return usuario

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            select u.id_usuario as id_usuario, \
                u.login as login, \
                null as hash_password, \
                u.primer_apellido as primer_apellido, \
                u.segundo_apellido as segundo_apellido, \
                u.nom as nom, \
                u.nom_preferido as nom_preferido, \
                u.cod_perfil as cod_perfil, \
                u.cod_carrera as cod_carrera, \
                p.nom_perfil as nom_perfil, \
                c.nom_carrera as nom_carrera \
            from usuario u \
            join perfil p on u.cod_perfil = p.cod_perfil \
            left join carrera c on u.cod_carrera = c.cod_carrera \
            where id_usuario = %s"

        values = (id_usuario_get)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()
            if not result:
                return usuario

            usuario = Usuario(id_usuario=result[0],
                              login=result[1],
                              hash_password=None,
                              primer_apellido=result[3],
                              segundo_apellido=result[4],
                              nom=result[5],
                              nom_preferido=result[6],
                              cod_perfil=result[7],
                              cod_carrera=result[8],
                              nom_perfil=result[9],
                              nom_carrera=result[10])
            return usuario

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


@router.delete("/api/usuario/eliminar/{id_usuario_eliminar}/{id_usuario}", response_model=dict, summary="Elimina un usuario", tags=["Usuarios"])
async def usuario_eliminar(id_usuario_eliminar: int, id_usuario: int):

    # Determinamos el perfil del usuario para determinar qué información puede borrar
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return {
            "id_usuario": id_usuario_eliminar,
            "eliminado": False,
            "msg_error": "Usuario con perfil Docente no tiene acceso a eliminar"
        }

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = "delete from usuario where id_usuario = %s"

        values = (id_usuario_eliminar,)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            await db.commit()

            return {
                "id_usuario": id_usuario_eliminar,
                "eliminado": True,
                "msg_error": None
            }

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1451" in error_message:
            return {
                "id_usuario": id_usuario_eliminar,
                "eliminado": False,
                "msg_error": "Usuario no se puede eliminar por integridad de datos"
                }
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

    finally:
        db.close()

    return {
        "id_usuario": id_usuario_eliminar,
        "eliminado": True
    }


@router.put("/api/usuario/{id_usuario}", response_model=Usuario, summary="Modificar un usuario", tags=["Usuarios"])
async def usuario_modificar(usuario: Usuario, id_usuario: int) -> Usuario:

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    usuarios: List[Usuario] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return usuarios
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no tiene privilegios para ejecutar la acción")
    if (usuario.cod_perfil == Const.K_DOCENTE.value or usuario.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value) and not usuario.cod_carrera:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los usuarios de perfil docente o administrador de carrera deben tener una carrera definida")
    if (usuario.cod_perfil == Const.K_ADMINISTRADOR_TI.value or usuario.cod_perfil == Const.K_JEFE_BODEGA.value) and usuario.cod_carrera:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los usuarios de perfil administrador TI o jefe de bodega no deben tener una carrera definida")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = "update usuario \
                    set login = %s, \
                        hash_password = %s, \
                        primer_apellido = %s, \
                        segundo_apellido = %s, \
                        nom = %s, \
                        nom_preferido = %s, \
                        cod_perfil = %s, \
                        cod_carrera = %s \
                where id_usuario = %s"
        values = (usuario.login,
                  usuario.hash_password,
                  usuario.primer_apellido,
                  usuario.segundo_apellido,
                  usuario.nom,
                  usuario.nom_preferido,
                  usuario.cod_perfil,
                  usuario.cod_carrera,
                  usuario.id_usuario)
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

    return usuario


@router.post("/api/usuario", response_model=Usuario, summary="Agregar un usuario", tags=["Usuarios"])
async def usuario_insertar(usuario: Usuario) -> Usuario:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = "insert into usuario ( \
                    login, \
                    hash_password, \
                    primer_apellido, \
                    segundo_apellido, \
                    nom, \
                    nom_preferido, \
                    cod_perfil, \
                    cod_carrera) \
                values (%s, \
                    %s, \
                    %s, \
                    %s, \
                    %s, \
                    %s, \
                    %s, \
                    %s)"
        values = (usuario.login,
                    usuario.hash_password,
                    usuario.primer_apellido,
                    usuario.segundo_apellido,
                    usuario.nom,
                    usuario.nom_preferido,
                    usuario.cod_perfil,
                    usuario.cod_carrera)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            usuario.id_usuario = cursor.lastrowid

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

    return usuario
