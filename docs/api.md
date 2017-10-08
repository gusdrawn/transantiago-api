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

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `100`       | Cantidad de resultados por página.               |
| `date`     | `si`   | `` | Fecha de horario a filtrar. formato ISO 8601 YYYY-MM-DD. |

> **Ejemplo**

- Consulta

```curl
api/v1/stops/PA1/schedule?limit=3&date=2017-11-11
```

- Respuesta

```json
{
    "results": [
        {
            "stop_headsign": null,
            "stop": {
                "stop_lat": "-33.440116927",
                "stop_code": "PA1",
                "stop_lon": "-70.680021028",
                "stop_url": null,
                "stop_id": "PA1",
                "stop_name": "PA1-Parada 6 / (M) Quinta Normal"
            },
            "arrival_time": "00:21:50",
            "stop_sequence": 34,
            "trip": {
                "route": {
                    "route_long_name": "El Cortijo - (M) Estacion Central",
                    "route_type": "3",
                    "route_text_color": "FFFFFF",
                    "agency_id": "TS",
                    "route_id": "B26",
                    "route_color": "ED1C24",
                    "route_desc": null,
                    "route_url": null,
                    "route_short_name": "B26"
                },
                "direction_id": "0",
                "is_valid": true,
                "trip_headsign": "(M) Est. Central",
                "start_stop": {
                    "stop_lat": "-33.367588431",
                    "stop_code": "PB833",
                    "stop_lon": "-70.691163625",
                    "stop_url": null,
                    "stop_id": "PB833",
                    "stop_name": "PB833-Julio Parra Santos Esq. / Julio Montt Salamanca"
                },
                "trip_len": 37,
                "end_stop": {
                    "stop_lat": "-33.452072584",
                    "stop_code": "PI169",
                    "stop_lon": "-70.678008931",
                    "stop_url": null,
                    "stop_id": "PI169",
                    "stop_name": "PI169-Parada 5 / (M) Estación Central"
                },
                "trip_id": "B26-I-D_V34-B28",
                "trip_short_name": null
            },
            "departure_time": "00:21:50"
        },
        {
            "stop_headsign": null,
            "stop": {
                "stop_lat": "-33.440116927",
                "stop_code": "PA1",
                "stop_lon": "-70.680021028",
                "stop_url": null,
                "stop_id": "PA1",
                "stop_name": "PA1-Parada 6 / (M) Quinta Normal"
            },
            "arrival_time": "00:21:52",
            "stop_sequence": 34,
            "trip": {
                "route": {
                    "route_long_name": "El Cortijo - (M) Estacion Central",
                    "route_type": "3",
                    "route_text_color": "FFFFFF",
                    "agency_id": "TS",
                    "route_id": "B26",
                    "route_color": "ED1C24",
                    "route_desc": null,
                    "route_url": null,
                    "route_short_name": "B26"
                },
                "direction_id": "0",
                "is_valid": true,
                "trip_headsign": "(M) Est. Central",
                "start_stop": {
                    "stop_lat": "-33.367588431",
                    "stop_code": "PB833",
                    "stop_lon": "-70.691163625",
                    "stop_url": null,
                    "stop_id": "PB833",
                    "stop_name": "PB833-Julio Parra Santos Esq. / Julio Montt Salamanca"
                },
                "trip_len": 37,
                "end_stop": {
                    "stop_lat": "-33.452072584",
                    "stop_code": "PI169",
                    "stop_lon": "-70.678008931",
                    "stop_url": null,
                    "stop_id": "PI169",
                    "stop_name": "PI169-Parada 5 / (M) Estación Central"
                },
                "trip_id": "B26-I-L_V34-B00",
                "trip_short_name": null
            },
            "departure_time": "00:21:52"
        },
        {
            "stop_headsign": null,
            "stop": {
                "stop_lat": "-33.440116927",
                "stop_code": "PA1",
                "stop_lon": "-70.680021028",
                "stop_url": null,
                "stop_id": "PA1",
                "stop_name": "PA1-Parada 6 / (M) Quinta Normal"
            },
            "arrival_time": "00:22:25",
            "stop_sequence": 34,
            "trip": {
                "route": {
                    "route_long_name": "El Cortijo - (M) Estacion Central",
                    "route_type": "3",
                    "route_text_color": "FFFFFF",
                    "agency_id": "TS",
                    "route_id": "B26",
                    "route_color": "ED1C24",
                    "route_desc": null,
                    "route_url": null,
                    "route_short_name": "B26"
                },
                "direction_id": "0",
                "is_valid": true,
                "trip_headsign": "(M) Est. Central",
                "start_stop": {
                    "stop_lat": "-33.367588431",
                    "stop_code": "PB833",
                    "stop_lon": "-70.691163625",
                    "stop_url": null,
                    "stop_id": "PB833",
                    "stop_name": "PB833-Julio Parra Santos Esq. / Julio Montt Salamanca"
                },
                "trip_len": 37,
                "end_stop": {
                    "stop_lat": "-33.452072584",
                    "stop_code": "PI169",
                    "stop_lon": "-70.678008931",
                    "stop_url": null,
                    "stop_id": "PI169",
                    "stop_name": "PI169-Parada 5 / (M) Estación Central"
                },
                "trip_id": "B26-I-L_V34-B11",
                "trip_short_name": null
            },
            "departure_time": "00:22:25"
        }
    ]
}
```

### Listar horarios de paradero para ruta (micro) específica.

> **Endpoint**

```curl
api/v1/stops/<stop_id>/schedule/<route_id>
```

> **Argumentos**

  - `{string} stop_id`: identificador de paradero
  - `{string} route_id`: identificador de ruta

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `100`       | Cantidad de resultados por página.               |
| `date`     | `si`   | `` | Fecha de horario a filtrar. formato ISO 8601 YYYY-MM-DD. |

> **Ejemplo**

- Consulta

```curl
api/v1/stops/PA1/schedule/J16?limit=3&date=2017-11-11
```

- Respuesta

```json
{
    "results": [
        {
            "stop_headsign": null,
            "stop": {
                "stop_lat": "-33.440116927",
                "stop_code": "PA1",
                "stop_lon": "-70.680021028",
                "stop_url": null,
                "stop_id": "PA1",
                "stop_name": "PA1-Parada 6 / (M) Quinta Normal"
            },
            "arrival_time": "00:22:51",
            "stop_sequence": 34,
            "trip": {
                "route": {
                    "route_long_name": "El Cortijo - (M) Estacion Central",
                    "route_type": "3",
                    "route_text_color": "FFFFFF",
                    "agency_id": "TS",
                    "route_id": "B26",
                    "route_color": "ED1C24",
                    "route_desc": null,
                    "route_url": null,
                    "route_short_name": "B26"
                },
                "direction_id": "0",
                "is_valid": true,
                "trip_headsign": "(M) Est. Central",
                "start_stop": {
                    "stop_lat": "-33.367588431",
                    "stop_code": "PB833",
                    "stop_lon": "-70.691163625",
                    "stop_url": null,
                    "stop_id": "PB833",
                    "stop_name": "PB833-Julio Parra Santos Esq. / Julio Montt Salamanca"
                },
                "trip_len": 37,
                "end_stop": {
                    "stop_lat": "-33.452072584",
                    "stop_code": "PI169",
                    "stop_lon": "-70.678008931",
                    "stop_url": null,
                    "stop_id": "PI169",
                    "stop_name": "PI169-Parada 5 / (M) Estación Central"
                },
                "trip_id": "B26-I-S_V34-B12",
                "trip_short_name": null
            },
            "departure_time": "00:22:51"
        }
    ]
}
```