
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from typing import List
from api.perfil import perfil_usuario
from models.consultas import RegistroConsultaValorizacionTaller
from models.consultas import RegistroConsultaPresupuestoEstimadoAsignatura
from models.consultas import RegistroConsultaAsignacionRegistroTalleresDocente
from models.consultas import RegistroConsultaResumenProductoRangoFechas
from models.consultas import RegistroConsultaDetalleProductoTallerRangoFechas
from database import get_db_connection
from datetime import date
from infrastructure.constants import Const

router = fastapi.APIRouter()


@router.get("/api/consulta/1/{id_usuario}", response_model=List[RegistroConsultaValorizacionTaller], summary="Datos de consulta de valorización por taller", tags=["Consultas"])
async def consulta_valorizacion_taller(id_usuario: int):
    registro: RegistroConsultaValorizacionTaller = None
    registros: List[RegistroConsultaValorizacionTaller] = []

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return registros
    # Perfil docente no debe tener acceso a listados
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return registros

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value:
        query = " \
            select c.nom_carrera as nom_carrera, \
                a.sigla as sigla, \
                a.nom_asign as nom_asign, \
                t.semana as semana, \
                min(t.id_taller) as id_taller, \
                t.titulo_preparacion as titulo_preparacion, \
                sum(round(p.precio * ct.cantidad, 0)) as total_taller \
            from asign a \
            join taller t on t.sigla = a.sigla \
            join config_taller ct on t.id_taller = ct.id_taller \
            join producto p on ct.id_producto = p.id_producto \
            join carrera c on a.cod_carrera = c.cod_carrera \
            group by c.nom_carrera, \
                a.sigla, \
                a.nom_asign, \
                t.semana, \
                t.titulo_preparacion \
            order by c.cod_carrera asc, \
                a.sigla asc, \
                t.semana asc"
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

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        query = " \
            select c.nom_carrera as nom_carrera, \
                a.sigla as sigla, \
                a.nom_asign as nom_asign, \
                t.semana as semana, \
                min(t.id_taller) as id_taller, \
                t.titulo_preparacion as titulo_preparacion, \
                sum(round(p.precio * ct.cantidad, 0)) as total_taller \
            from asign a \
            join taller t on t.sigla = a.sigla \
            join config_taller ct on t.id_taller = ct.id_taller \
            join producto p on ct.id_producto = p.id_producto \
            join carrera c on a.cod_carrera = c.cod_carrera \
            join usuario u on a.cod_carrera = u.cod_carrera \
            where u.id_usuario = %s \
            group by c.nom_carrera, \
                a.sigla, \
                a.nom_asign, \
                t.semana, \
                t.titulo_preparacion \
            order by c.cod_carrera asc, \
                a.sigla asc, \
                t.semana asc"
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
    for row in result:
        registro = RegistroConsultaValorizacionTaller(nom_carrera=row[0],
                                                      sigla=row[1],
                                                      nom_asign=row[2],
                                                      semana=row[3],
                                                      id_taller=row[4],
                                                      titulo_preparacion=row[5],
                                                      total_taller=row[6],)
        registros.append(registro)

    return registros


