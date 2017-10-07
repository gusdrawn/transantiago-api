# -*- coding: utf-8 -*-

from falcon import testing
from scl_transport.api.models import (
    Stop,
    Agency,
    Route,
    StopTime,
    Trip,
    Service
)

from scl_transport.api.api import create_app
from scl_transport.database import Adapter, CombinedConnection, Model


class BaseTestCase(testing.TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()

        # connect to db for use by test
        self.cc = CombinedConnection()
        self.cc.create_db(Model)

        # clear all tables
        self.cc.clear_tables(Model)

        # open session
        self.session = self.cc.get_session()

        # create LEM adapter
        self.adapter = Adapter(connection=self.cc)
        # return a `falcon.API` instance.
        self.app = create_app()

    def tearDown(self):
        # close session and connection
        self.session.close()
        self.cc.close()

        # call super
        super(BaseTestCase, self).tearDown()

    def get(self, url, query_string=None):
        return self.simulate_get(url, query_string=query_string)

"""
    app.add_route('/v1/trips/', TripCollectionResource())
    app.add_route('/v1/trips/{trip_id}', TripResource())  # TODO: order by sequence
"""


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

        self.service = Service(
            service_id='L_V34',
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True,
            start_date=None,
            end_date=None
        )
        self.session.add(self.service)

        self.trip = Trip(
            trip_id='106-I-L_V34-B02',
            route_id=self.route.route_id,
            service_id=self.service.service_id,
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
        self.session.add(self.trip)
        self.session.commit()

    def test_collection(self):
        result = self.get('/v1/trips/106-I-L_V34-B02/stops')
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

        self.service = Service(
            service_id='L_V34',
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True,
            start_date=None,
            end_date=None
        )
        self.session.add(self.service)

        self.trip = Trip(
            trip_id='106-I-L_V34-B02',
            route_id=self.route.route_id,
            service_id=self.service.service_id,
            shape_id=None,
            trip_headsign='La Florida',
            direction_id='0'
        )

        self.session.add(self.trip)
        self.session.commit()

    def test_collection(self):
        result = self.get('/v1/trips')
        expected_json = {
            u'has_next': False,
            u'page_number': 1,
            u'page_size': 1,
            u'results': [{
                u'direction_id': u'0',
                u'frequency': None,
                u'route': {
                    u'agency_id': u'TS',
                    u'route_color': u'00D5FF',
                    u'route_desc': None,
                    u'route_id': u'106',
                    u'route_long_name': u'Nueva San Martin - La Florida',
                    u'route_short_name': u'106',
                    u'route_text_color': u'000000',
                    u'route_type': u'3',
                    u'route_url': None
                },
                u'service': {
                    u'end_date': None,
                    u'friday': True,
                    u'monday': True,
                    u'saturday': True,
                    u'service_id': u'L_V34',
                    u'start_date': None,
                    u'sunday': True,
                    u'thursday': True,
                    u'tuesday': True,
                    u'wednesday': True
                },
                u'trip_headsign': u'La Florida',
                u'trip_id': u'106-I-L_V34-B02'
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
            u'frequency': None,
            u'route': {
                u'agency_id': u'TS',
                u'route_color': u'00D5FF',
                u'route_desc': None,
                u'route_id': u'106',
                u'route_long_name': u'Nueva San Martin - La Florida',
                u'route_short_name': u'106',
                u'route_text_color': u'000000',
                u'route_type': u'3',
                u'route_url': None
            },
            u'service': {
                u'end_date': None,
                u'friday': True,
                u'monday': True,
                u'saturday': True,
                u'service_id': u'L_V34',
                u'start_date': None,
                u'sunday': True,
                u'thursday': True,
                u'tuesday': True,
                u'wednesday': True
            },
            u'trip_headsign': u'La Florida',
            u'trip_id': u'106-I-L_V34-B02'
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
                u'route_color': u'00D5FF',
                u'route_desc': None,
                u'route_id': u'106',
                u'route_long_name': u'Nueva San Martin - La Florida',
                u'route_short_name': u'106',
                u'route_text_color': u'000000',
                u'route_type': u'3',
                u'route_url': None
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
            u'route_color': u'00D5FF',
            u'route_desc': None,
            u'route_id': u'106',
            u'route_long_name': u'Nueva San Martin - La Florida',
            u'route_short_name': u'106',
            u'route_text_color': u'000000',
            u'route_type': u'3',
            u'route_url': None
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
                u'stop_code': u'PA1',
                u'stop_id': u'PA1',
                u'stop_lat': u'-33.4401169274166',
                u'stop_lon': u'-33.4401169274166',
                u'stop_name': u'PA1-Parada 6 / (M) Quinta Normal',
                u'stop_url': u'http://www.metro.cl/estacion/vicuna-mackenna-l4'
            }],
            u'total_pages': 1,
            u'total_results': 1
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, expected_json)

    def test_item(self):
        result = self.get('/v1/stops/PA1')
        expected_json = {
            u'stop_code': u'PA1',
            u'stop_id': u'PA1',
            u'stop_lat': u'-33.4401169274166',
            u'stop_lon': u'-33.4401169274166',
            u'stop_name': u'PA1-Parada 6 / (M) Quinta Normal',
            u'stop_url': u'http://www.metro.cl/estacion/vicuna-mackenna-l4'
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

        self.service = Service(
            service_id='L_V34',
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True,
            start_date=None,
            end_date=None
        )
        self.session.add(self.service)

        self.trip = Trip(
            trip_id='106-I-L_V34-B02',
            route_id=self.route.route_id,
            service_id=self.service.service_id,
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
        result = self.get('/v1/stops/PA1/routes')
        self.assertEqual(result.status_code, 200)
        expected_json = {
            u'results': [{
                u'agency_id': u'TS',
                u'route_color': u'00D5FF',
                u'route_desc': None,
                u'route_id': u'106',
                u'route_long_name': u'Nueva San Martin - La Florida',
                u'route_short_name': u'106',
                u'route_text_color': u'000000',
                u'route_type': u'3',
                u'route_url': None
            }]
        }
        self.assertEqual(result.json, expected_json)


class HealthCheckTestCase(BaseTestCase):
    def test_success(self):
        result = self.get('/v1/ping')
        self.assertEqual(result.status_code, 200)
