import zeep
import random
import logging
import os
log = logging.getLogger(__name__)

CHARACTERS = 'abcdefghjklmnpqrstuvwxyz23456789'

"""
Serializers
"""


class BaseSerializer(object):
    def __init__(self, data):
        self.data = data


class MultipleRouteInfo(BaseSerializer):
    def get(self):
        return [
            {
                'bus_distance': self.data['distanciabus1'],
                'route_arrival_prediction': self.data['horaprediccionbus1'],
                'bus_plate_number': self.data['ppubus1'],
                'route_id': self.data['servicio'],
                'code': self.data['codigorespuesta'],
                'message': self.data['respuestaServicio']
            },
            {
                'bus_distance': self.data['distanciabus2'],
                'route_arrival_prediction': self.data['horaprediccionbus2'],
                'bus_plate_number': self.data['ppubus2'],
                'route_id': self.data['servicio'],
                'code': self.data['codigorespuesta'],
                'message': self.data['respuestaServicio']
            }
        ]


class SingleRouteInfo(BaseSerializer):
    def get(self):
        return [
            {
                'bus_distance': self.data['distanciabus1'],
                'route_arrival_prediction': self.data['horaprediccionbus1'],
                'bus_plate_number': self.data['ppubus1'],
                'route_id': self.data['servicio'],
                'code': self.data['codigorespuesta'],
                'message': self.data['respuestaServicio']
            }
        ]


class RouteFrequencyInfo(BaseSerializer):
    def get(self):
        return [
            {
                'bus_distance': None,
                'route_arrival_prediction': self.data['respuestaServicio'],
                'bus_plate_number': None,
                'route_id': self.data['servicio'],
                'code': self.data['codigorespuesta'],
                'message': self.data['respuestaServicio']
            },
        ]


class NoRoutesInfo(BaseSerializer):
    def get(self):
        return [
            {
                'bus_distance': None,
                'route_arrival_prediction': None,
                'bus_plate_number': None,
                'route_id': self.data['servicio'],
                'code': self.data['codigorespuesta'],
                'message': 'No hay buses que se dirijan al paradero'
            },
        ]


class ClosedStopInfo(BaseSerializer):
    def get(self):
        return [
            {
                'bus_distance': None,
                'route_arrival_prediction': None,
                'bus_plate_number': None,
                'route_id': self.data['servicio'],
                'code': self.data['codigorespuesta'],
                'message': 'Servicio fuera de horario de operacion para ese paradero'
            },
        ]


class NotAvailableService(BaseSerializer):
    def get(self):
        return [
            {
                'bus_distance': None,
                'route_arrival_prediction': None,
                'bus_plate_number': None,
                'route_id': self.data['servicio'],
                'code': self.data['codigorespuesta'],
                'message': 'Servicio no disponible'
            },
        ]


SERIALIZER_MAP = {
    '00': MultipleRouteInfo,
    '01': SingleRouteInfo,
    '9': RouteFrequencyInfo,
    '10': NoRoutesInfo,
    '11': ClosedStopInfo,
    '12': NotAvailableService,
}


#
RESPONSE_PRIORITY = ['00', '01', '9', '10', '11', '12']


class Predictor(object):
    _client = None

    def __init__(self, client_id, resolution, registered_IP):
        self.client_id = client_id
        self.resolution = resolution
        self.registered_IP = registered_IP

    @property
    def client(self):
        if not self._client:
            self._client = zeep.Client(wsdl=os.getenv('PREDICTOR_WS_CLIENT_WSDL'))
        return self._client

    @property
    def web_transit_ID(self):
        random_string = ''.join([random.choice(CHARACTERS).upper() for x in range(20)])
        return '{prefix}{random_string}'.format(
            prefix=os.getenv('PREDICTOR_WS_CLIENT_PREFIX'),
            random_string=random_string
        )

    def _request_data(self, stop_code, route_id=''):
        return self.client.service.predictorParaderoServicio(
            paradero=stop_code,
            servicio='',
            cliente=self.client_id,
            resolucion=self.resolution,
            ipUsuarioFinal=self.registered_IP,
            webTransId=self.web_transit_ID
        )

    def get(self, stop_code, route_id=''):
        input_data = self._request_data(stop_code, route_id)
        # serialize base info
        data = {
            'stop_name': input_data['nomett'],
            'stop_code': input_data['paradero'],
            'message': input_data['respuestaParadero']
        }
        data['calculated_at'] = '{} {}'.format(input_data['fechaprediccion'], input_data['horaprediccion'])

        response_items = {}
        # serialize reponse items
        for service_item in input_data['servicios']['item']:
            if service_item['codigorespuesta'] in SERIALIZER_MAP.keys():
                serializer = SERIALIZER_MAP[service_item['codigorespuesta']]
                if not response_items.get(service_item['codigorespuesta']):
                    response_items[service_item['codigorespuesta']] = []
                response_items[service_item['codigorespuesta']].extend(serializer(service_item).get())

        # merge response items
        data_items = []
        for item_name in RESPONSE_PRIORITY:
            items = response_items.get(item_name)
            if not items:
                continue
            # inject
            for item in items:
                item['calculated_at'] = data['calculated_at']
            data_items.extend(items)

        data['routes'] = data_items
        return data
