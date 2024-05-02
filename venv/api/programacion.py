
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.programacion_asignatura import ProgramacionAsignatura
from models.programacion_taller import ProgramacionTaller
from models.usuario import Usuario
from database import get_db_connection
from api.perfil import perfil_usuario
from infrastructure.constants import Const
from api.perfil import perfil_cod_carrera
from datetime import datetime

router = fastapi.APIRouter()


@router.get("/api/programacion/asignatura/{ano_academ}/{id_usuario}/lista", summary="Recupera la lista de las asignaturas programadas para un año académico", tags=["Programación"])
async def programacion_asignatura_lista(ano_academ: int, id_usuario: int):
    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    programaciones: List[ProgramacionAsignatura] = []
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return programaciones
    # Perfil docente no debe ver nada
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return programaciones

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        # Determinamos la carrera del usuario
        dicc = await perfil_cod_carrera(id_usuario)
        cod_carrera = dicc["cod_carrera"]

        query = " \
            select pa.ano_academ as ano_academ, \
                pa.cod_periodo_academ as cod_periodo_academ, \
                pa.sigla as sigla, \
                pa.seccion as seccion, \
                a.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                a.nom_asign as nom_asign, \
                per.nom_periodo_academ as nom_periodo_academ \
            from prog_asign pa \
                join periodo_academ per on pa.cod_periodo_academ = per.cod_periodo_academ \
                join asign a on pa.sigla = a.sigla \
                join carrera c on a.cod_carrera = c.cod_carrera \
            where pa.ano_academ = %s and \
                a.cod_carrera = %s \
            order by pa.cod_periodo_academ asc, \
                a.cod_carrera asc, \
                pa.sigla asc, \
                pa.seccion asc"

        db = await get_db_connection()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

        try:
            values = (ano_academ, cod_carrera)
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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DB error {error_message}")

        finally:
            db.close()

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value:
        query = " \
            select pa.ano_academ as ano_academ, \
                pa.cod_periodo_academ as cod_periodo_academ, \
                pa.sigla as sigla, \
                pa.seccion as seccion, \
                a.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                a.nom_asign as nom_asign, \
                per.nom_periodo_academ as nom_periodo_academ \
            from prog_asign pa \
                join periodo_academ per on pa.cod_periodo_academ = per.cod_periodo_academ \
                join asign a on pa.sigla = a.sigla \
                join carrera c on a.cod_carrera = c.cod_carrera \
            where pa.ano_academ = %s \
            order by a.cod_carrera asc, \
                pa.cod_periodo_academ asc, \
                a.cod_carrera asc, \
                pa.sigla asc, \
                pa.seccion asc"

        db = await get_db_connection()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

        try:
            values = (ano_academ)
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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DB error {error_message}")

        finally:
            db.close()

    # Armamos el diccionario de salida
    programacion: ProgramacionAsignatura = None
    for row in result:
        programacion = ProgramacionAsignatura(ano_academ=row[0],
                                              cod_periodo_academ=row[1],
                                              sigla=row[2],
                                              seccion=row[3],
                                              cod_carrera=row[4],
                                              nom_carrera=row[5],
                                              nom_asignatura=row[6],
                                              nom_periodo_academ=row[7])

        programaciones.append(programacion)

    return programaciones


@router.delete("/api/programacion/eliminar/ano_academ/{ano_academ}/cod_periodo_academ/{cod_periodo_academ}/sigla/{sigla}/seccion/{seccion}/{id_usuario}", response_model=dict, summary="Elimina la programación de una sección específica de una asignatura para un año y período académico", tags=["Programación"])
async def asignatura_eliminar(ano_academ: int, cod_periodo_academ: int, sigla: str, seccion: int, id_usuario: int):

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
        query = "delete from prog_asign where ano_academ = %s and cod_periodo_academ = %s and sigla = %s and seccion = %s"

        values = (ano_academ, cod_periodo_academ, sigla, seccion)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            await db.commit()

            return {
                "ano_academ": ano_academ,
                "cod_periodo_academ": cod_periodo_academ,
                "sigla": sigla,
                "seccion": seccion,
                "eliminado": True,
                "msg_error": None
            }

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1451" in error_message:
            return {
                "ano_academ": ano_academ,
                "cod_periodo_academ": cod_periodo_academ,
                "sigla": sigla,
                "seccion": seccion,
                "eliminado": False,
                "msg_error": "Programación de asignatura no se puede eliminar por integridad de datos"
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
        "ano_academ": ano_academ,
        "cod_periodo_academ": cod_periodo_academ,
        "sigla": sigla,
        "seccion": seccion,
        "eliminado": True
    }


@router.post("/api/programacion/asignatura/ano_academ/periodo/seccion", response_model=ProgramacionAsignatura, summary="Agregar la programación de una sección para una asignatura en un período académico", tags=["Programación"])
async def taller_insertar(programacion: ProgramacionAsignatura) -> ProgramacionAsignatura:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            insert into prog_asign ( \
                ano_academ, \
                cod_periodo_academ, \
                sigla, \
                seccion) \
            values ( \
                %s, \
                %s, \
                %s, \
                %s)"
        values = (programacion.ano_academ,
                  programacion.cod_periodo_academ,
                  programacion.sigla,
                  programacion.seccion)
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

    return programacion


