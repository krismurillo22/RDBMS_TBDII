# Database Manager Tool

Aplicación de escritorio desarrollada en Python utilizando Tkinter para la administración de bases de datos en CockroachDB.

Este proyecto fue creado para la asignatura **Teoría de Base de Datos II** y permite interactuar directamente con el catálogo interno del motor de base de datos, sin utilizar ORM ni herramientas de abstracción.

------------------------------------------------------------------------

## Descripción

Database Manager Tool es una herramienta tipo cliente visual (similar en concepto a DBeaver o pgAdmin) que permite administrar bases de datos CockroachDB mediante una interfaz gráfica desarrollada en Tkinter.

La aplicación permite:

-   Gestión de múltiples conexiones
-   Autenticación de usuario
-   Exploración jerárquica de objetos del sistema:
    -   Bases de datos
    -   Esquemas
    -   Tablas
    -   Vistas
    -   Índices
    -   Funciones
    -   Secuencias
-   Generación automática de DDL desde metadata
-   Creación visual básica de tablas y vistas
-   Editor SQL integrado
-   Ejecución de consultas SELECT, DDL y DML
-   Visualización de resultados en formato tabular
-   Manejo de errores del motor

El sistema consulta directamente las tablas internas (`pg_catalog` y `crdb_internal`) y **no utiliza**:

-   ORM (SQLAlchemy, Entity Framework, etc.)
-   `information_schema`
-   Frameworks de persistencia

Cumpliendo así con las restricciones académicas establecidas.

------------------------------------------------------------------------

## Arquitectura del Sistema

El proyecto sigue una arquitectura modular separando responsabilidades en capas claras:

### Capa de Presentación (UI)

Ubicada en el directorio `ui/`, contiene:

-   Ventana principal (`MainWindow`)
-   Árbol de objetos (`ObjectTree`)
-   Editor SQL (`SqlRunnerView`)
-   Vistas de creación de objetos (`CreateTableView`, `CreateViewView`)
-   Diálogos de conexión

**Responsabilidad:** - Interacción con el usuario - Renderizado de datos - Navegación entre vistas

------------------------------------------------------------------------

### Capa de Servicios

Ubicada en `services/`, incluye:

-   `connection_service.py`
-   Gestión de estado de conexión
-   Cambio dinámico de base de datos

**Responsabilidad:** - Abstracción de conexión - Control de sesiones - Manejo de múltiples bases

------------------------------------------------------------------------

### Capa de Acceso a Datos

Ubicada en `db/`, incluye:

-   `connection.py`
-   `execute.py`
-   `objects_repo.py`
-   Consultas SQL hacia `pg_catalog`

**Responsabilidad:** - Ejecutar consultas SQL - Obtener metadata - Reconstruir DDL manualmente

No se utiliza ningún ORM. Todas las consultas son SQL directo usando `psycopg2`.

------------------------------------------------------------------------

### Modelo de Objetos

Ubicado en `models/`, contiene:

-   `db_object.py`
-   Representación estructurada de objetos de base de datos

------------------------------------------------------------------------

## Flujo General de Funcionamiento

1.  El usuario inicia la aplicación.
2.  Se establece una conexión a CockroachDB.
3.  El sistema consulta el catálogo interno.
4.  Se construye dinámicamente el árbol de navegación.
5.  Al seleccionar un objeto:
    -   Se obtiene su metadata.
    -   Se reconstruye el DDL.
    -   Se muestra el código en pantalla.
6.  El usuario puede ejecutar consultas SQL desde el editor.

------------------------------------------------------------------------

## Estructura del Proyecto

    src/
    │
    ├── app.py
    │
    ├── ui/
    │   ├── main_window.py
    │   ├── widgets/
    │   │   ├── object_tree.py
    │   │   ├── create_table_view.py
    │   │   ├── create_view_view.py
    │   │   ├── ddl_view.py
    │   │   ├── empty_view.py
    │   │   ├── table_details.py
    │   │   └── sql_runner_view.py
    │   ├── main_window.py
    │   ├── theme.py
    │   └── dialogs/
    │
    ├── services/
    │   └── connection_service.py
    │
    ├── db/
    │   ├── connection.py
    │   ├── execute.py
    │   ├── ddl_repo.py
    │   ├── crdb_system_tables.py
    │   └── objects_repo.py
    │
    └── models/
        └── db_object.py
    connections.json
    docker-compose.yml
    dockerfile

------------------------------------------------------------------------

## Tecnologías Utilizadas

-   Python 3
-   Tkinter (GUI)
-   CockroachDB
-   psycopg2
-   Docker
-   SQL directo

------------------------------------------------------------------------

## Consideraciones Técnicas

-   No se utilizan ORMs.
-   No se utiliza `information_schema`.
-   Se trabaja directamente con `pg_catalog`.
-   El DDL se reconstruye manualmente.
-   Se manejan errores del motor distribuido.
-   Se adapta el comportamiento a las limitaciones de CockroachDB.

------------------------------------------------------------------------

## Alcance del Proyecto

El sistema permite:

-   Gestión estructural básica
-   Visualización de objetos
-   Generación de DDL
-   Ejecución de consultas

No incluye:

-   Soporte para triggers avanzados
-   Procedimientos almacenados complejos
-   Gestión de extensiones
-   Administración de clúster distribuido

------------------------------------------------------------------------

## Ejecución

### 1. Instalar dependencias

``` bash
pip install psycopg2
```

### 2️. Ejecutar la aplicación

``` bash
cd src
python app.py
```

------------------------------------------------------------------------

## Autor

Kristian Murillo\
Proyecto académico -- Teoría de Base de Datos II
