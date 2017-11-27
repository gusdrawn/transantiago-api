<p align="center">
    <a href="#">
        <img src="https://api.scltrans.it/shields/gtfs_version"
            alt="GTFS"></a>
    <a href="#">
        <img src="https://api.scltrans.it/shields/fetched_at"
            alt="Last fetch">
    </a>
</p>

# Transantiago API

> ***Transantiago API*** es una API no oficial basada en la información [oficial](#fuentes-de-datos) disponible de Transantiago. Información de servicios de buses y de Metro, posición de paraderos y estaciones, trazados de servicios y frecuencias y tiempos de viaje por periodo del día.

- [Información disponible](#información-disponible)
- [Fuentes de datos](#fuentes-de-datos)
- [Sobre la API](#sobre-la-api)
- [Ejemplos](#ejemplos)
- [uso](#Uso)

## Información disponible

* Recorridos [*ver*](http://scltrans.it/#/api?id=routes-servicios)
* Paraderos y estaciones de metro [*ver*](http://scltrans.it/#/api?id=stops-paraderos)
* Predicción de tiempos de arribo en paradero (tiempo real) [*ver*](http://scltrans.it/#/api?id=estimaci%c3%b3n-de-pr%c3%b3ximos-arribos)
* Itinerarios y horarios [*ver*](http://scltrans.it/#/api?id=secuencia-de-detenci%c3%b3n-para-viaje)
* Viajes [*ver*](http://scltrans.it/#/api?id=trips-viajes)
* Posición de buses (tiempo real) [*ver*](http://scltrans.it/#/api?id=buses)
* Puntos de carga BIP [*ver*](http://scltrans.it/#/api?id=bip-spots-puntos-carga)

## Fuentes de datos

Actualmente la API utiliza 4 fuentes de datos:

1. **GTFS**: Se utiliza el feed oficial GTFS ("General Transit Feed Specification - GTFS) provisto por la dirección de transporte Público Metropolitano. [Aquí](https://www.dtpm.cl/descargas/gtfs/GTFS.zip) puedes ver y descarga la última versión disponible. Esta información es verificada y actualizada internamente cada 12 horas. Toda la información estática (excluyendo los puntos de carga BIP) se basa en este feed.

2. **Webservice API SMSBUS**: Para obtener información sobre los [tiempos de llegada](http://scltrans.it/#/api?id=estimaci%c3%b3n-de-pr%c3%b3ximos-arribos) en un paradero, se utiliza el sistema de información Móvil para Transantiago (SMSBUS). Cuando se realiza una solicitud a la API, el sistema obtiene y procesa la información provista por este webservice.

3. **Webservice oficial de posicionamiento**: Para obtener información en relación a la [posición de los buses](http://scltrans.it/#/api?id=buses) del transantiago, se utiliza el Webservice oficial provisto por DTMP. [Aquí](https://www.dtpm.cl/index.php/2013-04-24-14-09-09/datos-y-servicios) puedes obtener más información. La información en relación a los buses es actualizada 1 vez por minuto.

4. **Portal abiertos de datos**: Para la información relacionada con los puntos de carga BIP, se utilizan los datos disponibles en el portal de datos abiertos del gobierno. [Aquí](http://datos.gob.cl/dataset?q=puntos+de+carga&organization=subsecretaria_de_transporte&sort=score+desc%2C+metadata_modified+desc) puedes ver la información disponible.



## Sobre la API

- **API abierta**

  La API está disponible en **https://api.scltrans.it**. Puedes revisar documentación [áca](http://scltrans.it/#/api). La API no require autenticación y puede ser utilizada libremente.

- **Operaciones extras sobre información**

  Se proveen ciertas operadores sobre la información, como filtros de geolocalización o filtros de fuentes. Para más información revisa la [documentación](http://scltrans.it/#/api).

- **Información sincronizada**

  La información de la API es actualizada automáticamente si se generan cambios en la información de la fuente original.

## Ejemplos

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

- Obtener información sobre los próximos arribos en el paradero PB1:

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

Este es un proyecto 100% opensource y por amor al arte. Cualquier colaboración es muy bienvenida. Especialmente sugerencias y reporte de errores.