@router.get("/api/programacion/ano_academ/{ano_academ}/periodo/{cod_periodo_academ}/sigla/{sigla}/seccion/{seccion}/lista", summary="Recupera la lista de talleres programados para una asignatura", tags=["Programación"])
async def programacion_taller_lista(ano_academ: int, cod_periodo_academ: int, sigla: str, seccion: int):
    programaciones: List[ProgramacionTaller] = []

    query = " \
        select pt.fecha as fecha, \
            pt.ano_academ as ano_academ, \
            pt.cod_periodo_academ as cod_periodo_academ, \
            pt.sigla as sigla, \
            pt.seccion as seccion, \
            pt.id_taller as id_taller, \
            pt.id_usuario as usuario, \
            pa.nom_periodo_academ as nom_periodo_academ, \
            a.nom_asign as nom_asign, \
            t.titulo_preparacion as titulo_preparacion, \
            t.semana as semana, \
            u.login as login, \
            u.nom_preferido as nom_preferido, \
            u.primer_apellido as primer_apellido, \
            u.segundo_apellido as segundo_apellido \
        from prog_taller pt \
        join periodo_academ pa on pt.cod_periodo_academ = pa.cod_periodo_academ \
        join asign a on pt.sigla = a.sigla \
        left outer join taller t on pt.id_taller = t.id_taller \
        join usuario u on pt.id_usuario = u.id_usuario \
        where pt.ano_academ = %s and \
            pt.cod_periodo_academ = %s and \
            pt.sigla = %s and \
            pt.seccion = %s \
        order by pt.fecha asc, \
            t.semana asc"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = (ano_academ, cod_periodo_academ, sigla, seccion)
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DB error {error_message}")

    finally:
        db.close()

    # Armamos el diccionario de salida
    for row in result:
        fecha_str = str(row[0])  # Convertir a cadena de texto
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")  # Convertir a objeto datetime

        # Obtener el día del mes con ceros a la izquierda
        dia = fecha.strftime('%d')
        # Obtener el mes con ceros a la izquierda
        mes = fecha.strftime('%m')
        # Obtener el año
        ano = fecha.strftime('%Y')
        # Construir la cadena de formato deseada
        fecha_salida = f"{ano}-{mes}-{dia}"

        # Resto del código...
        programacion = ProgramacionTaller(fecha=fecha_salida,
                                          ano_academ=row[1],
                                          cod_periodo_academ=row[2],
                                          sigla=row[3],
                                          seccion=row[4],
                                          id_taller=row[5],
                                          id_usuario=row[6],
                                          nom_periodo_academ=row[7],
                                          nom_asignatura=row[8],
                                          titulo_preparacion=row[9],
                                          semana=row[10],
                                          login=row[11],
                                          nom_preferido=row[12],
                                          primer_apellido=row[13],
                                          segundo_apellido=row[14],)

        programaciones.append(programacion)

    return programaciones


@router.get("/api/programacion/ano_academ/{ano_academ}/periodo/{cod_periodo_academ}/sigla/{sigla}/seccion/{seccion}/taller/{id_taller}/fecha/{fecha}", summary="Recupera un taller específico programado para una asignatura", tags=["Programación"])
async def programacion_taller(ano_academ: int, cod_periodo_academ: int, sigla: str, seccion: int, id_taller: int, fecha: str):

    programacion: ProgramacionTaller = ProgramacionTaller(fecha=fecha,
                                                          ano_academ=ano_academ,
                                                          cod_periodo_academ=cod_periodo_academ,
                                                          sigla=sigla,
                                                          seccion=seccion,
                                                          id_taller=id_taller)

    try:
        fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        # Acciones a realizar si la fecha no es válida
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha ingresada no es válida")

    query = " \
        select pt.fecha as fecha, \
            pt.ano_academ as ano_academ, \
            pt.cod_periodo_academ as cod_periodo_academ, \
            pt.sigla as sigla, \
            pt.seccion as seccion, \
            pt.id_taller as id_taller, \
            pt.id_usuario as usuario, \
            pa.nom_periodo_academ as nom_periodo_academ, \
            a.nom_asign as nom_asign, \
            t.titulo_preparacion as titulo_preparacion, \
            t.semana as semana, \
            u.login as login, \
            u.nom_preferido as nom_preferido, \
            u.primer_apellido as primer_apellido, \
            u.segundo_apellido as segundo_apellido \
        from prog_taller pt \
        join periodo_academ pa on pt.cod_periodo_academ = pa.cod_periodo_academ \
        join asign a on pt.sigla = a.sigla \
        join taller t on pt.id_taller = t.id_taller \
        join usuario u on pt.id_usuario = u.id_usuario \
        where pt.ano_academ = %s and \
            pt.cod_periodo_academ = %s and \
            pt.sigla = %s and \
            pt.seccion = %s and \
            pt.id_taller = %s and \
            pt.fecha = %s"

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        values = (ano_academ, cod_periodo_academ, sigla, seccion, id_taller, fecha_objeto)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()

            if not result:
                return programacion

    except aiomysql.Error as e:
        error_message = str(e)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DB error {error_message}")

    finally:
        db.close()

    fecha_str = str(result[0])  # Convertir a cadena de texto
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")  # Convertir a objeto datetime

    # Obtener el día del mes con ceros a la izquierda
    dia = fecha.strftime('%d')
    # Obtener el mes con ceros a la izquierda
    mes = fecha.strftime('%m')
    # Obtener el año
    ano = fecha.strftime('%Y')
    # Construir la cadena de formato deseada
    fecha_salida = f"{ano}-{mes}-{dia}"

    programacion = ProgramacionTaller(fecha=fecha_salida,
                                      ano_academ=result[1],
                                      cod_periodo_academ=result[2],
                                      sigla=result[3],
                                      seccion=result[4],
                                      id_taller=result[5],
                                      id_usuario=result[6],
                                      nom_periodo_academ=result[7],
                                      nom_asignatura=result[8],
                                      titulo_preparacion=result[9],
                                      semana=result[10],
                                      login=result[11],
                                      nom_preferido=result[12],
                                      primer_apellido=result[13],
                                      segundo_apellido=result[14])

    return programacion


