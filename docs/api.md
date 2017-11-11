# API

Actualmente la API está disponible en `https://api.scltrans.it`

## Stops (`Paraderos`)

Información sobre paraderos o estaciones.

### Listar paraderos

> **Endpoint**

```curl
/v1/stops
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `100`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |
| `is_active`  | `si`   | `None`       | Opción para filtrar paraderos en funcionamiento.  |
| `center_lon` | `si` | `None`      | Longitud. Si se define, los resultados serán ordenados de más cercano a más lejano a este punto. Usar en conjunto con `center_lat`. Ejemplo: `-70.643562`      |
| `center_lat` | `si` | `None`      | Latitud. Si se define, los resultados serán ordenados de más cercano a más lejano a este punto. Usar en conjunto con `center_lon`. Ejemplo: `-33.491585`      |
| `radius` | `si` | `None`      | Radio en metros. Usar en conjunto con `center_lat` y `center_lon`. Si es definido, se mostrarán sólo los resultados dentro de ese radio (en relación al centro (center_lat` y `center_lon`))     |
| `bbox` | `si` | `None`      |  Bounding box (min Longitude , min Latitude , max Longitude , max Latitude). Si es definido, se mostrarán sólo los resultados dentro de este bbox.  Ejemplo: `-70.609818,-33.442328,-70.566473,-33.409806`    |


!> **NOTA**  `center_lon`, `center_lat` y `radius` formar parte del mismo filtro de geolocalización. No se debe usar en conjunto con `bbox`, puesto que este es otro filtro. 

> **Ejemplo**

- Consulta

```curl
/v1/stops?limit=3
```

- Respuesta


```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 5231,
    "total_pages": 5231,
    "results": [
        {
            "stop_lat": "-33.426908855",
            "stop_code": "PC2",
            "stop_lon": "-70.615901969",
            "agency_id": "TS",
            "stop_id": "PC2",
            "directions": [
                {
                    "direction_id": 0,
                    "direction_headsign": "Mall P. Tobalaba",
                    "direction_name": "Outbound"
                }
            ],
            "stop_name": "PC2-Parada 7 / (M) Pedro   De Valdivia"
        },
        {
            "stop_lat": "-33.455996455",
            "stop_code": "PI438",
            "stop_lon": "-70.699194124",
            "agency_id": "TS",
            "stop_id": "PI438",
            "directions": [
                {
                    "direction_id": 0,
                    "direction_headsign": "La Florida",
                    "direction_name": "Outbound"
                }
            ],
            "stop_name": "PI438-Parada 1 / (M) Ecuador"
        },
        {
            "stop_lat": "-33.463569085",
            "stop_code": "PI396",
            "stop_lon": "-70.722582982",
            "agency_id": "TS",
            "stop_id": "PI396",
            "directions": [
                {
                    "direction_id": 0,
                    "direction_headsign": "La Florida",
                    "direction_name": "Outbound"
                }
            ],
            "stop_name": "PI396-Parada  / Paradero 5 1/2   Pajaritos"
        }
    ],
    "page_size": 3
}
```

### Obtener paradero

> **Endpoint**

```curl
/v1/stops/<stop_id>
```

> **Argumentos**

  - `{string} stop_id`: identificador de paradero


> **Ejemplo**

- Consulta

```curl
/v1/stops/PB1
```

- Respuesta

```json
{
    "stop_lat": "-33.404553756",
    "stop_code": "PB1",
    "stop_lon": "-70.623095148",
    "agency_id": "TS",
    "stop_id": "PB1",
    "directions": [
        {
            "direction_id": 0,
            "direction_headsign": "Cerrillos",
            "direction_name": "Outbound"
        }
    ],
    "stop_name": "PB1-Venezuela Esq. / Bolivia"
}
```

### Listar servicios (`routes) de paradero

> **Endpoint**

```curl
/v1/stops/<stop_id>/routes
```