@router.get("/api/consulta/2/ano_academ/{ano_academ}/{id_usuario}", response_model=List[RegistroConsultaPresupuestoEstimadoAsignatura], summary="Datos de consulta de presupuesto estimado por asignatura para un año académico", tags=["Consultas"])
async def consulta_presupuesto_estimado_asignatura(ano_academ: int, id_usuario: int):
    registro: RegistroConsultaPresupuestoEstimadoAsignatura = None
    registros: List[RegistroConsultaPresupuestoEstimadoAsignatura] = []

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return registros
    # Perfil docente no debe tener acceso a listados
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return registros

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value:
        query = " \
            select c.nom_carrera as nom_carrera, \
                pa.sigla as sigla, \
                a.nom_asign as nom_asign, \
                count(pa.seccion) as total_seccion, \
                (select sum(round(pr.precio * cota.cantidad, 0)) \
                    from config_taller cota \
                    join producto pr on cota.id_producto = pr.id_producto \
                    join taller ta on cota.id_taller = ta.id_taller \
                    where ta.sigla = pa.sigla) as total_asign, \
                (count(pa.seccion) * (select sum(round(pr.precio * cota.cantidad, 0)) as total_taller \
                                        from config_taller cota \
                                        join producto pr on cota.id_producto = pr.id_producto \
                                        join taller ta on cota.id_taller = ta.id_taller \
                                        where ta.sigla = pa.sigla)) as total \
            from prog_asign pa \
            join asign a on pa.sigla = a.sigla \
            join carrera c on a.cod_carrera = c.cod_carrera \
            where pa.ano_academ = %s \
            group by pa.sigla \
            order by c.cod_carrera asc, \
                a.sigla asc"
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

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        query = " \
            select c.nom_carrera as nom_carrera, \
                pa.sigla as sigla, \
                a.nom_asign as nom_asign, \
                count(pa.seccion) as total_seccion, \
                (select sum(round(pr.precio * cota.cantidad, 0)) \
                    from config_taller cota \
                    join producto pr on cota.id_producto = pr.id_producto \
                    join taller ta on cota.id_taller = ta.id_taller \
                    where ta.sigla = pa.sigla) as total_asign, \
                (count(pa.seccion) * (select sum(round(pr.precio * cota.cantidad, 0)) as total_taller \
                                        from config_taller cota \
                                        join producto pr on cota.id_producto = pr.id_producto \
                                        join taller ta on cota.id_taller = ta.id_taller \
                                        where ta.sigla = pa.sigla)) as total \
            from prog_asign pa \
            join asign a on pa.sigla = a.sigla \
            join carrera c on a.cod_carrera = c.cod_carrera \
            join usuario u on c.cod_carrera = u.cod_carrera \
            where pa.ano_academ = %s and \
                u.id_usuario = %s \
            group by pa.sigla \
            order by c.cod_carrera asc, \
                a.sigla asc"
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

    # Armamos el diccionario de salida
    for row in result:
        registro = RegistroConsultaPresupuestoEstimadoAsignatura(nom_carrera=row[0],
                                                                 sigla=row[1],
                                                                 nom_asign=row[2],
                                                                 total_seccion=row[3],
                                                                 total_asign=row[4],
                                                                 total=row[5],)
        registros.append(registro)

    return registros