@router.delete("/api/programacion/eliminar/ano_academ/{ano_academ}/cod_periodo_academ/{cod_periodo_academ}/sigla/{sigla}/seccion/{seccion}/taller/{id_taller}/fecha/{fecha}/{id_usuario}", response_model=dict, summary="Elimina la programación de una sección específica de una asignatura para un año y período académico", tags=["Programación"])
async def taller_eliminar(ano_academ: int, cod_periodo_academ: int, sigla: str, seccion: int, id_taller: int, fecha: str, id_usuario: int):

    try:
        fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        # Acciones a realizar si la fecha no es válida
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha ingresada no es válida")

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
        query = "delete from prog_taller where ano_academ = %s and cod_periodo_academ = %s and sigla = %s and seccion = %s and id_taller = %s and fecha = %s"

        values = (ano_academ, cod_periodo_academ, sigla, seccion, id_taller, fecha_objeto)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            await db.commit()

            return {
                "ano_academ": ano_academ,
                "cod_periodo_academ": cod_periodo_academ,
                "sigla": sigla,
                "seccion": seccion,
                "id_taller": id_taller,
                "fecha": fecha,
                "eliminado": True,
                "msg_error": None
            }

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1451" in error_message:
            return {
                "ano_academ": ano_academ,
                "cod_periodo_academ": cod_periodo_academ,
                "sigla": sigla,
                "seccion": seccion,
                "id_taller": id_taller,
                "fecha": fecha,
                "eliminado": False,
                "msg_error": "Programación de asignatura no se puede eliminar por integridad de datos"
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
        "ano_academ": ano_academ,
        "cod_periodo_academ": cod_periodo_academ,
        "sigla": sigla,
        "seccion": seccion,
        "id_taller": id_taller,
        "fecha": fecha,
        "eliminado": True
    }


@router.put("/api/programacion/ano_academ/periodo/sigla/seccion/taller/fecha", response_model=ProgramacionTaller, summary="Modificar la programación de un taller específico", tags=["Programación"])
async def programacion_taller_update(programacion: ProgramacionTaller) -> ProgramacionTaller:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            update prog_taller \
                set id_usuario = %s \
            where fecha = %s and \
                ano_academ = %s and \
                cod_periodo_academ = %s and \
                sigla = %s and \
                seccion = %s and \
                id_taller = %s"
        values = (programacion.id_usuario,
                  programacion.fecha,
                  programacion.ano_academ,
                  programacion.cod_periodo_academ,
                  programacion.sigla,
                  programacion.seccion,
                  programacion.id_taller)
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

    return programacion


@router.post("/api/programacion/asignatura/ano_academ/periodo/seccion/taller/fecha", response_model=ProgramacionTaller, summary="Agregar la programación de un taller para una asignatura en un período académico para una fecha ", tags=["Programación"])
async def programacion_taller_insertar(programacion: ProgramacionTaller) -> ProgramacionTaller:

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            insert into prog_taller ( \
                fecha, \
                ano_academ, \
                cod_periodo_academ, \
                sigla, \
                seccion, \
                id_taller, \
                id_usuario) \
            values ( \
                %s, \
                %s, \
                %s, \
                %s, \
                %s, \
                %s, \
                %s)"
        values = (programacion.fecha,
                  programacion.ano_academ,
                  programacion.cod_periodo_academ,
                  programacion.sigla,
                  programacion.seccion,
                  programacion.id_taller,
                  programacion.id_usuario)
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

    return programacion
