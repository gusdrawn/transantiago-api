<p align="center">
    <a href="#">
        <img src="https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/shields/gtfs_version"
            alt="GTFS"></a>
    <a href="#">
        <img src="https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/shields/fetched_at"
            alt="Last fetch">
    </a>
</p>

!> **NOTA** Esta es una versión no estable de la API, se pueden introducir cambios profundos.

> ***Transantiago API*** es una API (no oficial) basada en la información [oficial](https://www.dtpm.cl/index.php/2013-04-24-14-10-40/gtfs-vigente) disponible de transantiago (formato "General Transit Feed Specification - GTFS). Información de servicios de buses y de Metro, posición de paraderos y estaciones, trazados de servicios y frecuencias y tiempos de viaje por periodo del día.

- [uso](#Uso)

---

## Características

- API REST (kinda)

  La API se basa en la arquitectura REST y no requiere autenticación.

- Operaciones extras sobre información

  Se proveen ciertas operaciones sobre la información original, como la opción de filtrar paraderos por cercanía a ubicación o mostrar tabla de siguiente horarios de paradas en paradero concreto (basada en tiempos de viaje previstos, no información "en tiempo real"). 

- Información sincronizada

  La información de la API es actualizada automáticamente si se generan cambios en la información de la fuente original (información oficial provista por transantiago). La información original puede ser obtenida [acá](https://www.dtpm.cl/index.php/2013-04-24-14-10-40/gtfs-vigente)

## Uso

Ver la [documentación](https://ignaciohermosilla.github.io/transantiago-api/#/api) para ver todos los endpoints disponibles. 

Aquí algunos ejemplos de uso:

- Obtener los paraderos (a.k.a `stops`) cercanos a cierta ubicación (ordenados por cercanía):

```
https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/api/v1/stops?lat=-33.491585&lon=-70.643562
```

- Obtener las rutas o "micros" de un paradero concreto:

```
https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/api/v1/stops/<stop_id>/routes
https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/api/v1/stops/PB1/routes
```

- Obtener la información de un viaje específico (a.k.a `trips`), incluyendo todos los paraderos de la ruta y la "micro" asociada.

```
https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/api/v1/trips/<trip_id>
https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/api/v1/trips/101-I-L_V34-B00
```

## Contribución

Este es un proyecto 100% opensource y por amor al arte. Cualquier colaboración es muy bienvenida.

