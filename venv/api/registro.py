
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from models.programacion_asignatura import ProgramacionAsignatura
from models.registro_taller import RegistroTaller
from database import get_db_connection
from api.perfil import perfil_usuario
from infrastructure.constants import Const
from datetime import datetime

router = fastapi.APIRouter()


@router.get("/api/registro/asignatura/ano_academ/{ano_academ}/docente/{id_usuario}/lista", summary="Recupera la lista de asignaturas asignadas a un docente específico para un año académico", tags=["Registro"])
async def registro_asignaturas(ano_academ: int, id_usuario: int):

    programaciones: List[ProgramacionAsignatura] = []    

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return programaciones

    if perfil.cod_perfil == Const.K_DOCENTE.value:
        query = " \
            select distinct pa.ano_academ as ano_academ, \
                pa.cod_periodo_academ as cod_periodo_academ, \
                pa.sigla as sigla, \
                pa.seccion as seccion, \
                a.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                a.nom_asign as nom_asign, \
                peracadem.nom_periodo_academ as nom_periodo_academ \
            from prog_asign pa \
            join prog_taller pt on pa.ano_academ = pt.ano_academ and pa.cod_periodo_academ = pt.cod_periodo_academ and pa.sigla = pt.sigla and pa.seccion = pt.seccion \
            join asign a on pa.sigla = a.sigla \
            join carrera c on a.cod_carrera = c.cod_carrera \
            join periodo_academ peracadem on pa.cod_periodo_academ = peracadem.cod_periodo_academ \
            where pa.ano_academ = %s and \
                pt.id_usuario = %s \
            order by cod_periodo_academ asc, \
                sigla asc, \
                seccion asc"

        db = await get_db_connection()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

        try:
            values = (ano_academ, id_usuario)
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

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        query = " \
            select distinct pa.ano_academ as ano_academ, \
                pa.cod_periodo_academ as cod_periodo_academ, \
                pa.sigla as sigla, \
                pa.seccion as seccion, \
                a.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                a.nom_asign as nom_asign, \
                peracadem.nom_periodo_academ as nom_periodo_academ \
            from prog_asign pa \
            join prog_taller pt on pa.ano_academ = pt.ano_academ and pa.cod_periodo_academ = pt.cod_periodo_academ and pa.sigla = pt.sigla and pa.seccion = pt.seccion \
            join asign a on pa.sigla = a.sigla \
            join usuario u on a.cod_carrera = u.cod_carrera \
            join carrera c on a.cod_carrera = c.cod_carrera \
            join periodo_academ peracadem on pa.cod_periodo_academ = peracadem.cod_periodo_academ \
            where pa.ano_academ = %s and \
                u.id_usuario = %s \
            order by cod_periodo_academ asc, \
                sigla asc, \
                seccion asc"

        db = await get_db_connection()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

        try:
            values = (ano_academ, id_usuario)
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

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value:
        query = " \
            select distinct pa.ano_academ as ano_academ, \
                pa.cod_periodo_academ as cod_periodo_academ, \
                pa.sigla as sigla, \
                pa.seccion as seccion, \
                a.cod_carrera as cod_carrera, \
                c.nom_carrera as nom_carrera, \
                a.nom_asign as nom_asign, \
                peracadem.nom_periodo_academ as nom_periodo_academ \
            from prog_asign pa \
            join prog_taller pt on pa.ano_academ = pt.ano_academ and pa.cod_periodo_academ = pt.cod_periodo_academ and pa.sigla = pt.sigla and pa.seccion = pt.seccion \
            join asign a on pa.sigla = a.sigla \
            join usuario u on a.cod_carrera = u.cod_carrera \
            join carrera c on a.cod_carrera = c.cod_carrera \
            join periodo_academ peracadem on pa.cod_periodo_academ = peracadem.cod_periodo_academ \
            where pa.ano_academ = %s \
            order by cod_periodo_academ asc, \
                sigla asc, \
                seccion asc"

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

        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

        finally:
            db.close()

    # Armamos el diccionario de salida
    programacion: ProgramacionAsignatura = None
    programaciones: List[ProgramacionAsignatura] = []
    for row in result:
        programacion = ProgramacionAsignatura(ano_academ=row[0],
                                              cod_periodo_academ=row[1],
                                              sigla=row[2],
                                              seccion=row[3],
                                              cod_carrera=row[4],
                                              nom_carrera=row[5],
                                              nom_asignatura=row[6],
                                              nom_periodo_academ=row[7],)
        programaciones.append(programacion)

    return programaciones