> **Argumentos**

  - `{string} stop_id`: identificador de paradero

> **Ejemplo**

- Consulta

```curl
/v1/stops/101/routes
```

- Respuesta

```json
{
    "results": [
        {
            "route_long_name": "El Salto - Mapocho",
            "end_date": "2018-03-31",
            "route_type": "3",
            "route_text_color": "FFFFFF",
            "agency_id": "TS",
            "route_id": "B14",
            "route_color": "ED1C24",
            "route_desc": null,
            "directions": [
                {
                    "direction_id": 1,
                    "route_id": "B14",
                    "direction_headsign": "El Salto",
                    "direction_name": "Inbound"
                },
                {
                    "direction_id": 0,
                    "route_id": "B14",
                    "direction_headsign": "Mapocho",
                    "direction_name": "Outbound"
                }
            ],
            "route_url": null,
            "route_short_name": "B14",
            "start_date": "2017-11-07"
        },
        {
            "route_long_name": "Recoleta - Cerrillos",
            "end_date": "2018-03-31",
            "route_type": "3",
            "route_text_color": "000000",
            "agency_id": "TS",
            "route_id": "101",
            "route_color": "00D5FF",
            "route_desc": null,
            "directions": [
                {
                    "direction_id": 0,
                    "route_id": "101",
                    "direction_headsign": "Cerrillos",
                    "direction_name": "Outbound"
                },
                {
                    "direction_id": 1,
                    "route_id": "101",
                    "direction_headsign": "Recoleta",
                    "direction_name": "Inbound"
                }
            ],
            "route_url": null,
            "route_short_name": "101",
            "start_date": "2017-11-07"
        }
    ]
}
```

### Listar viajes (`trips`) de paradero

> **Endpoint**

```curl
/v1/stops/<stop_id>/trips
```

> **Argumentos**

  - `{string} stop_id`: identificador de paradero

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `route_id`     | `si`   | `None` | opción de filtrar por `route_id` |
| `is_active`  | `si`   | `None`       | Opción para filtrar viajes activos.  |


> **Ejemplo**

- Consulta

```curl
/v1/stops/101/trips
```

- Respuesta

```json
{
    "results": [
        {
            "direction_id": "0",
            "start_time": "00:00:00",
            "route_id": "101",
            "frequency": {
                "start_time": "00:00:00",
                "headway_secs": 1800,
                "exact_times": false,
                "end_time": "01:00:00"
            },
            "trip_headsign": "Cerrillos",
            "end_time": "01:01:05",
            "service_id": "D_V35",
            "trip_len": 76,
            "trip_id": "101-I-D_V35-B21",
            "trip_short_name": null
        },
        {
            "direction_id": "0",
            "start_time": "00:00:00",
            "route_id": "101",
            "frequency": {
                "start_time": "05:30:00",
                "headway_secs": 720,
                "exact_times": false,
                "end_time": "09:30:00"
            },
            "trip_headsign": "Cerrillos",
            "end_time": "01:05:30",
            "service_id": "D_V35",
            "trip_len": 76,
            "trip_id": "101-I-D_V35-B23",
            "trip_short_name": null
        },
        {
            "direction_id": "0",
            "start_time": "00:00:00",
            "route_id": "101",
            "frequency": {
                "start_time": "09:30:00",
                "headway_secs": 533,
                "exact_times": false,
                "end_time": "13:30:00"
            },
            "trip_headsign": "Cerrillos",
            "end_time": "01:17:10",
            "service_id": "D_V35",
            "trip_len": 76,
            "trip_id": "101-I-D_V35-B24",
            "trip_short_name": null
        }
    ]
}
```


## Routes (`Servicios`)

Rutas de transporte público. Una ruta es un grupo de viajes que se muestran a los usuarios como servicio independiente.

### Listar servicios

> **Endpoint**

