# Database Manager Tool

Aplicación de escritorio desarrollada en Python utilizando Tkinter para la administración de bases de datos en CockroachDB.  

Este proyecto fue creado para la asignatura **Teoría de Base de Datos II** y permite interactuar directamente con las tablas del sistema del motor de base de datos.

## Descripción

Database Manager Tool permite:

- Gestión de conexiones a la base de datos
- Autenticación de usuario
- Exploración de objetos del sistema (tablas, vistas, índices, etc.)
- Generación automática de DDL a partir de metadata
- Creación básica de tablas y vistas
- Ejecución de consultas SQL (SELECT, DDL y DML)
- Visualización de resultados en formato tabular

El sistema consulta directamente las tablas del sistema (`pg_catalog` y `crdb_internal`) y no utiliza ORM ni `information_schema`, cumpliendo con las restricciones del proyecto académico.

## Tecnologías utilizadas

- Python 3
- Tkinter
- CockroachDB
- psycopg2
- Docker

## Ejecución

1. Instalar dependencias:
   pip install psycopg2

2. Ejecutar la aplicación:
  cd src
  python app.py

## Autor

Kristian Murillo



