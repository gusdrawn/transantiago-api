# -*- coding: utf-8 -*-

import os
import logging
import arrow
from falcon import testing
from scl_transport.gtfsdb.gtfsdb import (
    Stop,
    Agency,
    Route,
    StopTime,
    RouteStop,
    Trip,
)
from scl_transport.api.api import create_app
from scl_transport.gtfsdb.gtfsdb import Database
from scl_transport.gtfsdb.gtfsdb.settings import config


class BaseTestCase(testing.TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        kwargs = {'url': config.DEFAULT_DATABASE_URL}
        self.db = Database(**kwargs)
        self.session = self.db.session
        # createdb
        self.db.create()
        self.app = create_app()
        logging.disable(logging.DEBUG)

        # return a `falcon.API` instance.
        self.app = create_app()

    def tearDown(self):
        # close session and connection
        self.session.close()
        # call super
        super(BaseTestCase, self).tearDown()

    def get(self, url, query_string=None):
        return self.simulate_get(url, query_string=query_string)


class TripStopsTestCase(BaseTestCase):
    def setUp(self):
        super(TripStopsTestCase, self).setUp()

        self.agency = Agency(
            agency_id='TS',
            agency_name='Transantiago',
            agency_url='http://www.transantiago.cl',
            agency_timezone='America/Santiago'
        )
        self.session.add(self.agency)

        self.stop = Stop(
            stop_id='PA1',
            stop_code='PA1',
            stop_name='PA1-Parada 6 / (M) Quinta Normal',
            stop_lat='-33.4401169274166',
            stop_lon='-33.4401169274166',
            stop_url='http://www.metro.cl/estacion/vicuna-mackenna-l4'
        )
        self.session.add(self.stop)

        self.route = Route(
            route_id='106',
            agency_id='TS',
            route_short_name='106',
            route_long_name='Nueva San Martin - La Florida',
            route_type='3',
            route_color='00D5FF',
            route_text_color='000000'

        )
        self.session.add(self.route)

        self.trip_id = '106-I-L_V34-B02'

        self.trip = Trip(
            trip_id=self.trip_id,
            route_id=self.route.route_id,
            service_id='TS',
            shape_id=None,
            trip_headsign='La Florida',
            direction_id='0'
        )
        self.session.add(self.trip)

        self.stop_time = StopTime(
            trip_id=self.trip_id,
            arrival_time=None,
            departure_time=None,
            stop_id=self.stop.stop_id,
            stop_sequence=1
        )
        self.session.add(self.trip)
        self.session.add(self.stop_time)
        self.session.commit()

    def test_collection(self):
        result = self.get('/v1/trips/{}/stops'.format(self.trip_id))
        self.assertEqual(result.status_code, 200)


class TripsTestCase(BaseTestCase):
    def setUp(self):
        super(TripsTestCase, self).setUp()
        self.agency = Agency(
            agency_id='TS',
            agency_name='Transantiago',
            agency_url='http://www.transantiago.cl',
            agency_timezone='America/Santiago'
        )
        self.session.add(self.agency)

        self.stop = Stop(
            stop_id='PA1',
            stop_code='PA1',
            stop_name='PA1-Parada 6 / (M) Quinta Normal',
            stop_lat='-33.4401169274166',
            stop_lon='-33.4401169274166',
            stop_url='http://www.metro.cl/estacion/vicuna-mackenna-l4'
        )
        self.session.add(self.stop)

        self.route = Route(
            route_id='106',
            agency_id='TS',
            route_short_name='106',
            route_long_name='Nueva San Martin - La Florida',
            route_type='3',
            route_color='00D5FF',
            route_text_color='000000'

        )
        self.session.add(self.route)
        self.trip = Trip(
            trip_id='106-I-L_V34-B02',
            route_id=self.route.route_id,
            service_id='L_V34',
            shape_id=None,
            trip_headsign='La Florida',
            direction_id='0'
        )

        self.stop_time = StopTime(
            trip_id='106-I-L_V34-B02',
            arrival_time=None,
            departure_time=None,
            stop_id='PA1',
            stop_sequence=1
        )

        self.session.add(self.trip)
        self.session.add(self.stop_time)
        self.session.commit()

    def test_collection(self):
        result = self.get('/v1/trips')
        expected_json = {
            u'has_next': False,
            u'page_number': 1,
            u'page_size': 1,
            u'results': [{
                u'direction_id': u'0',
                u'end_time': None,
                u'frequency': None,
                u'route_id': u'106',
                u'service_id': u'L_V34',
                u'start_time': None,
                u'trip_headsign': u'La Florida',
                u'trip_id': u'106-I-L_V34-B02',
                u'trip_len': 1,
                u'trip_short_name': None
            }],
            u'total_pages': 1,
            u'total_results': 1
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, expected_json)

    def test_item(self):
        result = self.get('/v1/trips/106-I-L_V34-B02')
        expected_json = {
            u'direction_id': u'0',
            u'end_time': None,
            u'frequency': None,
            u'route_id': u'106',
            u'service_id': u'L_V34',
            u'start_time': None,
            u'trip_headsign': u'La Florida',
            u'trip_id': u'106-I-L_V34-B02',
            u'trip_len': 1,
            u'trip_short_name': None
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, expected_json)


class RoutesTestCase(BaseTestCase):
    def setUp(self):
        super(RoutesTestCase, self).setUp()
        self.stop = Stop(
            stop_id='PA1',
            stop_code='PA1',
            stop_name='PA1-Parada 6 / (M) Quinta Normal',
            stop_lat='-33.4401169274166',
            stop_lon='-33.4401169274166',
            stop_url='http://www.metro.cl/estacion/vicuna-mackenna-l4'
        )
        self.agency = Agency(
            agency_id='TS',
            agency_name='Transantiago',
            agency_url='http://www.transantiago.cl',
            agency_timezone='America/Santiago'
        )
        self.session.add(self.agency)
        self.session.add(self.stop)
        self.route = Route(
            route_id='106',
            agency_id=self.agency.agency_id,
            route_short_name='106',
            route_long_name='Nueva San Martin - La Florida',
            route_type='3',
            route_color='00D5FF',
            route_text_color='000000'

        )
        self.session.add(self.route)
        self.session.commit()

    def test_collection(self):
        result = self.get('/v1/routes')

        expected_json = {
            u'has_next': False,
            u'page_number': 1,
            u'page_size': 1,
            u'results': [{
                u'agency_id': u'TS',
                u'directions': [],
                u'end_date': None,
                u'route_color': u'00D5FF',
                u'route_desc': None,
                u'route_id': u'106',
                u'route_long_name': u'Nueva San Martin - La Florida',
                u'route_short_name': u'106',
                u'route_text_color': u'000000',
                u'route_type': u'3',
                u'route_url': None,
                u'start_date': None
            }],
            u'total_pages': 1,
            u'total_results': 1
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, expected_json)

    def test_item(self):
        result = self.get('/v1/routes/106')
        expected_json = {
            u'agency_id': u'TS',
            u'directions': [],
            u'end_date': None,
            u'route_color': u'00D5FF',
            u'route_desc': None,
            u'route_id': u'106',
            u'route_long_name': u'Nueva San Martin - La Florida',
            u'route_short_name': u'106',
            u'route_text_color': u'000000',
            u'route_type': u'3',
            u'route_url': None,
            u'start_date': None
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, expected_json)


class StopsTestCase(BaseTestCase):

    def setUp(self):
        super(StopsTestCase, self).setUp()

        self.stop = Stop(
            stop_id='PA1',
            stop_code='PA1',
            stop_name='PA1-Parada 6 / (M) Quinta Normal',
            stop_lat='-33.4401169274166',
            stop_lon='-33.4401169274166',
            stop_url='http://www.metro.cl/estacion/vicuna-mackenna-l4'
        )
        self.session.add(self.stop)
        self.session.commit()

    def test_collection(self):
        result = self.get('/v1/stops')
        expected_json = {
            u'has_next': False,
            u'page_number': 1,
            u'page_size': 1,
            u'results': [{
                u'agency_id': None,
                u'stop_code': u'PA1',
                u'stop_id': u'PA1',
                u'stop_lat': u'-33.440116927',
                u'stop_lon': u'-33.440116927',
                u'stop_name': u'PA1-Parada 6 / (M) Quinta Normal'
            }],
            u'total_pages': 1,
            u'total_results': 1
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, expected_json)

    def test_item(self):
        result = self.get('/v1/stops/PA1')
        expected_json = {
            u'agency_id': None,
            u'stop_code': u'PA1',
            u'stop_id': u'PA1',
            u'stop_lat': u'-33.440116927',
            u'stop_lon': u'-33.440116927',
            u'stop_name': u'PA1-Parada 6 / (M) Quinta Normal'
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, expected_json)


class StopRoutesTestCase(BaseTestCase):
    def setUp(self):
        super(StopRoutesTestCase, self).setUp()

        self.agency = Agency(
            agency_id='TS',
            agency_name='Transantiago',
            agency_url='http://www.transantiago.cl',
            agency_timezone='America/Santiago'
        )
        self.session.add(self.agency)

        self.stop = Stop(
            stop_id='PA1',
            stop_code='PA1',
            stop_name='PA1-Parada 6 / (M) Quinta Normal',
            stop_lat='-33.4401169274166',
            stop_lon='-33.4401169274166',
            stop_url='http://www.metro.cl/estacion/vicuna-mackenna-l4'
        )
        self.session.add(self.stop)

        self.route = Route(
            route_id='106',
            agency_id='TS',
            route_short_name='106',
            route_long_name='Nueva San Martin - La Florida',
            route_type='3',
            route_color='00D5FF',
            route_text_color='000000'

        )
        self.session.add(self.route)

        self.route_stop = RouteStop(
            route_id=self.route.route_id,
            direction_id=0,
            stop_id=self.stop.stop_id,
            order=1,
            start_date=arrow.now().date(),
            end_date=arrow.now().date(),
        )
        self.session.add(self.route_stop)

        self.trip = Trip(
            trip_id='106-I-L_V34-B02',
            route_id=self.route.route_id,
            service_id='L_V34',
            shape_id=None,
            trip_headsign='La Florida',
            direction_id='0'
        )
        self.session.add(self.trip)

        self.stop_time = StopTime(
            trip_id='106-I-L_V34-B02',
            arrival_time=None,
            departure_time=None,
            stop_id=self.stop.stop_id,
            stop_sequence=1
        )
        self.session.add(self.stop_time)
        self.session.commit()

    def test_collection(self):
        result = self.get('/v1/stops/PA1/stop_routes')
        self.assertEqual(result.status_code, 200)
        expected_json = [{
            u'direction': None,
            u'route': {
                u'agency_id': u'TS',
                u'directions': [],
                u'end_date': None,
                u'route_color': u'00D5FF',
                u'route_desc': None,
                u'route_id': u'106',
                u'route_long_name': u'Nueva San Martin - La Florida',
                u'route_short_name': u'106',
                u'route_text_color': u'000000',
                u'route_type': u'3',
                u'route_url': None,
                u'start_date': None
            }
        }]
        self.assertEqual(result.json, expected_json)


class HealthCheckTestCase(BaseTestCase):
    def test_success(self):
        result = self.get('/v1/ping')
        self.assertEqual(result.status_code, 200)
