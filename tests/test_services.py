from falcon import testing
import mock
from scl_transport.api.utils.predictor import Predictor
from scl_transport.api.utils.arrivals import NextArrivals


from scl_transport.gtfsdb.gtfsdb import Database
from scl_transport.gtfsdb.gtfsdb.settings import config

from .scenarios import (
    EXAMPLE,
    STOP_ID,
    ROUTE_ID
)


class PredictorTestCase(testing.TestCase):
    def setUp(self):
        super(PredictorTestCase, self).setUp()
        patch_attribute = 'scl_transport.api.utils.predictor.Predictor._request_data'
        self.patcher = mock.patch(patch_attribute)
        patch = self.patcher.start()
        patch.return_value = EXAMPLE

    def tearDown(self):
        self.patcher.stop()
        # call super
        super(PredictorTestCase, self).tearDown()

    def test_result(self):
        predictor = Predictor(
            client_id='',
            resolution='',
            registered_IP=''
        )
        live_arrivals = predictor.get(STOP_ID, ROUTE_ID)
        expected_result = {
            'calculated_at': '2018-01-11 21:19',
            'message': None,
            'routes': [{
                'bus_distance': '21',
                'bus_plate_number': 'CJRT-12',
                'calculated_at': '2018-01-11 21:19',
                'code': '01',
                'message': None,
                'route_arrival_prediction': 'Menos de 5 min.',
                'route_id': 'D02'
            }],
            'stop_code': 'PD1431',
            'stop_name': 'PARADA 1 / PLAZA OSSANDON'
        }
        self.assertEqual(live_arrivals, expected_result)


class ArrivalsTestCase(testing.TestCase):
    def setUp(self):
        super(ArrivalsTestCase, self).setUp()
        patch_attribute = 'scl_transport.api.utils.predictor.Predictor._request_data'
        self.patcher = mock.patch(patch_attribute)
        patch = self.patcher.start()
        patch.return_value = EXAMPLE

        kwargs = {'url': config.DEFAULT_DATABASE_URL}
        self.db = Database(**kwargs)
        self.session = self.db.session
        # createdb
        self.db.create()

    def tearDown(self):
        self.patcher.stop()
        # call super
        super(ArrivalsTestCase, self).tearDown()

    def test_arrivals(self):
        predictor = Predictor(
            client_id='',
            resolution='',
            registered_IP=''
        )
        live_arrivals = predictor.get(STOP_ID, ROUTE_ID)
        next_arrivals = NextArrivals(data=live_arrivals, session=self.session, stop_id=STOP_ID)
        results = next_arrivals.get()
        expected_result = [{
            'arrival_estimation': 'Menos de 5 min.',
            'bus_distance': '21',
            'bus_plate_number': 'CJRT-12',
            'calculated_at': '2018-01-11 21:19',
            'is_live': True,
            'route_id': 'D02'
        }]
        self.assertEqual(results, expected_result)