@router.get("/api/consulta/3/ano_academ/{ano_academ}/{id_usuario}", response_model=List[RegistroConsultaAsignacionRegistroTalleresDocente], summary="Datos de consulta de asignación y registro de talleres de docentes para un año académico", tags=["Consultas"])
async def consulta_asignacion_registro_docentes(ano_academ: int, id_usuario: int):
    registro: RegistroConsultaAsignacionRegistroTalleresDocente = None
    registros: List[RegistroConsultaAsignacionRegistroTalleresDocente] = []

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return registros
    # Perfil docente no debe tener acceso a listados
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return registros

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value:
        query = f" \
            select c.nom_carrera as nom_carrera, \
                u.primer_apellido as primer_apellido, \
                u.segundo_apellido as segundo_apellido, \
                u.nom_preferido as nom_preferido, \
                (case \
                    when pt.sigla is not null then pt.sigla \
                    else '-' \
                    end) as sigla, \
                (case \
                    when pt.sigla is not null then a.nom_asign \
                    else '-' \
                    end) as nom_asign, \
                pt.seccion as seccion, \
                min(pt.cod_periodo_academ) as cod_periodo_academ, \
                (case \
                    when pt.sigla is not null then pa.nom_periodo_academ \
                    else '-' \
                    end) as nom_periodo_academ, \
                count(pt.id_taller) as total_taller_asignado, \
                count(rt.id_taller) as total_taller_registrado, \
                (case \
                    when pt.sigla is not null then 0 \
                    else 1 \
                    end) as orden_asignacion \
            from prog_taller pt \
            right outer join usuario u on pt.id_usuario = u.id_usuario \
            left outer join regis_taller rt on pt.fecha = rt.fecha and pt.ano_academ = rt.ano_academ and pt.cod_periodo_academ = rt.cod_periodo_academ and pt.sigla = rt.sigla and pt.seccion = rt.seccion and pt.id_taller = rt.id_taller and pt.id_usuario = rt.id_usuario \
            join carrera c on u.cod_carrera = c.cod_carrera \
            left outer join periodo_academ pa on pt.cod_periodo_academ = pa.cod_periodo_academ \
            left outer join asign a on pt.sigla = a.sigla \
            where (pt.ano_academ = %s or pt.ano_academ is null) and \
                u.cod_perfil = {Const.K_DOCENTE.value} \
            group by c.nom_carrera, \
                u.primer_apellido, \
                u.segundo_apellido, \
                u.nom_preferido, \
                pt.sigla, \
                a.nom_asign, \
                pt.seccion, \
                pa.nom_periodo_academ \
            order by c.nom_carrera asc, \
                orden_asignacion asc, \
                pt.sigla asc, \
                cod_periodo_academ asc, \
                u.primer_apellido asc, \
                u.segundo_apellido asc, \
                u.nom_preferido asc"
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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

        finally:
            db.close()

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        query = f" \
            select c.nom_carrera as nom_carrera, \
                u.primer_apellido as primer_apellido, \
                u.segundo_apellido as segundo_apellido, \
                u.nom_preferido as nom_preferido, \
                (case \
                    when pt.sigla is not null then pt.sigla \
                    else '-' \
                    end) as sigla, \
                (case \
                    when pt.sigla is not null then a.nom_asign \
                    else '-' \
                    end) as nom_asign, \
                pt.seccion as seccion, \
                min(pt.cod_periodo_academ) as cod_periodo_academ, \
                (case \
                    when pt.sigla is not null then pa.nom_periodo_academ \
                    else '-' \
                    end) as nom_periodo_academ, \
                count(pt.id_taller) as total_taller_asignado, \
                count(rt.id_taller) as total_taller_registrado, \
                (case \
                    when pt.sigla is not null then 0 \
                    else 1 \
                    end) as orden_asignacion \
            from prog_taller pt \
            right outer join usuario u on pt.id_usuario = u.id_usuario \
            left outer join regis_taller rt on pt.fecha = rt.fecha and pt.ano_academ = rt.ano_academ and pt.cod_periodo_academ = rt.cod_periodo_academ and pt.sigla = rt.sigla and pt.seccion = rt.seccion and pt.id_taller = rt.id_taller and pt.id_usuario = rt.id_usuario \
            join carrera c on u.cod_carrera = c.cod_carrera \
            left outer join periodo_academ pa on pt.cod_periodo_academ = pa.cod_periodo_academ \
            left outer join asign a on pt.sigla = a.sigla \
            where (pt.ano_academ = %s or pt.ano_academ is null) and \
                u.cod_perfil = {Const.K_DOCENTE.value} and \
                u.cod_carrera = (select us.cod_carrera from usuario us where us.id_usuario = %s) \
            group by c.nom_carrera, \
                u.primer_apellido, \
                u.segundo_apellido, \
                u.nom_preferido, \
                pt.sigla, \
                a.nom_asign, \
                pt.seccion, \
                pa.nom_periodo_academ \
            order by c.nom_carrera asc, \
                orden_asignacion asc, \
                pt.sigla asc, \
                nom_periodo_academ asc, \
                u.primer_apellido asc, \
                u.segundo_apellido asc, \
                u.nom_preferido asc"
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

        except Exception as e:
            error_message = str(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

        finally:
            db.close()

    # Armamos el diccionario de salida
    for row in result:
        registro = RegistroConsultaAsignacionRegistroTalleresDocente(nom_carrera=row[0],
                                                                     primer_apellido=row[1],
                                                                     segundo_apellido=row[2],
                                                                     nom_preferido=row[3],
                                                                     sigla=row[4],
                                                                     nom_asign=row[5],
                                                                     seccion=row[6],
                                                                     cod_periodo_academ=row[7],
                                                                     nom_periodo_academ=row[8],
                                                                     total_taller_asignado=row[9],
                                                                     total_taller_registrado=row[10],)
        registros.append(registro)

    return registros


@router.get("/api/consulta/4/ano_academ/{ano_academ}/fecha_inicio/{fecha_inicio}/fecha_termino/{fecha_termino}/{id_usuario}", response_model=List[RegistroConsultaResumenProductoRangoFechas], summary="Resumen de productos por rango de fechas", tags=["Consultas"])
async def consulta_resumen_producto_periodo(ano_academ: int, fecha_inicio: date, fecha_termino: date, id_usuario: int):
    registro: RegistroConsultaResumenProductoRangoFechas = None
    registros: List[RegistroConsultaResumenProductoRangoFechas] = []

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return registros
    # Perfil docente no debe tener acceso a listados
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return registros

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value or perfil.cod_perfil == Const.K_JEFE_BODEGA.value:
        query = " \
            select c.nom_carrera as nom_carrera, \
                cp.nom_categ_producto as nom_categ_producto, \
                p.nom_producto as nom_producto, \
                sum(ct.cantidad) as cantidad_total_productos, \
                um.nom_unidad_medida as nom_unidad_medida, \
                p.precio as precio_producto, \
                round(sum(ct.cantidad) * p.precio, 0) as precio_total_productos \
            from prog_taller pt \
            join config_taller ct on pt.id_taller = ct.id_taller \
            join producto p on ct.id_producto = p.id_producto \
            join unidad_medida um on p.cod_unidad_medida = um.cod_unidad_medida \
            join categ_producto cp on p.cod_categ_producto = cp.cod_categ_producto \
            join asign a on pt.sigla = a.sigla \
            join carrera c on a.cod_carrera = c.cod_carrera \
            where pt.ano_academ = %s and \
                pt.fecha between %s and %s \
            group by c.nom_carrera,\
                cp.nom_categ_producto, \
                ct.id_producto, \
                p.nom_producto, \
                p.precio, \
                um.nom_unidad_medida \
            order by c.nom_carrera asc, \
                cp.nom_categ_producto asc, \
                p.nom_producto asc"
        db = await get_db_connection()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

        try:
            values = (ano_academ, fecha_inicio, fecha_termino)
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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

        finally:
            db.close()

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        query = " \
            select c.nom_carrera as nom_carrera, \
                cp.nom_categ_producto as nom_categ_producto, \
                p.nom_producto as nom_producto, \
                sum(ct.cantidad) as cantidad_total_productos, \
                um.nom_unidad_medida as nom_unidad_medida, \
                p.precio as precio_producto, \
                round(sum(ct.cantidad) * p.precio, 0) as precio_total_productos \
            from prog_taller pt \
            join config_taller ct on pt.id_taller = ct.id_taller \
            join producto p on ct.id_producto = p.id_producto \
            join unidad_medida um on p.cod_unidad_medida = um.cod_unidad_medida \
            join categ_producto cp on p.cod_categ_producto = cp.cod_categ_producto \
            join asign a on pt.sigla = a.sigla \
            join usuario u on a.cod_carrera = u.cod_carrera \
            join carrera c on a.cod_carrera = c.cod_carrera \
            where pt.ano_academ = %s and \
                u.id_usuario = %s and \
                pt.fecha between %s and %s \
            group by c.nom_carrera, \
                cp.nom_categ_producto, \
                ct.id_producto, \
                p.nom_producto, \
                p.precio, \
                um.nom_unidad_medida \
            order by c.nom_carrera asc, \
                cp.nom_categ_producto asc, \
                p.nom_producto asc"
        db = await get_db_connection()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

        try:
            values = (ano_academ, id_usuario, fecha_inicio, fecha_termino)
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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

        finally:
            db.close()

    # Armamos el diccionario de salida
    for row in result:
        registro = RegistroConsultaResumenProductoRangoFechas(nom_carrera = row[0],
                                                              nom_categ_producto = row[1],
                                                              nom_producto = row[2],
                                                              cantidad_total_productos = row[3],
                                                              nom_unidad_medida = row[4],
                                                              precio_producto = row[5],
                                                              precio_total_productos = row[6],)
        registros.append(registro)

    return registros


@router.get("/api/consulta/5/ano_academ/{ano_academ}/fecha_inicio/{fecha_inicio}/fecha_termino/{fecha_termino}/{id_usuario}", response_model=List[RegistroConsultaDetalleProductoTallerRangoFechas], summary="Detalle de productos por taller y por rango de fechas", tags=["Consultas"])
async def consulta_detalle_producto_taller_periodo(ano_academ: int, fecha_inicio: date, fecha_termino: date, id_usuario: int):
    registro: RegistroConsultaDetalleProductoTallerRangoFechas = None
    registros: List[RegistroConsultaDetalleProductoTallerRangoFechas] = []

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return registros
    # Perfil docente no debe tener acceso a listados
    if perfil.cod_perfil == Const.K_DOCENTE.value:
        return registros

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value or perfil.cod_perfil == Const.K_JEFE_BODEGA.value:
        query = " \
            select c.nom_carrera, \
                cp.nom_categ_producto as nom_categ_producto, \
                p.nom_producto as nom_producto, \
                ct.cantidad as cantidad, \
                um.nom_unidad_medida as nom_unidad_medida, \
                p.precio as precio, \
                (ct.cantidad * p.precio) as precio_total, \
                pt.fecha as fecha, \
                pa.nom_periodo_academ as nom_periodo_academ, \
                pt.sigla as sigla, \
                a.nom_asign as nom_asign, \
                pt.seccion as seccion, \
                t.semana as semana, \
                t.titulo_preparacion as titulo_preparacion \
            from prog_taller pt \
            join asign a on pt.sigla = a.sigla \
            join config_taller ct on pt.id_taller = ct.id_taller \
            join taller t on pt.id_taller = t.id_taller \
            join producto p on ct.id_producto = p.id_producto \
            join unidad_medida um on p.cod_unidad_medida = um.cod_unidad_medida \
            join categ_producto cp on p.cod_categ_producto = cp.cod_categ_producto \
            join carrera c on a.cod_carrera = c.cod_carrera \
            join periodo_academ pa on pt.cod_periodo_academ = pa.cod_periodo_academ \
            where pt.ano_academ = %s and \
                pt.fecha between %s and %s \
            order by c.nom_carrera asc, \
                cp.nom_categ_producto asc, \
                p.nom_producto asc, \
                pt.sigla asc, \
                pt.seccion asc, \
                t.semana asc, \
                pt.fecha asc"
        db = await get_db_connection()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

        try:
            values = (ano_academ, fecha_inicio, fecha_termino)
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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

        finally:
            db.close()

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        query = " \
            select c.nom_carrera, \
                cp.nom_categ_producto as nom_categ_producto, \
                p.nom_producto as nom_producto, \
                ct.cantidad as cantidad, \
                um.nom_unidad_medida as nom_unidad_medida, \
                p.precio as precio, \
                (ct.cantidad * p.precio) as precio_total, \
                pt.fecha as fecha, \
                pa.nom_periodo_academ as nom_periodo_academ, \
                pt.sigla as sigla, \
                a.nom_asign as nom_asign, \
                pt.seccion as seccion, \
                t.semana as semana, \
                t.titulo_preparacion as titulo_preparacion \
            from prog_taller pt \
            join asign a on pt.sigla = a.sigla \
            join config_taller ct on pt.id_taller = ct.id_taller \
            join taller t on pt.id_taller = t.id_taller \
            join producto p on ct.id_producto = p.id_producto \
            join unidad_medida um on p.cod_unidad_medida = um.cod_unidad_medida \
            join categ_producto cp on p.cod_categ_producto = cp.cod_categ_producto \
            join carrera c on a.cod_carrera = c.cod_carrera \
            join usuario u on a.cod_carrera = u.cod_carrera \
            join periodo_academ pa on pt.cod_periodo_academ = pa.cod_periodo_academ \
            where pt.ano_academ = %s and \
                u.id_usuario = %s and \
                pt.fecha between %s and %s \
            order by c.nom_carrera asc, \
                cp.nom_categ_producto asc, \
                p.nom_producto asc, \
                pt.sigla asc, \
                pt.seccion asc, \
                t.semana asc, \
                pt.fecha asc"
        db = await get_db_connection()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

        try:
            values = (ano_academ, id_usuario, fecha_inicio, fecha_termino)
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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. DBError {error_message}")

        finally:
            db.close()

    # Armamos el diccionario de salida
    for row in result:
        registro = RegistroConsultaDetalleProductoTallerRangoFechas(nom_carrera = row[0],
                                                            nom_categ_producto = row[1],
                                                            nom_producto = row[2],
                                                            cantidad = row[3],
                                                            nom_unidad_medida = row[4],
                                                            precio = row[5],
                                                            precio_total = row[6],
                                                            fecha = row[7],
                                                            nom_periodo_academ = row[8],
                                                            sigla = row[9],
                                                            nom_asign = row[10],
                                                            seccion = row[11],
                                                            semana = row[12],
                                                            titulo_preparacion = row[13],)

        registros.append(registro)

    return registros
