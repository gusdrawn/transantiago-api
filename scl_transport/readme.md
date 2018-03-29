
# Instrucciones Desarrollo

## Prerrequisitos

- Necesitas tener instalado postgreSQL en tu entorno de desarrollo con 2 base de datos (vacías): `testing` y `scltransit`. La primera es para ser capaz de correr los tests y la segunda es por si deseas correr el proyecto apuntando a una base local (abajo se explica como cargar los datos).

- Python 2.7

## Tests

Para correr los tests

1. Instalar dependencias:

```
pip install -r requirements.txt
```

2. Definir el entorno a utilizar (`test`): Para esto hay que utilizar la variable de entorno **ENVIRONMENT** con valor **test**:

```
export ENVIRONMENT=test
```

3. Correr tests: Todos los tests están dentro de la carpeta **/tests**, acá el comando para ejecutar los tests:

```
nosetests tests
```

## Instalación proyecto para entorno de desarrollo:

1. Definir el entorno a utilizar (`dev`): Para esto hay que utilizar la variable de entorno **ENVIRONMENT** con valor **dev**:

```
export ENVIRONMENT=dev
```

2. Instalar dependencias:

```
pip install -r requirements.txt
```

3. Cargar datos localmente

Para Ejecutar el proyecto localmente, lo recomendado es cargar una base de datos con los datos reales del último GTFS disponible.

Asumiendo que ya la base de datos local es `postgresql://postgres:@loca
lhost/scltransit`, necesitas ejecutar el siguiente comando para cargar los datos (en el directorio raíz del proyecto):

```
scl_transport/gtfsdb/bin/gtfsdb-load --database_url postgresql://postgres:@loca
lhost/scltransit --is_geospatial https://www.dtpm.cl/descargas/gtfs/GTFS.zip
```

**NOTA**: El proceso de carga de datos toma un buen tiempo, alrededor de 40 minutos. La razón es que se analizan y procesan los datos para facilitar la consulta posterior a través de la API. 


## Ejecutar proyecto

```
python apidev.py
```

