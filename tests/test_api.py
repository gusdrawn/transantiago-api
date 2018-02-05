# -*- coding: utf-8 -*-

import logging
import mock

from .scenarios import (
    EXAMPLE,
    STOP_ID,
    ROUTE_ID,
    BUS_PLATE_NUMBER
)

import arrow
from falcon import testing
from scl_transport.gtfsdb.gtfsdb import (
    Agency,
    Stop,
    Bus,
    Route,
    StopTime,
    RouteStop,
    Trip,
    FeedInfo
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


"""
Pending tests (missing endpoints)
    /v2/stops/{stop_id}/stop_routes
    /v3/stops/{stop_id}/stop_routes
    /v1/routes/{route_id}/directions
    /v1/routes/{route_id}/directions/{direction_id}
    /v2/routes/{route_id}/directions
    /v2/routes/{route_id}/directions/{direction_id}
    /v1/trips/{trip_id}/stop_times
    /v1/trips/{trip_id}/shape
    /v1/map
    /v2/map
"""


# /v1/routes/{}/trips
class RouteTripsTestCase(BaseTestCase):
    def setUp(self):
        super(RouteTripsTestCase, self).setUp()

        self.agency = Agency(
            agency_id='TS',
            agency_name='Transantiago',
            agency_url='http://www.transantiago.cl',
            agency_timezone='America/Santiago'
        )
        self.session.add(self.agency)

        self.stop_id = 'PA1'
        self.stop = Stop(
            stop_id=self.stop_id,
            stop_code='PA1',
            stop_name='PA1-Parada 6 / (M) Quinta Normal',
            stop_lat='-33.4401169274166',
            stop_lon='-33.4401169274166',
            stop_url='http://www.metro.cl/estacion/vicuna-mackenna-l4'
        )
        self.session.add(self.stop)

        self.route_id = '106'
        self.route = Route(
            route_id=self.route_id,
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
        result = self.get('/v1/routes/{}/trips'.format(self.route_id))
        self.assertEqual(result.status_code, 200)


# /v1/buses/
# /v1/buses/{}
class BusTestCase(BaseTestCase):
    def setUp(self):
        super(BusTestCase, self).setUp()
        bus = Bus(
            bus_plate_number=BUS_PLATE_NUMBER,
            fetched_at=arrow.now().naive,
            direction_id=0,
        )
        self.session.add(bus)
        self.session.commit()

    def test_collection(self):
        result = self.get('/v1/buses')
        self.assertEqual(result.status_code, 200)
        from pprint import pprint
        pprint(result.json)
        expected_json = {
            u'has_next': False,
            u'page_number': 1,
            u'page_size': 1,
            u'results': [{
                u'added_at': None,
                u'bus_lat': None,
                u'bus_lon': None,
                u'bus_movement_orientation': None,
                u'bus_plate_number': u'CJRT-12',
                u'bus_speed': None,
                u'captured_at': None,
                u'direction_id': 0,
                u'operator_number': None,
                u'route_id': None
            }],
            u'total_pages': 1,
            u'total_results': 1
        }
        self.assertEqual(result.json, expected_json)

    def test_item(self):
        result = self.get('/v1/buses/{}'.format(BUS_PLATE_NUMBER))
        self.assertEqual(result.status_code, 200)
        from pprint import pprint
        pprint(result.json)
        expected_json = {
            u'added_at': None,
            u'bus_lat': None,
            u'bus_lon': None,
            u'bus_movement_orientation': None,
            u'bus_plate_number': u'CJRT-12',
            u'bus_speed': None,
            u'captured_at': None,
            u'direction_id': 0,
            u'operator_number': None,
            u'route_id': None
        }
        self.assertEqual(result.json, expected_json)


# /v1/stops/{}/trips
class StopTripsTestCase(BaseTestCase):
    def setUp(self):
        super(StopTripsTestCase, self).setUp()

        self.agency = Agency(
            agency_id='TS',
            agency_name='Transantiago',
            agency_url='http://www.transantiago.cl',
            agency_timezone='America/Santiago'
        )
        self.session.add(self.agency)

        self.stop_id = 'PA1'
        self.stop = Stop(
            stop_id=self.stop_id,
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
        result = self.get('/v1/stops/{}/trips'.format(self.stop_id))
        self.assertEqual(result.status_code, 200)


class AgencyTestCase(BaseTestCase):
    def setUp(self):
        super(AgencyTestCase, self).setUp()
        agency_id = 'TS'
        agency_name = 'Transantiago'
        agency_url = 'http://www.transantiago.cl'
        agency_timezone = 'America/Santiago'

        self.agency = Agency(
            agency_id=agency_id,
            agency_name=agency_name,
            agency_url=agency_url,
            agency_timezone=agency_timezone
        )
        self.session.add(self.agency)
        self.session.commit()
        self.expected_json = {
            u'results': [{
                u'agency_id': u'TS',
                u'agency_name': u'Transantiago',
                u'agency_url': u'http://www.transantiago.cl'
            }]
        }

    def test_collection(self):
        result = self.get('/v1/agencies')
        self.assertEqual(result.status_code, 200)
        from pprint import pprint
        pprint(result.json)
        self.assertEqual(result.json, self.expected_json)


class InfoTestCase(BaseTestCase):
    def setUp(self):
        super(InfoTestCase, self).setUp()

        feed_publisher_name = u'Transantiago'
        feed_publisher_url = u'http://www.transantiago.cl'
        feed_lang = u'es'
        feed_start_date = u'2018-01-08'
        feed_end_date = u'2018-09-30'
        feed_version = u'V37.20180113'

        self.feed_info = FeedInfo(
            feed_publisher_name=feed_publisher_name,
            feed_publisher_url=feed_publisher_url,
            feed_lang=feed_lang,
            feed_start_date=feed_start_date,
            feed_end_date=feed_end_date,
            feed_version=feed_version,
        )
        self.session.add(self.feed_info)
        self.session.commit()

        self.expected_json = {
            u'feed_end_date': feed_end_date,
            u'feed_lang': feed_lang,
            u'feed_publisher_name': feed_publisher_name,
            u'feed_publisher_url': feed_publisher_url,
            u'feed_start_date': feed_start_date,
            u'feed_version': feed_version
        }

    def test_item(self):
        result = self.get('/v1/info')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, self.expected_json)


# /v1/trips/{}/stops
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


#/v1/trips/{}
#/v1/trips/
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


# /v1/routes
# /v1/routes/{}
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

#v1/stops
#v1/stops/{}
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

#/v1/stops/{}/stop_routes
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


#/v2/stops/{}/stop_routes
class StopRoutesTestCase_v2(BaseTestCase):
    def setUp(self):
        super(StopRoutesTestCase_v2, self).setUp()

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
        result = self.get('/v2/stops/PA1/stop_routes')
        self.assertEqual(result.status_code, 200)
        expected_json = {
            'results': [{
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
        }
        self.assertEqual(result.json, expected_json)


#/v3/stops/{}/stop_routes
class StopRoutesTestCase_v3(BaseTestCase):
    def setUp(self):
        super(StopRoutesTestCase_v3, self).setUp()

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
        result = self.get('/v3/stops/PA1/stop_routes')
        self.assertEqual(result.status_code, 200)
        expected_json = {
            'results': [{
                u'is_first_stop': None,
                u'is_last_stop': None,
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
        }
        self.assertEqual(result.json, expected_json)


# /
class HealthCheckAliasTestCase(BaseTestCase):
    def test_success(self):
        result = self.get('/')
        self.assertEqual(result.status_code, 200)


# /v1/ping
class HealthCheckTestCase(BaseTestCase):
    def test_success(self):
        result = self.get('/')
        self.assertEqual(result.status_code, 200)


# /v1/stops/{}/next_arrivals
class StopArrivalTestCase(BaseTestCase):
    def setUp(self):
        super(StopArrivalTestCase, self).setUp()
        patch_attribute = 'scl_transport.api.utils.predictor.Predictor._request_data'
        self.patcher = mock.patch(patch_attribute)
        patch = self.patcher.start()
        patch.return_value = EXAMPLE
        self.app = create_app()

    def tearDown(self):
        self.patcher.stop()
        super(StopArrivalTestCase, self).tearDown()

    def test_collection(self):
        result = self.get('/v1/stops/FAKE_STOP_ID/next_arrivals')
        self.assertEqual(result.status_code, 200)

        expected_json = {
            u'results': [{
                u'arrival_estimation': u'Menos de 5 min.',
                u'bus_distance': u'21',
                u'bus_plate_number': u'CJRT-12',
                u'calculated_at': u'2018-01-11 21:19',
                u'is_live': True,
                u'route_id': u'D02'
            }]
        }

        self.assertEqual(result.json, expected_json)


# /v2/stops/{}/next_arrivals
class StopArrivalTestCase_v2(BaseTestCase):
    def setUp(self):
        super(StopArrivalTestCase_v2, self).setUp()
        patch_attribute = 'scl_transport.api.utils.predictor.Predictor._request_data'
        self.patcher = mock.patch(patch_attribute)
        patch = self.patcher.start()
        patch.return_value = EXAMPLE
        self.app = create_app()

        # create stop
        self.stop = Stop(
            stop_id=STOP_ID,
            stop_code='PA1',
            stop_name='PA1-Parada 6 / (M) Quinta Normal',
            stop_lat='-33.4401169274166',
            stop_lon='-33.4401169274166',
            stop_url='http://www.metro.cl/estacion/vicuna-mackenna-l4',
            route_directions={ROUTE_ID: '1'}
        )
        self.session.add(self.stop)
        self.session.commit()

    def tearDown(self):
        self.patcher.stop()
        super(StopArrivalTestCase_v2, self).tearDown()

    def test_collection_direction_id_on_cache(self):
        result = self.get('/v2/stops/{}/next_arrivals'.format(STOP_ID))
        self.assertEqual(result.status_code, 200)

        expected_json = {
            u'results': [{
                u'arrival_estimation': u'Menos de 5 min.',
                u'bus_distance': u'21',
                u'bus_plate_number': u'CJRT-12',
                u'calculated_at': u'2018-01-11 21:19',
                u'is_live': True,
                u'route_id': u'D02',
                u'direction_id': 1,
            }]
        }

        self.assertEqual(result.json, expected_json)

    def test_collection_direction_id_on_buses(self):
        EXPECTED_DIRECTION_ID = 0
        bus = Bus(
            bus_plate_number=BUS_PLATE_NUMBER,
            fetched_at=arrow.now().naive,
            direction_id=EXPECTED_DIRECTION_ID,
        )
        self.session.add(bus)
        self.stop.route_directions = {ROUTE_ID: None}
        self.session.add(self.stop)
        self.session.commit()

        result = self.get('/v2/stops/{}/next_arrivals'.format(STOP_ID))
        self.assertEqual(result.status_code, 200)

        expected_json = {
            u'results': [{
                u'arrival_estimation': u'Menos de 5 min.',
                u'bus_distance': u'21',
                u'bus_plate_number': u'CJRT-12',
                u'calculated_at': u'2018-01-11 21:19',
                u'is_live': True,
                u'route_id': u'D02',
                u'direction_id': 0,
            }]
        }

        self.assertEqual(result.json, expected_json)

    def test_collection_direction_id_no_info(self):
        self.stop.route_directions = {ROUTE_ID: None}
        self.session.add(self.stop)
        self.session.commit()

        result = self.get('/v2/stops/{}/next_arrivals'.format(STOP_ID))
        self.assertEqual(result.status_code, 200)

        expected_json = {
            u'results': [{
                u'arrival_estimation': u'Menos de 5 min.',
                u'bus_distance': u'21',
                u'bus_plate_number': u'CJRT-12',
                u'calculated_at': u'2018-01-11 21:19',
                u'is_live': True,
                u'route_id': u'D02',
                u'direction_id': None,
            }]
        }

        self.assertEqual(result.json, expected_json)
