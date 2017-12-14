# -*- coding: utf-8 -*-
import os

import arrow
import requests
from decimal import Decimal

RECORD_FIELDS = [
    'captured_at',  # Fecha Hora Gps UTC (Alfanumérico) -> 03-11-2017 11:00:22
    'bus_plate_number',  # 'Patente (Alfanumérico)' -> BJFC-73
    'latitud',  # Latitud -33.4332656860352
    'longitud',  # longitud -70.6573715209961
    'vehicle_speed',  # velocidad_instantanea (km/hr) 13.0
    'vehicle_movement_orientation',  # 'Dirección Geográfica Movimiento del bus (0-7)', 2.0
    'operator_number',  # Número de Operador 5.0
    'original_route_id',  # Nombre Comercial del Servicio T502
    'direction_id',  #  Sentido <>(Alfabético), I-Ida, R-Retorno (vacio)', # I  (TODO: process to inbound/outbound and check)
    'console_route_id', # T502 00I ruta asignada por consola
    'synoptic_route_id', # T502 00I ruta asignada por
    'added_at' # Fecha Hora de inserción UTC'  # 03-11-2017 11:00:27
]

NUM_OF_RECORDS = len(RECORD_FIELDS)

DIRECTION_MAPPING = {
    'I': 0,
    'R': 1,
}


class BusInfo(object):
    def __init__(self, input_fields, route_decoder):
        self.input_fields = input_fields
        self.route_decoder = route_decoder

    @property
    def captured_at(self):
        try:
            return arrow.get(self.input_fields[0], 'DD-MM-YYYY HH:mm:ss').datetime
        except:
            return None

    @property
    def bus_plate_number(self):
        return self.input_fields[1]

    @property
    def bus_lat(self):
        return self.input_fields[2]

    @property
    def bus_lon(self):
        return self.input_fields[3]

    @property
    def bus_speed(self):
        return Decimal(self.input_fields[4])

    @property
    def bus_movement_orientation(self):
        return int(Decimal(self.input_fields[5]))

    @property
    def operator_number(self):
        return int(Decimal(self.input_fields[6]))

    @property
    def original_route_id(self):
        original_route_id = self.input_fields[7].upper()
        if original_route_id.startswith('T'):
            original_route_id = original_route_id[1:]
        if self.route_decoder.get(original_route_id):
            return self.route_decoder[original_route_id]
        return original_route_id

    @property
    def direction_id(self):
        direction = self.input_fields[8]
        if direction not in DIRECTION_MAPPING.keys():
            return None
        return DIRECTION_MAPPING.get(direction)

    @property
    def console_route_id(self):
        return self.input_fields[9]

    @property
    def synoptic_route_id(self):
        return self.input_fields[10]

    @property
    def added_at(self):
        try:
            return arrow.get(self.input_fields[11], 'DD-MM-YYYY HH:mm:ss').datetime
        except:
            return None

    def as_dict(self):
        return {
            'captured_at': self.captured_at,
            'bus_plate_number': self.bus_plate_number,
            'bus_lat': self.bus_lat,
            'bus_lon': self.bus_lon,
            'bus_speed': self.bus_speed,
            'bus_movement_orientation': self.bus_movement_orientation,
            'operator_number': self.operator_number,
            'original_route_id': self.original_route_id,
            'console_route_id': self.console_route_id,
            'synoptic_route_id': self.synoptic_route_id,
            'direction_id': self.direction_id,
            'added_at': self.added_at
        }


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class PositioningFetcher(object):
    _input_data = None
    _route_decoder = None

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @property
    def route_decoder(self):
        if not self._route_decoder:
            with open(os.path.join(__location__, 'serviciosdeco.txt'), 'r') as f:
                decoder_lines = f.read().splitlines()
            route_decoder = {}
            for decoder_line in decoder_lines:
                real_route_id, original_route_id, _ = decoder_line.split(',')
                route_decoder[original_route_id] = real_route_id
            self._route_decoder = route_decoder
        return self._route_decoder

    def _process_line(self, line):
        line_lenght = len(line.split(';'))
        if (line_lenght - 1) % NUM_OF_RECORDS:
            raise Exception("invalid input line")
        line = line.rstrip(";")  # clean character
        line_fields = line.split(';')
        line_lenght = len(line.split(';'))
        results = []
        for i in range(0, line_lenght, NUM_OF_RECORDS):
            b_i = BusInfo(line_fields[i:i + NUM_OF_RECORDS], route_decoder=self.route_decoder)
            results.append(b_i.as_dict())
        if not results:
            return []
        return results[-1]  # get latest sample, @@TODO: check datetime

    @property
    def input_data(self):
        if not self._input_data:
            r = requests.get('https://www.dtpmetropolitano.cl/posiciones', auth=(self.username, self.password), verify=False)
            self._input_data = r.json()
        return self._input_data

    def get_results(self):
        results = []
        for line in self.input_data['posiciones']:
            bus_position = self._process_line(line)
            results.append(bus_position)
        return results
