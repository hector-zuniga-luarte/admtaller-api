
import fastapi
from fastapi import HTTPException
from fastapi import status
import aiomysql

from database import get_db_connection
from models.autenticacion import Autenticacion
from models.autenticacion import CambioPassword

router = fastapi.APIRouter()

@router.post("/api/autenticacion/", response_model=Autenticacion, summary="Autenticar un usuario y contraseña", tags=["Autenticación"])
async def autenticacion(autenticacion: Autenticacion) -> Autenticacion:
    db = await get_db_connection()

    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        autenticacion.login = autenticacion.login.strip()
        query = " \
            select id_usuario as id_usuario \
            from usuario \
            where login = %s and \
                hash_password = %s"
        values = (autenticacion.login, autenticacion.hash_password)

        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            result = await cursor.fetchone()

        if result:
            autenticacion.autenticado = True
        else:
            autenticacion.autenticado = False

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

    finally:
        db.close()

    autenticacion.hash_password = None

    return autenticacion


@router.put("/api/autenticacion/password", response_model=CambioPassword, summary="Cambiar la contraseña del usuario conectado", tags=["Autenticación"])
async def autenticacion_password(cambio_password: CambioPassword):
    nueva_password: str = cambio_password.nueva_password

    # Anulamos las contraseñas para no devolverlas en la respuesta
    cambio_password.nueva_password = None
    cambio_password.confirmacion_nueva_password = None

    db = await get_db_connection()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al conectar a la base de datos")

    try:
        query = " \
            update usuario \
            set hash_password = %s \
            where id_usuario = %s"
        values = (nueva_password, cambio_password.id_usuario)
        async with db.cursor() as cursor:
            await cursor.execute(query, values)
            affected_rows = cursor.rowcount

        if affected_rows > 0:
            cambio_password.modificada = True
        else:
            cambio_password.modificada = False

    except aiomysql.Error as e:
        error_message = str(e)
        print(error_message)
        if "Connection" in error_message:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al conectar a la base de datos. DBerror {error_message}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la consulta a la base de datos. DBerror {error_message}")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en la base de datos")

    finally:
        db.close()

    return cambio_password