```curl
/v1/routes
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `100`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |

> **Ejemplo**

- Consulta

```curl
/v1/routes?limit=3
```

- Respuesta

```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 254,
    "total_pages": 254,
    "results": [
        {
            "route_long_name": "(M) Blanqueado - Mall Plaza Tobalaba",
            "end_date": "2018-03-31",
            "route_type": "3",
            "route_text_color": "000000",
            "agency_id": "TS",
            "route_id": "102",
            "route_color": "00D5FF",
            "route_desc": null,
            "directions": [
                {
                    "direction_id": 0,
                    "route_id": "102",
                    "direction_headsign": "Mall P. Tobalaba",
                    "direction_name": "Outbound"
                },
                {
                    "direction_id": 1,
                    "route_id": "102",
                    "direction_headsign": "(M) Blanqueado",
                    "direction_name": "Inbound"
                }
            ],
            "route_url": null,
            "route_short_name": "102",
            "start_date": "2017-11-07"
        },
        {
            "route_long_name": "Recoleta - Cerrillos",
            "end_date": "2018-03-31",
            "route_type": "3",
            "route_text_color": "000000",
            "agency_id": "TS",
            "route_id": "101",
            "route_color": "00D5FF",
            "route_desc": null,
            "directions": [
                {
                    "direction_id": 0,
                    "route_id": "101",
                    "direction_headsign": "Cerrillos",
                    "direction_name": "Outbound"
                },
                {
                    "direction_id": 1,
                    "route_id": "101",
                    "direction_headsign": "Recoleta",
                    "direction_name": "Inbound"
                }
            ],
            "route_url": null,
            "route_short_name": "101",
            "start_date": "2017-11-07"
        },
        {
            "route_long_name": "(M) Blanqueado - Cerrillos",
            "end_date": "2018-03-30",
            "route_type": "3",
            "route_text_color": "000000",
            "agency_id": "TS",
            "route_id": "101c",
            "route_color": "00D5FF",
            "route_desc": null,
            "directions": [
                {
                    "direction_id": 0,
                    "route_id": "101c",
                    "direction_headsign": "Cerrillos",
                    "direction_name": "Outbound"
                },
                {
                    "direction_id": 1,
                    "route_id": "101c",
                    "direction_headsign": "(M) Blanqueado",
                    "direction_name": "Inbound"
                }
            ],
            "route_url": null,
            "route_short_name": "101c",
            "start_date": "2017-11-07"
        }
    ],
    "page_size": 3
}
```


### Obtener ruta

> **Endpoint**

```curl
/v1/routes/<route_id>
```

> **Argumentos**

  - `{string} route_id`: identificador de ruta


> **Ejemplo**

- Consulta

```curl
/v1/routes/102
```

- Respuesta

```json
{
    "route_long_name": "(M) Blanqueado - Mall Plaza Tobalaba",
    "end_date": "2018-03-31",
    "route_type": "3",
    "route_text_color": "000000",
    "agency_id": "TS",
    "route_id": "102",
    "route_color": "00D5FF",
    "route_desc": null,
    "directions": [
        {
            "direction_id": 0,
            "route_id": "102",
            "direction_headsign": "Mall P. Tobalaba",
            "direction_name": "Outbound"
        },
        {
            "direction_id": 1,
            "route_id": "102",
            "direction_headsign": "(M) Blanqueado",
            "direction_name": "Inbound"
        }
    ],
    "route_url": null,
    "route_short_name": "102",
    "start_date": "2017-11-07"
}
```

## Trips (`Viajes`)

Viajes para cada servicio (`route`). Un viaje es una secuencia de dos o más paradas que se produce en una hora específica.

### Listar viajes

> **Endpoint**

```curl
/v1/trips
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `50`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |

> **Ejemplo**

- Consulta

```curl
/v1/trips?limit=3
```

- Respuesta

