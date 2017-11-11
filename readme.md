<p align="center">
    <a href="#">
        <img src="https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/shields/gtfs_version"
            alt="GTFS"></a>
    <a href="#">
        <img src="https://txgr7z1gbc.execute-api.eu-west-2.amazonaws.com/dev/shields/fetched_at"
            alt="Last fetch">
    </a>
</p>

!> **NOTA** Esta es una API en proceso temprano de desarrollo, se pueden introducir cambios profundos.

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

Ver la [documentación](http://scltrans.it/#/api) para ver todos los endpoints disponibles. 

Aquí algunos ejemplos de uso:

- Listar los paraderos (a.k.a `stops`) cercanos a cierta ubicación (ordenados por cercanía).:

```
https://api.scltrans.it/v1/stops?center_lat=-33.491585&center_lon=-70.643562
```

- Listar los paraderos activos en un área (bounding box)

```
https://api.scltrans.it/v1/stops?bbox=-70.609818,-33.442328,-70.566473,-33.409806&is_active=1
```

- Listar las rutas o "micros" del paradero PB1:

```
https://api.scltrans.it/v1/stops/PB1/routes
```

- Obtener información sobre los próximos arrivos en el paradero PB1:

```
https://api.scltrans.it/v1/stops/PB1/next_arrivals
```

- Obtener la información de un viaje específico (a.k.a `trips`), incluyendo todos los paraderos de la ruta y la "micro" asociada.

```
https://api.scltrans.it/v1/trips/101-I-L_V34-B00
```

- Obtener la información de trazado del viaje 101-I-L_V34-B00:

```
https://api.scltrans.it/v1/trips/101-I-L_V34-B00/shape
```

- Listar los puntos de carga bip en área específica (bounding box):

```
https://api.scltrans.it/v1/bip_spots?bbox=-70.609818,-33.442328,-70.566473,-33.409806
``` 


## Contribución

Este es un proyecto 100% opensource y por amor al arte. Cualquier colaboración es muy bienvenida.
