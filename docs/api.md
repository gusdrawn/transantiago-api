# API

Actualmente la API está disponible en `https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/` (temporal)

## Stops (`Paraderos`)

Información sobre paraderos

### Listar paraderos

> **Endpoint**

```curl
api/v1/stops
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `100`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |
| `lon` | `si` | `None`      | Longitud, debe ser definido en conjunto con `lat`. Ejemplo: `-70.643562`      |
| `lat` | `si` | `None`      | Latitud, debe ser definido en conjunto con `lon` Ejemplo: `-33.491585      |

> **Ejemplo**

- Consulta

```curl
api/v1/stops?limit=3
```

- Respuesta

```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 1140,
    "total_pages": 1140,
    "results": [
        {
            "stop_lat": "-33.4045537555341",
            "stop_code": "PB1",
            "stop_lon": "-70.623095148163",
            "stop_url": "",
            "stop_id": "PB1",
            "stop_name": "PB1-Venezuela Esq. / Bolivia"
        },
        {
            "stop_lat": "-33.402453078379",
            "stop_code": "PB2",
            "stop_lon": "-70.6266392477005",
            "stop_url": "",
            "stop_id": "PB2",
            "stop_name": "PB2-Venezuela Esq. / H. De La Concepción"
        },
        {
            "stop_lat": "-33.4012186446509",
            "stop_code": "PB3",
            "stop_lon": "-70.6297346535453",
            "stop_url": "",
            "stop_id": "PB3",
            "stop_name": "PB3-Reina De Chile Esq. / Avenida El Salto"
        }
    ],
    "page_size": 3
}
```

### Obtener paradero

> **Endpoint**

```curl
api/v1/stops/<stop_id>
```

> **Argumentos**

  - `{string} stop_id`: identificador de paradero


> **Ejemplo**

- Consulta

```curl
api/v1/stops/PB1
```

- Respuesta

```json
{
    "stop_lat": "-33.4045537555341",
    "stop_code": "PB1",
    "stop_lon": "-70.623095148163",
    "stop_url": "",
    "stop_id": "PB1",
    "stop_name": "PB1-Venezuela Esq. / Bolivia"
}
```

### Listar rutas (micros) de paradero

> **Endpoint**

```curl
api/v1/stops/<stop_id>/routes
```

> **Argumentos**

  - `{string} stop_id`: identificador de paradero


> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `100`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |

> **Ejemplo**

- Consulta

```curl
api/v1/stops/PB1/routes
```

- Respuesta

```json
{
    "results": [
        {
            "route_long_name": "Recoleta - Cerrillos",
            "route_type": "3",
            "route_text_color": "000000",
            "agency_id": "TS",
            "route_id": "101",
            "route_color": "00D5FF",
            "route_desc": "",
            "route_url": "",
            "route_short_name": "101"
        },
        {
            "route_long_name": "El Salto - Mapocho",
            "route_type": "3",
            "route_text_color": "FFFFFF",
            "agency_id": "TS",
            "route_id": "B14",
            "route_color": "ED1C24",
            "route_desc": "",
            "route_url": "",
            "route_short_name": "B14"
        }
    ]
}
```

## Routes (`Micros`)

Información sobre rutas (micros).

### Listar rutas

> **Endpoint**