@router.get("/api/registro/asignatura/ano_academ/{ano_academ}/periodo/{cod_periodo_academ}/asignatura/{sigla}/seccion/{seccion}/docente/{id_usuario}/lista", summary="Recupera la lista de talleres de una asignatura programada para un docente específic", tags=["Registro"])
async def registro_talleres(ano_academ: int, cod_periodo_academ: int, sigla: str, seccion: int, id_usuario: int):

    query = " \
        select pt.fecha as fecha, \
            pt.ano_academ as ano_academ, \
            pt.cod_periodo_academ as cod_periodo_academ, \
            pt.sigla as sigla, \
            pt.seccion, \
            pt.id_taller as id_taller, \
            pt.id_usuario as id_usuario, \
            peracadem.nom_periodo_academ as nom_periodo_academ, \
            a.nom_asign as nom_asign, \
            t.titulo_preparacion as titulo_preparacion, \
            t.semana as semana, \
            u.login as login, \
            u.nom_preferido as nom_preferido, \
            u.primer_apellido as primer_apellido, \
            u.segundo_apellido as segundo_apellido, \
            (case \
                when pt.id_usuario = %s then 0 \
                else 1 \
                end) as indicador_usuario, \
            (select count(*) \
            from regis_taller rt \
            where rt.fecha = pt.fecha and \
                    rt.ano_academ = pt.ano_academ and \
                    rt.cod_periodo_academ = pt.cod_periodo_academ and \
                    rt.sigla = pt.sigla and \
                    rt.seccion = pt.seccion and \
                    rt.id_taller = pt.id_taller) as indicador_registro, \
            (case \
				when rt.obs is null then '(Taller pendiente registro)' \
                else rt.obs \
                end) as obs \
        from prog_taller pt \
        join taller t on pt.id_taller = t.id_taller \
        join usuario u on pt.id_usuario = u.id_usuario \
        join periodo_academ peracadem on pt.cod_periodo_academ = peracadem.cod_periodo_academ \
        join asign a on pt.sigla = a.sigla \
        left outer join regis_taller rt on pt.ano_academ = rt.ano_academ and pt.cod_periodo_academ = rt.cod_periodo_academ and pt.sigla = rt.sigla and pt.seccion = rt.seccion and pt.id_taller = rt.id_taller \
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
        values = (id_usuario, ano_academ, cod_periodo_academ, sigla, seccion)
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
    registro: RegistroTaller = None
    registros: List[RegistroTaller] = []
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

        registro = RegistroTaller(fecha=fecha_salida,
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
                                  segundo_apellido=row[14],
                                  indicador_usuario=row[15],
                                  indicador_registro=row[16],
                                  obs=row[17],)
        registros.append(registro)

    return registros


@router.post("/api/registro/taller", response_model=RegistroTaller, summary="Registrar la ejecución de un taller específico", tags=["Registro"])
async def registro_taller(registro: RegistroTaller) -> RegistroTaller:

    try:
        fecha_objeto = datetime.strptime(registro.fecha, '%Y-%m-%d')
    except ValueError:
        # Acciones a realizar si la fecha no es válida
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha ingresada no es válida")

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    # Parte 1 - Insertar el registro en regis_taller
    try:
        query = " \
            insert into regis_taller ( \
                fecha, \
                ano_academ, \
                cod_periodo_academ, \
                sigla, \
                seccion, \
                id_taller, \
                id_usuario, \
                obs) \
            values ( \
                %s, \
                %s, \
                %s, \
                %s, \
                %s, \
                %s, \
                %s, \
                %s)"
        values = (fecha_objeto,
                  registro.ano_academ,
                  registro.cod_periodo_academ,
                  registro.sigla,
                  registro.seccion,
                  registro.id_taller,
                  registro.id_usuario,
                  registro.obs)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1062" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error. Registro existente. DBerror {error_message}")

        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    # Parte 2: Replicar registros de detalle con los productos a los precios actuales
    try:
        query = " \
            insert into det_regis_taller \
            select rt.fecha as fecha, \
                rt.ano_academ as ano_academ, \
                rt.cod_periodo_academ as cod_periodo_academ, \
                rt.sigla as sigla, \
                rt.seccion as seccion, \
                ct.id_producto as id_producto, \
                rt.id_taller as id_taller, \
                ct.cod_agrupador as cod_agrupador, \
                p.precio as precio, \
                ct.cantidad as cantidad \
            from regis_taller rt \
            join config_taller ct on ct.id_taller = rt.id_taller \
            join producto p on ct.id_producto = p.id_producto \
            where rt.fecha = %s and \
                rt.ano_academ = %s and \
                rt.cod_periodo_academ = %s and \
                rt.sigla = %s and \
                rt.seccion = %s and \
                rt.id_taller = %s"
        values = (fecha_objeto,
                  registro.ano_academ,
                  registro.cod_periodo_academ,
                  registro.sigla,
                  registro.seccion,
                  registro.id_taller)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)

    except aiomysql.Error as e:
        error_message = str(e)
        # Controlamos de manera especial el error de integridad de datos
        if "1062" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error. Registro existente. DBerror {error_message}")

        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

    finally:
        db.close()

    return registro