```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 4777,
    "total_pages": 4777,
    "results": [
        {
            "direction_id": "0",
            "start_time": "00:00:00",
            "route_id": "101",
            "frequency": {
                "start_time": "00:00:00",
                "headway_secs": 1200,
                "exact_times": false,
                "end_time": "01:00:00"
            },
            "trip_headsign": "Cerrillos",
            "end_time": "01:00:23",
            "service_id": "L_V35",
            "trip_len": 76,
            "trip_id": "101-I-L_V35-B00",
            "trip_short_name": null
        },
        {
            "direction_id": "0",
            "start_time": "00:00:00",
            "route_id": "101",
            "frequency": {
                "start_time": "05:30:00",
                "headway_secs": 600,
                "exact_times": false,
                "end_time": "06:30:00"
            },
            "trip_headsign": "Cerrillos",
            "end_time": "01:17:39",
            "service_id": "L_V35",
            "trip_len": 76,
            "trip_id": "101-I-L_V35-B02",
            "trip_short_name": null
        },
        {
            "direction_id": "0",
            "start_time": "00:00:00",
            "route_id": "101",
            "frequency": {
                "start_time": "06:30:00",
                "headway_secs": 600,
                "exact_times": false,
                "end_time": "08:30:00"
            },
            "trip_headsign": "Cerrillos",
            "end_time": "01:41:15",
            "service_id": "L_V35",
            "trip_len": 76,
            "trip_id": "101-I-L_V35-B03",
            "trip_short_name": null
        }
    ],
    "page_size": 3
}
```

### Obtener viaje

> **Endpoint**

```curl
/v1/trips/<trip_id>
```

> **Argumentos**

  - `{string} trip_id`: identificador de viaje


> **Ejemplo**

- Consulta

```curl
/v1/trips/101-I-L_V35-B00
```

- Respuesta

```json
{
    "direction_id": "0",
    "start_time": "00:00:00",
    "route_id": "101",
    "frequency": {
        "start_time": "00:00:00",
        "headway_secs": 1200,
        "exact_times": false,
        "end_time": "01:00:00"
    },
    "trip_headsign": "Cerrillos",
    "end_time": "01:00:23",
    "service_id": "L_V35",
    "trip_len": 76,
    "trip_id": "101-I-L_V35-B00",
    "trip_short_name": null
}
```

### Listar paraderos de viaje

> **Endpoint**

```curl
/v1/trips/<trip_id>/stops
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `50`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |

> **Ejemplo**

- Consulta

```curl
/v1/trips/101-I-L_V35-B00/stops?limit=3
```

- Respuesta

```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 38,
    "total_pages": 38,
    "results": [
        {
            "stop_lat": "-33.404553756",
            "stop_code": "PB1",
            "stop_lon": "-70.623095148",
            "agency_id": "TS",
            "stop_id": "PB1",
            "directions": [
                {
                    "direction_id": 0,
                    "direction_headsign": "Cerrillos",
                    "direction_name": "Outbound"
                },
                {
                    "direction_id": 1,
                    "direction_headsign": "El Salto",
                    "direction_name": "Inbound"
                }
            ],
            "stop_name": "PB1-Venezuela Esq. / Bolivia"
        },
        {
            "stop_lat": "-33.395523330",
            "stop_code": "PB10",
            "stop_lon": "-70.650770017",
            "agency_id": "TS",
            "stop_id": "PB10",
            "directions": [
                {
                    "direction_id": 0,
                    "direction_headsign": "Av. Departamental",
                    "direction_name": "Outbound"
                }
            ],
            "stop_name": "PB10-Avenida Dorsal Esq. / La Plata"
        },
        {
            "stop_lat": "-33.405162456",
            "stop_code": "PB108",
            "stop_lon": "-70.703977045",
            "agency_id": "TS",
            "stop_id": "PB108",
            "directions": [
                {
                    "direction_id": 0,
                    "direction_headsign": "Av. Departamental",
                    "direction_name": "Outbound"
                }
            ],
            "stop_name": "PB108-Parada 3 / Plaza Renca"
        }
    ],
    "page_size": 3
}
```

### Listar puntos de trayecto para viaje

`Shape` define las reglas para el trazado de las líneas en un mapa que representen las rutas de una organización de transporte público.

> **Endpoint**

```curl
/v1/trips/<trip_id>/shape
```

> **Ejemplo**

- Consulta

```curl
/v1/trips/101-I-L_V34-B00/shape
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