```curl
api/v1/routes
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `100`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |

> **Ejemplo**

- Consulta

```curl
api/v1/routes?limit=3
```

- Respuesta

```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 131,
    "total_pages": 131,
    "results": [
        {
            "route_long_name": "Recoleta - Cerrillos",
            "route_type": "3",
            "route_text_color": "000000",
            "agency_id": "TS",
            "route_id": "101",
            "route_color": "00D5FF",
            "route_desc": "",
            "route_url": "",
            "route_short_name": "101"
        },
        {
            "route_long_name": "(M) Blanqueado - Cerrillos",
            "route_type": "3",
            "route_text_color": "000000",
            "agency_id": "TS",
            "route_id": "101c",
            "route_color": "00D5FF",
            "route_desc": "",
            "route_url": "",
            "route_short_name": "101c"
        },
        {
            "route_long_name": "(M) Blanqueado - Mall Plaza Tobalaba",
            "route_type": "3",
            "route_text_color": "000000",
            "agency_id": "TS",
            "route_id": "102",
            "route_color": "00D5FF",
            "route_desc": "",
            "route_url": "",
            "route_short_name": "102"
        }
    ],
    "page_size": 3
}
```


### Obtener ruta

> **Endpoint**

```curl
api/v1/routes/<route_id>
```

> **Argumentos**

  - `{string} route_id`: identificador de ruta


> **Ejemplo**

- Consulta

```curl
api/v1/routes/101c
```

- Respuesta

```json
{
    "route_long_name": "(M) Blanqueado - Cerrillos",
    "route_type": "3",
    "route_text_color": "000000",
    "agency_id": "TS",
    "route_id": "101c",
    "route_color": "00D5FF",
    "route_desc": "",
    "route_url": "",
    "route_short_name": "101c"
}
```

## Trips (`Viajes`)

Informaciñon sobre viajes.

### Listar viajes

> **Endpoint**

```curl
api/v1/trips
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `100`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |

> **Ejemplo**

- Consulta

```curl
api/v1/trips?limit=3
```

- Respuesta

```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 4764,
    "total_pages": 4764,
    "results": [
        {
            "service": {
                "end_date": "2018-03-31",
                "monday": true,
                "tuesday": true,
                "friday": true,
                "wednesday": true,
                "thursday": true,
                "saturday": false,
                "sunday": false,
                "service_id": "L_V34",
                "start_date": "2017-08-30"
            },
            "route": {
                "route_long_name": "Recoleta - Cerrillos",
                "route_type": "3",
                "route_text_color": "000000",
                "agency_id": "TS",
                "route_id": "101",
                "route_color": "00D5FF",
                "route_desc": "",
                "route_url": "",
                "route_short_name": "101"
            },
            "direction_id": "0",
            "frequency": {
                "start_time": "00:00:00",
                "headway_secs": 1200,
                "exact_times": false,
                "end_time": "01:00:00"
            },
            "trip_headsign": "Cerrillos",
            "trip_id": "101-I-L_V34-B00"
        },
        {
            "service": {
                "end_date": "2018-03-31",
                "monday": true,
                "tuesday": true,
                "friday": true,
                "wednesday": true,
                "thursday": true,
                "saturday": false,
                "sunday": false,
                "service_id": "L_V34",
                "start_date": "2017-08-30"
            },
            "route": {
                "route_long_name": "Recoleta - Cerrillos",
                "route_type": "3",
                "route_text_color": "000000",
                "agency_id": "TS",
                "route_id": "101",
                "route_color": "00D5FF",
                "route_desc": "",
                "route_url": "",
                "route_short_name": "101"
            },
            "direction_id": "0",
            "frequency": {
                "start_time": "05:30:00",
                "headway_secs": 600,
                "exact_times": false,
                "end_time": "06:30:00"
            },
            "trip_headsign": "Cerrillos",
            "trip_id": "101-I-L_V34-B02"
        },
        {
            "service": {
                "end_date": "2018-03-31",
                "monday": true,
                "tuesday": true,
                "friday": true,
                "wednesday": true,
                "thursday": true,
                "saturday": false,
                "sunday": false,
                "service_id": "L_V34",
                "start_date": "2017-08-30"
            },
            "route": {
                "route_long_name": "Recoleta - Cerrillos",
                "route_type": "3",
                "route_text_color": "000000",
                "agency_id": "TS",
                "route_id": "101",
                "route_color": "00D5FF",
                "route_desc": "",
                "route_url": "",
                "route_short_name": "101"
            },
            "direction_id": "0",
            "frequency": {
                "start_time": "06:30:00",
                "headway_secs": 600,
                "exact_times": false,
                "end_time": "08:30:00"
            },
            "trip_headsign": "Cerrillos",
            "trip_id": "101-I-L_V34-B03"
        }
    ],
    "page_size": 3
}
```

