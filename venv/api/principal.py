
from typing import List
import fastapi
from models.principal import Resumen
from models.principal import Dashboard
from api.perfil import perfil_usuario
from api.perfil import perfil_cod_carrera
from api.param import param_ano_academ_valor

from fastapi import HTTPException
from fastapi import status
import aiomysql

from database import get_db_connection
from infrastructure.constants import Const

router = fastapi.APIRouter()


@router.get("/api/principal/{id_usuario}", summary="Obtiene los dashboards para presentar en la página principal", tags=["Principal"])
async def principal(id_usuario: int):
    nom_carrera: str = None
    nom_ultima_carrera: str = None
    resumen: Resumen = None
    dashboard: Dashboard = None
    resumenes: List[Resumen] = []
    principal: List[Dashboard] = []

    # Determinamos el perfil del usuario para determinar qué información puede ver
    perfil = await perfil_usuario(id_usuario)
    # Si todo está correcto, Retornamos la respuesta de la API
    if not perfil:
        return principal

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_TI.value or perfil.cod_perfil == Const.K_JEFE_BODEGA.value:
        query = " \
            select c.nom_carrera as nom_carrera, \
                'Cantidad de asignaturas' as concepto, \
                count(*) as valor \
            from asign a \
            join carrera c on a.cod_carrera = c.cod_carrera \
            group by c.nom_carrera \
            union \
            select c.nom_carrera as nom_carrera, \
                'Cantidad de talleres' as concepto, \
                count(*) as valor \
            from taller t \
            join asign a on t.sigla = a.sigla \
            join carrera c on a.cod_carrera = c.cod_carrera \
            group by c.nom_carrera \
            union \
            select c.nom_carrera as nom_carrera, \
                'Cantidad de productos' as concepto, \
                count(distinct ct.id_producto) as valor \
            from config_taller ct \
            join taller t on ct.id_taller = t.id_taller \
            join asign a on t.sigla = a.sigla \
            join carrera c on a.cod_carrera = c.cod_carrera \
            group by c.nom_carrera \
            union \
            select c.nom_carrera as nom_carrera, \
                'Cantidad de docentes' as concepto, \
                count(*) as valor \
            from usuario u \
            join carrera c on u.cod_carrera = c.cod_carrera \
            where u.cod_perfil = 2 \
            group by c.nom_carrera \
            order by nom_carrera asc"

        try:
            values = ()
            async with db.cursor() as cursor:
                await cursor.execute(query, values)
                result = await cursor.fetchall()

        except aiomysql.Error as e:
            error_message = str(e)
            print(error_message)
            if "Connection" in error_message:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}.")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}.")

        except Exception as e:
            error_message = str(e)
            print(error_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. {error_message}")

        finally:
            db.close()

    if perfil.cod_perfil == Const.K_ADMINISTRADOR_CARRERA.value:
        # Determinamos la carrera del usuario
        dicc = await perfil_cod_carrera(id_usuario)
        cod_carrera = dicc["cod_carrera"]

        query = " \
            select c.nom_carrera as nom_carrera, \
                'Cantidad de asignaturas' as concepto, \
                count(*) as valor \
            from asign a \
            join carrera c on a.cod_carrera = c.cod_carrera \
            where c.cod_carrera = %s \
            union \
            select c.nom_carrera as nom_carrera, \
                'Cantidad de talleres' as concepto, \
                count(*) as valor \
            from taller t \
            join asign a on t.sigla = a.sigla \
            join carrera c on a.cod_carrera = c.cod_carrera \
            where c.cod_carrera = %s \
            union \
            select c.nom_carrera as nom_carrera, \
                'Cantidad de productos' as concepto, \
                count(distinct ct.id_producto) as valor \
            from config_taller ct \
            join taller t on ct.id_taller = t.id_taller \
            join asign a on t.sigla = a.sigla \
            join carrera c on a.cod_carrera = c.cod_carrera \
            where c.cod_carrera = %s \
            union \
            select c.nom_carrera as nom_carrera, \
                'Cantidad de docentes' as concepto, \
                count(*) as valor \
            from usuario u \
            join carrera c on u.cod_carrera = c.cod_carrera \
            where u.cod_perfil = 2 and \
                c.cod_carrera = %s"

        try:
            values = (cod_carrera, cod_carrera, cod_carrera, cod_carrera)
            async with db.cursor() as cursor:
                await cursor.execute(query, values)
                result = await cursor.fetchall()

        except aiomysql.Error as e:
            error_message = str(e)
            print(error_message)
            if "Connection" in error_message:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}.")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}.")

        except Exception as e:
            error_message = str(e)
            print(error_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. {error_message}")

        finally:
            db.close()

    if perfil.cod_perfil == Const.K_DOCENTE.value:

        # Determinamos el año académico vigente
        dicc = await param_ano_academ_valor()
        ano_academ = dicc["ano_academ"]

        query = " \
            select (select carr.nom_carrera \
		            from carrera carr \
		            join usuario usu on carr.cod_carrera = usu.cod_carrera and \
			        usu.id_usuario = %s) as nom_carrera, \
                'Cantidad de talleres asignados' as concepto, \
                count(*) as valor \
            from prog_taller pt \
            join usuario u on pt.id_usuario = u.id_usuario \
            join carrera c on u.cod_carrera = c.cod_carrera \
            where pt.id_usuario = %s and \
                pt.ano_academ = %s \
            union \
            select (select carr.nom_carrera \
		            from carrera carr \
		            join usuario usu on carr.cod_carrera = usu.cod_carrera and \
			        usu.id_usuario = %s) as nom_carrera, \
                'Cantidad de talleres registrados' as concepto, \
                count(*) as valor \
            from regis_taller rt \
            join usuario u on rt.id_usuario = u.id_usuario \
            join carrera c on u.cod_carrera = c.cod_carrera \
            where rt.id_usuario = %s and \
                rt.ano_academ = %s"

        try:
            values = (id_usuario, id_usuario, ano_academ, id_usuario, id_usuario, ano_academ)
            async with db.cursor() as cursor:
                await cursor.execute(query, values)
                result = await cursor.fetchall()

        except aiomysql.Error as e:
            error_message = str(e)
            print(error_message)
            if "Connection" in error_message:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}.")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}.")

        except Exception as e:
            error_message = str(e)
            print(error_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos. {error_message}")

        finally:
            db.close()

    # Armamos la colección de salida
    for row in result:
        nom_carrera = row[0]

        if nom_carrera != nom_ultima_carrera:
            resumen = {"concepto": row[1],
                       "valor": row[2]}
            resumenes = []
            resumenes.append(resumen)
            dashboard = Dashboard(nom_carrera, resumenes)
            principal.append(dashboard)
        else:
            resumen = {"concepto": row[1],
                       "valor": row[2]}
            resumenes.append(resumen)

        nom_ultima_carrera = nom_carrera

    return principal
