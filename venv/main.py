
import aiomysql
import fastapi

# Importación de routers
from api import autenticacion
from api import usuario
from api import perfil
from api import principal
from api import asignatura
from api import programacion
from api import producto
from api import registro
from api import taller
from api import carrera
from api import param
from api import agrupador
from api import unidad_medida
from api import categoria_producto
from api import consultas

from database import get_db_connection

# Instanciamos la aplicación
api = fastapi.FastAPI(
    title="API's para sistema de administración de talleres DuocUC",
    description="Catálogo de API's construidas para dar servicio al sistema web de administración de talleres DuocUC para las carreras de gastronomía y administración hotelera",
    openapi_tags=[
        {"name": "Asignaturas",
         "description": "API's relacionadas con asignaturas"},
        {"name": "Agrupadores",
         "description": "API's relacionadas con los agrupadores de los productos de un taller"},
        {"name": "Autenticación",
         "description": "API's relacionadas con la autenticación de usuario, cambio de contraseña y otras"},
        {"name": "Carreras",
         "description": "API's relacionadas con la administración de carreras"},
        {"name": "Categorías de productos",
         "description": "API's relacionadas con las categorías de los productos"},
        {"name": "Consultas",
         "description": "API's relacionadas con consultas del sistema"},
        {"name": "Parámetros",
         "description": "API's relacionadas con los parámetros del sistema"},
        {"name": "Perfiles",
         "description": "API's relacionadas con los perfiles del sistema o asociadas al perfilamiento del usuario"},
        {"name": "Principal",
         "description": "API's relacionadas con el dashboard que se muestra en la página principal de un usuario ya autenticado"},
        {"name": "Productos",
         "description": "API's relacionadas con los productos del sistema"},
        {"name": "Programación",
         "description": "API's relacionadas con la programación de los talleres"},
        {"name": "Registro",
         "description": "API's relacionadas con el registro de ejecución de los talleres"},
        {"name": "Talleres",
         "description": "API's relacionadas con la administración de los talleres"},
        {"name": "Unidades de medida",
         "description": "API's relacionadas con las unidades de medida disponibles en el sistema"},
        {"name": "Usuarios",
         "description": "API's relacionadas con la administración de usuarios"},
    ],
    version="0.1.0",
)

# Variable para base de datos
db = None


# Método de configuración de routers
async def configura_routers():
    api.include_router(autenticacion.router)
    api.include_router(usuario.router)
    api.include_router(perfil.router)
    api.include_router(principal.router)
    api.include_router(asignatura.router)
    api.include_router(programacion.router)
    api.include_router(producto.router)
    api.include_router(registro.router)
    api.include_router(taller.router)
    api.include_router(carrera.router)
    api.include_router(param.router)
    api.include_router(agrupador.router)
    api.include_router(unidad_medida.router)
    api.include_router(categoria_producto.router)
    api.include_router(consultas.router)


# Método de configuración de base de datos
async def configura_db():
    global db
    try:
        # Obtiene la conexión a la base de datos desde el módulo database
        conn = await get_db_connection()
        # Asigna la conexión a la variable global db
        db = conn
    except aiomysql.Error as e:
        # Maneja la excepción y muestra un mensaje de error personalizado
        print(f"Error al conectar a la base de datos: {e}")
        return None


# Método de configuración general, que llama a los otros sub-métodos de configuración
async def configura():
    await configura_db()
    await configura_routers()


# Método para cerrar la conexión a la base de datos
async def close_db_connection():
    global db
    if db is not None:
        db.close()


# Manejadores de eventos
api.add_event_handler("startup", configura)
api.add_event_handler("shutdown", close_db_connection)