### Obtener viaje

> **Endpoint**

```curl
api/v1/trips/<trip_id>
```

> **Argumentos**

  - `{string} trip_id`: identificador de viaje


> **Ejemplo**

- Consulta

```curl
api/v1/trips/101-I-L_V34-B00
```

- Respuesta

```json
{
    "service": {
        "end_date": "2018-03-31",
        "monday": true,
        "tuesday": true,
        "friday": true,
        "wednesday": true,
        "thursday": true,
        "saturday": false,
        "sunday": false,
        "service_id": "L_V34",
        "start_date": "2017-08-30"
    },
    "route": {
        "route_long_name": "Recoleta - Cerrillos",
        "route_type": "3",
        "route_text_color": "000000",
        "agency_id": "TS",
        "route_id": "101",
        "route_color": "00D5FF",
        "route_desc": "",
        "route_url": "",
        "route_short_name": "101"
    },
    "direction_id": "0",
    "frequency": {
        "start_time": "00:00:00",
        "headway_secs": 1200,
        "exact_times": false,
        "end_time": "01:00:00"
    },
    "trip_headsign": "Cerrillos",
    "trip_id": "101-I-L_V34-B00"
}
```

### Listar paraderos de viaje

> **Endpoint**

```curl
api/v1/trips/trip_id/stops
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `100`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |

> **Ejemplo**

- Consulta

```curl
api/v1/trips/101-I-L_V34-B00/stops?limit=3
```

- Respuesta

```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 26,
    "total_pages": 26,
    "results": [
        {
            "stop_lat": "-33.4045537555341",
            "stop_code": "PB1",
            "stop_lon": "-70.623095148163",
            "stop_url": "",
            "stop_id": "PB1",
            "stop_name": "PB1-Venezuela Esq. / Bolivia"
        },
        {
            "stop_lat": "-33.402453078379",
            "stop_code": "PB2",
            "stop_lon": "-70.6266392477005",
            "stop_url": "",
            "stop_id": "PB2",
            "stop_name": "PB2-Venezuela Esq. / H. De La Concepción"
        },
        {
            "stop_lat": "-33.4012186446509",
            "stop_code": "PB3",
            "stop_lon": "-70.6297346535453",
            "stop_url": "",
            "stop_id": "PB3",
            "stop_name": "PB3-Reina De Chile Esq. / Avenida El Salto"
        }
    ],
    "page_size": 3
}
```

## Schedule (`Horarios`)

Información sobre horarios de buses en paradero especificado.

### Listar horarios de paradero

> **Endpoint**

```curl
api/v1/stops/<stop_id>/schedule
```

> **Argumentos**

  - `{string} stop_id`: identificador de paradero

> **Query params**

> **Ejemplo**

- Consulta

```curl
api/v1/stops/PA1/schedule
```

- Respuesta

```json
{
    "results": [
        {
            "arrival_date": "2017-10-13",
            "arrival_timestamp": 1507919127,
            "route_id": "406",
            "arrival_time": "18:25:27",
            "stop_id": "PA1",
            "trip_id": "406-I-L_V34-B08"
        },
        {
            "arrival_date": "2017-10-13",
            "arrival_timestamp": 1507919137,
            "route_id": "109",
            "arrival_time": "18:25:37",
            "stop_id": "PA1",
            "trip_id": "109-I-L_V34-B08"
        },
        {
            "arrival_date": "2017-10-13",
            "arrival_timestamp": 1507919137,
            "route_id": "513",
            "arrival_time": "18:25:37",
            "stop_id": "PA1",
            "trip_id": "513-I-L_V34-B08"
        }
    ]
}
```