### Secuencia de detención para viaje

Horarios a los que un vehículo llega a una parada concreta y sale de ella en cada viaje.

> **Endpoint**

```curl
/v1/trips/<trip_id>/stop_times
```

> **Ejemplo**

- Consulta

```curl
/v1/trips/101-I-L_V34-B00/stop_times
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

## BIP Spots (`Puntos carga`)

Información sobre puntos carga tarjeta BIP

### Listar puntos de carga

> **Endpoint**

```curl
/v1/bip_spots
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `50`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |
| `center_lon` | `si` | `None`      | Longitud. Si se define, los resultados serán ordenados de más cercano a más lejano a este punto. Usar en conjunto con `center_lat`. Ejemplo: `-70.643562`      |
| `center_lat` | `si` | `None`      | Latitud. Si se define, los resultados serán ordenados de más cercano a más lejano a este punto. Usar en conjunto con `center_lon`. Ejemplo: `-33.491585`      |
| `radius` | `si` | `None`      | Radio en metros. Usar en conjunto con `center_lat` y `center_lon`. Si es definido, se mostrarán sólo los resultados dentro de ese radio (en relación al centro (center_lat` y `center_lon`))     |

> **Ejemplo**

- Consulta

```curl
/v1/bip_spots?limit=3
```

- Respuesta

```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 676,
    "total_pages": 676,
    "results": [
        {
            "bip_spot_code": "60",
            "bip_spot_fantasy_name": "PCMA60",
            "bip_spot_commune": "SANTIAGO",
            "bip_spot_lat": "-33.44272566",
            "bip_spot_lon": "-70.644872",
            "bip_spot_address": "AV. LIB. BERNARDO OHIGGINS 622",
            "bip_spot_entity": "Serviestado",
            "bip_opening_time": "Lun a Vie 8:00 a 19:00 Sab 9:00 a 17:00"
        },
        {
            "bip_spot_lat": "-33.486436",
            "bip_spot_code": "61",
            "bip_spot_fantasy_name": "PCMA61",
            "bip_spot_commune": "MAIPU",
            "bip_spot_lon": "-70.750752",
            "bip_spot_address": "AV. AMERICO VESPUCIO NORTE CALETERA ORIENTE 51",
            "bip_spot_entity": "Serviestado",
            "bip_opening_time": "Lun a Vie 8:00 a 19:00 Sab 9:00 a 17:00"
        },
        {
            "bip_spot_lat": "-33.5332983565256",
            "bip_spot_code": "64",
            "bip_spot_fantasy_name": "PCMA 64",
            "bip_spot_commune": "LA CISTERNA",
            "bip_spot_lon": "-70.6630693155897",
            "bip_spot_address": "GRAN AV. JOSE MIGUEL CARRERA 8496",
            "bip_spot_entity": "Serviestado",
            "bip_opening_time": "Lun a Vie 8:00 a 19:00 Sab 9:00 a 17:00"
        }
    ],
    "page_size": 3
}
```

### Obtener Punto de carga BIP

> **Endpoint**

```curl
/v1/bip_spots/<bip_spot_code>
```

> **Argumentos**

  - `{string} bip_spot_code`: identificador de Punto de carga


> **Ejemplo**

- Consulta

```curl
/v1/bip_spots/60
```

- Respuesta

```json
{
    "bip_spot_lat": "-33.44272566",
    "bip_spot_code": "60",
    "bip_spot_fantasy_name": "PCMA60",
    "bip_spot_commune": "SANTIAGO",
    "bip_spot_lon": "-70.644872",
    "bip_spot_address": "AV. LIB. BERNARDO OHIGGINS 622",
    "bip_spot_entity": "Serviestado",
    "bip_opening_time": "Lun a Vie 8:00 a 19:00 Sab 9:00 a 17:00"
}
```

## Buses

Información sobre buses del transantiago en operación. Esta información es obtenida en tiempo real utilizando el [Web Service de Posicionamiento](https://www.dtpm.cl/index.php/2013-04-24-14-09-09/datos-y-servicios) provisto por la dirección de transporte público metropolitano.


### Listar buses en operación

> **Endpoint**

```curl
/v1/buses
```

> **Query params**

| property  | opcional       | default         | description                                         |
| --------- | :-------:  | :-------------: | --------------------------------------------------- |
| `limit`  | `si`   | `50`       | Cantidad de resultados por página.               |
| `page`     | `si`   | `1` | Número de página |
| `center_lon` | `si` | `None`      | Longitud. Si se define, los resultados serán ordenados de más cercano a más lejano a este punto. Usar en conjunto con `center_lat`. Ejemplo: `-70.643562`      |
| `center_lat` | `si` | `None`      | Latitud. Si se define, los resultados serán ordenados de más cercano a más lejano a este punto. Usar en conjunto con `center_lon`. Ejemplo: `-33.491585`      |
| `radius` | `si` | `None`      | Radio en metros. Usar en conjunto con `center_lat` y `center_lon`. Si es definido, se mostrarán sólo los resultados dentro de ese radio (en relación al centro (center_lat` y `center_lon`))     |

