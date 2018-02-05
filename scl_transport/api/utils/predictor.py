import zeep
from zeep.cache import Base
from zeep.transports import Transport
from requests import Session

import random
import logging
import os
log = logging.getLogger(__name__)

CHARACTERS = 'abcdefghjklmnpqrstuvwxyz23456789'

OPERATION_TIMEOUT = 10


class PermanentCache(Base):
    _cache = {
        'http://ws13.smsbus.cl:8080/wspatentedos/services/PredictorParaderoServicioWS?WSDL': '<?xml version="1.0" encoding="UTF-8"?>\n<wsdl:definitions targetNamespace="http://predParaderoServicioWS.ws.simtws.wirelessiq.cl" xmlns:apachesoap="http://xml.apache.org/xml-soap" xmlns:impl="http://predParaderoServicioWS.ws.simtws.wirelessiq.cl" xmlns:intf="http://predParaderoServicioWS.ws.simtws.wirelessiq.cl" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:wsdlsoap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n<!--WSDL created by Apache Axis version: 1.4\nBuilt on Apr 22, 2006 (06:55:48 PDT)-->\n <wsdl:types>\n  <schema elementFormDefault="qualified" targetNamespace="http://predParaderoServicioWS.ws.simtws.wirelessiq.cl" xmlns="http://www.w3.org/2001/XMLSchema">\n <element name="predictorParaderoServicio">\n  <complexType>\n   <sequence>\n  <element name="paradero" type="xsd:string"/>\n  <element name="servicio" type="xsd:string"/>\n  <element name="cliente" type="xsd:int"/>\n  <element name="resolucion" type="xsd:string"/>\n  <element name="ipUsuarioFinal" type="xsd:string"/>\n  <element name="webTransId" type="xsd:string"/>\n   </sequence>\n  </complexType>\n </element>\n <element name="predictorParaderoServicioResponse">\n  <complexType>\n   <sequence>\n  <element name="predictorParaderoServicioReturn" type="impl:Result"/>\n   </sequence>\n  </complexType>\n </element>\n <complexType name="Servicios">\n  <sequence>\n   <element name="codigorespuesta" nillable="true" type="xsd:string"/>\n   <element name="distanciabus1" nillable="true" type="xsd:string"/>\n   <element name="distanciabus2" nillable="true" type="xsd:string"/>\n   <element name="horaprediccionbus1" nillable="true" type="xsd:string"/>\n   <element name="horaprediccionbus2" nillable="true" type="xsd:string"/>\n   <element name="ppubus1" nillable="true" type="xsd:string"/>\n   <element name="ppubus2" nillable="true" type="xsd:string"/>\n   <element name="respuestaServicio" nillable="true" type="xsd:string"/>\n   <element name="servicio" nillable="true" type="xsd:string"/>\n  </sequence>\n </complexType>\n <complexType name="ArrayOfServicios">\n  <sequence>\n   <element maxOccurs="unbounded" minOccurs="0" name="item" type="impl:Servicios"/>\n  </sequence>\n </complexType>\n <complexType name="Result">\n  <sequence>\n   <element name="fechaprediccion" nillable="true" type="xsd:string"/>\n   <element name="horaprediccion" nillable="true" type="xsd:string"/>\n   <element name="nomett" nillable="true" type="xsd:string"/>\n   <element name="paradero" nillable="true" type="xsd:string"/>\n   <element name="respuestaParadero" nillable="true" type="xsd:string"/>\n   <element name="servicios" nillable="true" type="impl:ArrayOfServicios"/>\n   <element name="urlLinkPublicidad" nillable="true" type="xsd:string"/>\n   <element name="urlPublicidad" nillable="true" type="xsd:string"/>\n  </sequence>\n </complexType>\n  </schema>\n </wsdl:types>\n\n <wsdl:message name="predictorParaderoServicioRequest">\n\n  <wsdl:part element="impl:predictorParaderoServicio" name="parameters">\n\n  </wsdl:part>\n\n </wsdl:message>\n\n <wsdl:message name="predictorParaderoServicioResponse">\n\n  <wsdl:part element="impl:predictorParaderoServicioResponse" name="parameters">\n\n  </wsdl:part>\n\n </wsdl:message>\n\n <wsdl:portType name="PredictorParaderoServicioWS">\n\n  <wsdl:operation name="predictorParaderoServicio">\n\n   <wsdl:input message="impl:predictorParaderoServicioRequest" name="predictorParaderoServicioRequest">\n\n   </wsdl:input>\n\n   <wsdl:output message="impl:predictorParaderoServicioResponse" name="predictorParaderoServicioResponse">\n\n   </wsdl:output>\n\n  </wsdl:operation>\n\n </wsdl:portType>\n\n <wsdl:binding name="PredictorParaderoServicioWSSoapBinding" type="impl:PredictorParaderoServicioWS">\n\n  <wsdlsoap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>\n\n  <wsdl:operation name="predictorParaderoServicio">\n\n   <wsdlsoap:operation soapAction=""/>\n\n   <wsdl:input name="predictorParaderoServicioRequest">\n\n    <wsdlsoap:body use="literal"/>\n\n   </wsdl:input>\n\n   <wsdl:output name="predictorParaderoServicioResponse">\n\n    <wsdlsoap:body use="literal"/>\n\n   </wsdl:output>\n\n  </wsdl:operation>\n\n </wsdl:binding>\n\n <wsdl:service name="PredictorParaderoServicioWSService">\n\n  <wsdl:port binding="impl:PredictorParaderoServicioWSSoapBinding" name="PredictorParaderoServicioWS">\n\n   <wsdlsoap:address location="http://ws13.smsbus.cl:8080/wspatentedos/services/PredictorParaderoServicioWS"/>\n\n  </wsdl:port>\n\n </wsdl:service>\n\n</wsdl:definitions>\n'
    }

    def __init__(self, timeout=3600):
        self._timeout = timeout

    def add(self, url, content):
        pass

    def get(self, url):
        return self._cache[url]


session = Session()
session.verify = False
transport = Transport(session=session, cache=PermanentCache(), timeout=10, operation_timeout=OPERATION_TIMEOUT)


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
            self._client = zeep.Client(wsdl=os.getenv('PREDICTOR_WS_CLIENT_WSDL'), transport=transport)
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
