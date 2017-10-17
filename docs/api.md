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
| `limit`  | `si`   | `50`       | Cantidad de resultados por página.               |
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
    "total_results": 3796,
    "total_pages": 3796,
    "results": [
        {
            "direction": null,
            "stop_code": "PB1",
            "stop_lon": "-70.623095148",
            "stop_id": "PB1",
            "stop_lat": "-33.404553756",
            "stop_url": null,
            "parent_station": null,
            "position": null,
            "stop_desc": null,
            "stop_name": "PB1-Venezuela Esq. / Bolivia",
            "zone_id": null
        },
        {
            "direction": null,
            "stop_code": "PB2",
            "stop_lon": "-70.626639248",
            "stop_id": "PB2",
            "stop_lat": "-33.402453078",
            "stop_url": null,
            "parent_station": null,
            "position": null,
            "stop_desc": null,
            "stop_name": "PB2-Venezuela Esq. / H. De La Concepción",
            "zone_id": null
        },
        {
            "direction": null,
            "stop_code": "PB3",
            "stop_lon": "-70.629734654",
            "stop_id": "PB3",
            "stop_lat": "-33.401218645",
            "stop_url": null,
            "parent_station": null,
            "position": null,
            "stop_desc": null,
            "stop_name": "PB3-Reina De Chile Esq. / Avenida El Salto",
            "zone_id": null
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
    "direction": null,
    "stop_code": "PB1",
    "stop_lon": "-70.623095148",
    "stop_id": "PB1",
    "stop_lat": "-33.404553756",
    "stop_url": null,
    "parent_station": null,
    "position": null,
    "stop_desc": null,
    "stop_name": "PB1-Venezuela Esq. / Bolivia",
    "zone_id": null
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
| `limit`  | `si`   | `50`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |

> **Ejemplo**

- Consulta

```curl
api/v1/stops/101/routes
```

- Respuesta

```json
{
    "results": [
        {
            "route_text_color": "000000",
            "route_long_name": "Recoleta - Cerrillos",
            "end_date": "2018-03-31",
            "route_type": "3",
            "min_headway_minutes": null,
            "is_active": true,
            "agency_id": "TS",
            "route_id": "101",
            "route_color": "00D5FF",
            "route_desc": null,
            "directions": [
                {
                    "route_id": "101",
                    "direction_name": "Inbound",
                    "direction_id": 1
                },
                {
                    "route_id": "101",
                    "direction_name": "Outbound",
                    "direction_id": 0
                }
            ],
            "route_url": null,
            "route_short_name": "101",
            "start_date": "2017-08-30",
            "route_sort_order": null
        },
        {
            "route_text_color": "FFFFFF",
            "route_long_name": "El Salto - Mapocho",
            "end_date": "2018-03-31",
            "route_type": "3",
            "min_headway_minutes": null,
            "is_active": true,
            "agency_id": "TS",
            "route_id": "B14",
            "route_color": "ED1C24",
            "route_desc": null,
            "directions": [
                {
                    "route_id": "B14",
                    "direction_name": "Inbound",
                    "direction_id": 1
                },
                {
                    "route_id": "B14",
                    "direction_name": "Outbound",
                    "direction_id": 0
                }
            ],
            "route_url": null,
            "route_short_name": "B14",
            "start_date": "2017-08-30",
            "route_sort_order": null
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
| `limit`  | `si`   | `50`       | Cantidad de resultados por página.               |
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
    "total_results": 253,
    "total_pages": 253,
    "results": [
        {
            "route_text_color": "000000",
            "route_long_name": "Recoleta - Cerrillos",
            "end_date": "2018-03-31",
            "route_type": "3",
            "min_headway_minutes": null,
            "is_active": true,
            "agency_id": "TS",
            "route_id": "101",
            "route_color": "00D5FF",
            "route_desc": null,
            "directions": [
                {
                    "route_id": "101",
                    "direction_name": "Outbound",
                    "direction_id": 0
                },
                {
                    "route_id": "101",
                    "direction_name": "Inbound",
                    "direction_id": 1
                }
            ],
            "route_url": null,
            "route_short_name": "101",
            "start_date": "2017-08-30",
            "route_sort_order": null
        },
        {
            "route_text_color": "000000",
            "route_long_name": "(M) Blanqueado - Cerrillos",
            "end_date": "2018-03-30",
            "route_type": "3",
            "min_headway_minutes": null,
            "is_active": true,
            "agency_id": "TS",
            "route_id": "101c",
            "route_color": "00D5FF",
            "route_desc": null,
            "directions": [
                {
                    "route_id": "101c",
                    "direction_name": "Outbound",
                    "direction_id": 0
                },
                {
                    "route_id": "101c",
                    "direction_name": "Inbound",
                    "direction_id": 1
                }
            ],
            "route_url": null,
            "route_short_name": "101c",
            "start_date": "2017-08-30",
            "route_sort_order": null
        },
        {
            "route_text_color": "000000",
            "route_long_name": "(M) Blanqueado - Mall Plaza Tobalaba",
            "end_date": "2018-03-31",
            "route_type": "3",
            "min_headway_minutes": null,
            "is_active": true,
            "agency_id": "TS",
            "route_id": "102",
            "route_color": "00D5FF",
            "route_desc": null,
            "directions": [
                {
                    "route_id": "102",
                    "direction_name": "Outbound",
                    "direction_id": 0
                },
                {
                    "route_id": "102",
                    "direction_name": "Inbound",
                    "direction_id": 1
                }
            ],
            "route_url": null,
            "route_short_name": "102",
            "start_date": "2017-08-30",
            "route_sort_order": null
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
    "route_text_color": "000000",
    "route_long_name": "(M) Blanqueado - Cerrillos",
    "end_date": "2018-03-30",
    "route_type": "3",
    "min_headway_minutes": null,
    "is_active": true,
    "agency_id": "TS",
    "route_id": "101c",
    "route_color": "00D5FF",
    "route_desc": null,
    "directions": [
        {
            "route_id": "101c",
            "direction_name": "Outbound",
            "direction_id": 0
        },
        {
            "route_id": "101c",
            "direction_name": "Inbound",
            "direction_id": 1
        }
    ],
    "route_url": null,
    "route_short_name": "101c",
    "start_date": "2017-08-30",
    "route_sort_order": null
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
| `limit`  | `si`   | `50`       | Cantidad de resultados por página.               |
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
            "start_time": "00:00:00",
            "route": {
                "route_text_color": "000000",
                "route_long_name": "Recoleta - Cerrillos",
                "end_date": "2018-03-31",
                "route_type": "3",
                "min_headway_minutes": null,
                "is_active": true,
                "agency_id": "TS",
                "route_id": "101",
                "route_color": "00D5FF",
                "route_desc": null,
                "directions": [
                    {
                        "route_id": "101",
                        "direction_name": "Outbound",
                        "direction_id": 0
                    },
                    {
                        "route_id": "101",
                        "direction_name": "Inbound",
                        "direction_id": 1
                    }
                ],
                "route_url": null,
                "route_short_name": "101",
                "start_date": "2017-08-30",
                "route_sort_order": null
            },
            "direction_id": "0",
            "is_valid": true,
            "frequency": {
                "start_time": "00:00:00",
                "headway_secs": 1200,
                "exact_times": false,
                "end_time": "01:00:00"
            },
            "end_time": "01:00:23",
            "start_stop": {
                "direction": null,
                "stop_code": "PB1",
                "stop_lon": "-70.623095148",
                "stop_id": "PB1",
                "stop_lat": "-33.404553756",
                "stop_url": null,
                "parent_station": null,
                "position": null,
                "stop_desc": null,
                "stop_name": "PB1-Venezuela Esq. / Bolivia",
                "zone_id": null
            },
            "trip_headsign": "Cerrillos",
            "end_stop": {
                "direction": null,
                "stop_code": "PI1243",
                "stop_lon": "-70.735167001",
                "stop_id": "PI1243",
                "stop_lat": "-33.508227853",
                "stop_url": null,
                "parent_station": null,
                "position": null,
                "stop_desc": null,
                "stop_name": "PI1243-Avenida Las Torres Esq. / La Primavera",
                "zone_id": null
            },
            "trip_id": "101-I-L_V34-B00",
            "trip_len": 76,
            "trip_short_name": null
        },
        {
            "start_time": "00:00:00",
            "route": {
                "route_text_color": "000000",
                "route_long_name": "Recoleta - Cerrillos",
                "end_date": "2018-03-31",
                "route_type": "3",
                "min_headway_minutes": null,
                "is_active": true,
                "agency_id": "TS",
                "route_id": "101",
                "route_color": "00D5FF",
                "route_desc": null,
                "directions": [
                    {
                        "route_id": "101",
                        "direction_name": "Outbound",
                        "direction_id": 0
                    },
                    {
                        "route_id": "101",
                        "direction_name": "Inbound",
                        "direction_id": 1
                    }
                ],
                "route_url": null,
                "route_short_name": "101",
                "start_date": "2017-08-30",
                "route_sort_order": null
            },
            "direction_id": "0",
            "is_valid": true,
            "frequency": {
                "start_time": "05:30:00",
                "headway_secs": 600,
                "exact_times": false,
                "end_time": "06:30:00"
            },
            "end_time": "01:17:39",
            "start_stop": {
                "direction": null,
                "stop_code": "PB1",
                "stop_lon": "-70.623095148",
                "stop_id": "PB1",
                "stop_lat": "-33.404553756",
                "stop_url": null,
                "parent_station": null,
                "position": null,
                "stop_desc": null,
                "stop_name": "PB1-Venezuela Esq. / Bolivia",
                "zone_id": null
            },
            "trip_headsign": "Cerrillos",
            "end_stop": {
                "direction": null,
                "stop_code": "PI1243",
                "stop_lon": "-70.735167001",
                "stop_id": "PI1243",
                "stop_lat": "-33.508227853",
                "stop_url": null,
                "parent_station": null,
                "position": null,
                "stop_desc": null,
                "stop_name": "PI1243-Avenida Las Torres Esq. / La Primavera",
                "zone_id": null
            },
            "trip_id": "101-I-L_V34-B02",
            "trip_len": 76,
            "trip_short_name": null
        },
        {
            "start_time": "00:00:00",
            "route": {
                "route_text_color": "000000",
                "route_long_name": "Recoleta - Cerrillos",
                "end_date": "2018-03-31",
                "route_type": "3",
                "min_headway_minutes": null,
                "is_active": true,
                "agency_id": "TS",
                "route_id": "101",
                "route_color": "00D5FF",
                "route_desc": null,
                "directions": [
                    {
                        "route_id": "101",
                        "direction_name": "Outbound",
                        "direction_id": 0
                    },
                    {
                        "route_id": "101",
                        "direction_name": "Inbound",
                        "direction_id": 1
                    }
                ],
                "route_url": null,
                "route_short_name": "101",
                "start_date": "2017-08-30",
                "route_sort_order": null
            },
            "direction_id": "0",
            "is_valid": true,
            "frequency": {
                "start_time": "06:30:00",
                "headway_secs": 600,
                "exact_times": false,
                "end_time": "08:30:00"
            },
            "end_time": "01:41:15",
            "start_stop": {
                "direction": null,
                "stop_code": "PB1",
                "stop_lon": "-70.623095148",
                "stop_id": "PB1",
                "stop_lat": "-33.404553756",
                "stop_url": null,
                "parent_station": null,
                "position": null,
                "stop_desc": null,
                "stop_name": "PB1-Venezuela Esq. / Bolivia",
                "zone_id": null
            },
            "trip_headsign": "Cerrillos",
            "end_stop": {
                "direction": null,
                "stop_code": "PI1243",
                "stop_lon": "-70.735167001",
                "stop_id": "PI1243",
                "stop_lat": "-33.508227853",
                "stop_url": null,
                "parent_station": null,
                "position": null,
                "stop_desc": null,
                "stop_name": "PI1243-Avenida Las Torres Esq. / La Primavera",
                "zone_id": null
            },
            "trip_id": "101-I-L_V34-B03",
            "trip_len": 76,
            "trip_short_name": null
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
    "start_time": "00:00:00",
    "route": {
        "route_text_color": "000000",
        "route_long_name": "Recoleta - Cerrillos",
        "end_date": "2018-03-31",
        "route_type": "3",
        "min_headway_minutes": null,
        "is_active": true,
        "agency_id": "TS",
        "route_id": "101",
        "route_color": "00D5FF",
        "route_desc": null,
        "directions": [
            {
                "route_id": "101",
                "direction_name": "Outbound",
                "direction_id": 0
            },
            {
                "route_id": "101",
                "direction_name": "Inbound",
                "direction_id": 1
            }
        ],
        "route_url": null,
        "route_short_name": "101",
        "start_date": "2017-08-30",
        "route_sort_order": null
    },
    "direction_id": "0",
    "is_valid": true,
    "frequency": {
        "start_time": "00:00:00",
        "headway_secs": 1200,
        "exact_times": false,
        "end_time": "01:00:00"
    },
    "end_time": "01:00:23",
    "start_stop": {
        "direction": null,
        "stop_code": "PB1",
        "stop_lon": "-70.623095148",
        "stop_id": "PB1",
        "stop_lat": "-33.404553756",
        "stop_url": null,
        "parent_station": null,
        "position": null,
        "stop_desc": null,
        "stop_name": "PB1-Venezuela Esq. / Bolivia",
        "zone_id": null
    },
    "trip_headsign": "Cerrillos",
    "end_stop": {
        "direction": null,
        "stop_code": "PI1243",
        "stop_lon": "-70.735167001",
        "stop_id": "PI1243",
        "stop_lat": "-33.508227853",
        "stop_url": null,
        "parent_station": null,
        "position": null,
        "stop_desc": null,
        "stop_name": "PI1243-Avenida Las Torres Esq. / La Primavera",
        "zone_id": null
    },
    "trip_id": "101-I-L_V34-B00",
    "trip_len": 76,
    "trip_short_name": null
}
```

### Listar paraderos de viaje

> **Endpoint**

```curl
api/v1/trips/<trip_id>/stops
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `50`       | Cantidad de resultados por página.               |
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
            "direction": null,
            "stop_code": "PB1",
            "stop_lon": "-70.623095148",
            "stop_id": "PB1",
            "stop_lat": "-33.404553756",
            "stop_url": null,
            "parent_station": null,
            "position": null,
            "stop_desc": null,
            "stop_name": "PB1-Venezuela Esq. / Bolivia",
            "zone_id": null
        },
        {
            "direction": null,
            "stop_code": "PB10",
            "stop_lon": "-70.650770017",
            "stop_id": "PB10",
            "stop_lat": "-33.395523330",
            "stop_url": null,
            "parent_station": null,
            "position": null,
            "stop_desc": null,
            "stop_name": "PB10-Avenida Dorsal Esq. / La Plata",
            "zone_id": null
        },
        {
            "direction": null,
            "stop_code": "PB108",
            "stop_lon": "-70.703977045",
            "stop_id": "PB108",
            "stop_lat": "-33.405162456",
            "stop_url": null,
            "parent_station": null,
            "position": null,
            "stop_desc": null,
            "stop_name": "PB108-Parada 3 / Plaza Renca",
            "zone_id": null
        }
    ],
    "page_size": 3
}
```

### Listar puntos de trayecto para viaje

> **Endpoint**

```curl
api/v1/trips/<trip_id>/shape
```

> **Ejemplo**

- Consulta

```curl
api/v1/trips/101-I-L_V34-B00/shape
```

- Respuesta

```json
{
    "results": [
        {
            "shape_pt_lat": "-33.406175001",
            "shape_id": "101I_V34",
            "shape_pt_lon": "-70.623244000",
            "shape_pt_sequence": 1
        },
        {
            "shape_pt_lat": "-33.405073001",
            "shape_id": "101I_V34",
            "shape_pt_lon": "-70.622375000",
            "shape_pt_sequence": 2
        },
        {
            "shape_pt_lat": "-33.404523001",
            "shape_id": "101I_V34",
            "shape_pt_lon": "-70.623311000",
            "shape_pt_sequence": 3
        },
        {
            "shape_pt_lat": "-33.403721001",
            "shape_id": "101I_V34",
            "shape_pt_lon": "-70.624666000",
            "shape_pt_sequence": 4
        },
        {
            "shape_pt_lat": "-33.403699001",
            "shape_id": "101I_V34",
            "shape_pt_lon": "-70.624721000",
            "shape_pt_sequence": 5
        }
    ]
}
```

## Schedule (`Horarios`)

!> **NOTA** Este endpoint aún está en proceso de construcción.

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