> **Ejemplo**

- Consulta

```curl
/v1/buses?limit=3
```

- Respuesta

```json
{
    "has_next": true,
    "page_number": 1,
    "total_results": 903,
    "total_pages": 903,
    "results": [
        {
            "bus_plate_number": "BJFC-73",
            "operator_number": 5,
            "direction_id": 1,
            "bus_movement_orientation": 6,
            "added_at": "2017-11-11T17:23:26+00:00",
            "bus_lon": "-70.6349182128906",
            "route_id": "502",
            "bus_speed": 0,
            "bus_lat": "-33.4347496032715",
            "captured_at": "2017-11-11T17:23:21+00:00"
        },
        {
            "bus_plate_number": "ZB-6711",
            "operator_number": 4,
            "direction_id": 1,
            "bus_movement_orientation": 5,
            "added_at": "2017-11-11T17:23:16+00:00",
            "bus_lon": "-70.6487503051758",
            "route_id": "403",
            "bus_speed": 0,
            "bus_lat": "-33.4433441162109",
            "captured_at": "2017-11-11T17:23:09+00:00"
        },
        {
            "bus_plate_number": "CJRC-20",
            "operator_number": 9,
            "direction_id": 1,
            "bus_movement_orientation": 2,
            "added_at": "2017-11-11T17:23:11+00:00",
            "bus_lon": "-70.5545120239258",
            "route_id": "F06",
            "bus_speed": 0,
            "bus_lat": "-33.602611541748",
            "captured_at": "2017-11-11T17:23:06+00:00"
        }
    ],
    "page_size": 3
}
```

### Obtener bus

> **Endpoint**

```curl
/v1/buses/<bus_plate_number>
```

> **Argumentos**

  - `{string} bus_plate_number`: patente de bus


> **Ejemplo**

- Consulta

```curl
/v1/buses/BJFC-73
```

- Respuesta

```json
{
    "bus_plate_number": "BJFC-73",
    "operator_number": 5,
    "direction_id": 1,
    "bus_movement_orientation": 6,
    "added_at": "2017-11-11T17:23:26+00:00",
    "bus_lon": "-70.6349182128906",
    "route_id": "502",
    "bus_speed": 0,
    "bus_lat": "-33.4347496032715",
    "captured_at": "2017-11-11T17:23:21+00:00"
}
```
