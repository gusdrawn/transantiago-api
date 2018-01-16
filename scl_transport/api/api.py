# -*- coding: utf-8 -*-

import json
import falcon
import arrow
import os
from marshmallow import fields
from webargs.falconparser import use_args
from sqlalchemy.orm import scoped_session
from sqlalchemy import func
from geoalchemy2.elements import WKTElement

from scl_transport.api.utils import pager
from scl_transport.api.utils.predictor import Predictor
from scl_transport.api.utils.arrivals import NextArrivals
from scl_transport.api.utils.geo import BoundingBox, get_bounding_box
from scl_transport.gtfsdb.gtfsdb import (
    Stop,
    StopTime,
    Trip,
    Route,
    FeedInfo,
    StopSchedule,
    Database,
    RouteStop,
    BipSpot,
    Agency,
    Bus
)
from scl_transport.gtfsdb.gtfsdb.schemas import (
    BusSchema,
    FeedSchema,
    BipSpotSchema,
    TripSchema,
    ShapeSchema,
    AgencySchema,
    RouteSchema,
    DetailedDirectionSchema,
    StopSchema,
    StopRouteSchema,
    StopTimeSchema,
    StopWithStopRoutesSchema
)


import newrelic.agent
if os.environ.get('NEWRELIC_ENABLED'):
    newrelic.agent.initialize('newrelic.ini')

# global raven

raven_client = None


"""
Create engine, session_factory and scoped_session object.
"""

adapter = None
session_factory = lambda: adapter.session_factory()
Session = scoped_session(session_factory)


"""
Middlewares
"""


class SQLAlchemySessionManager(object):
    """
    Create a scoped session for every request and close it when the request
    ends.
    """
    def __init__(self, Session):
        self.Session = Session

    def process_resource(self, req, resp, resource, params):
        resource.session = self.Session()

    def process_response(self, req, resp, resource, req_succeeded):
        if hasattr(resource, 'session'):
            resource.session.close()


"""
Error Exceptions and Handlers
"""


class ApiError(falcon.HTTPStatus):
    response = None

    def __init__(self, status, title, errors=None):
        body = self.build_default_body(title, errors)
        super(ApiError, self).__init__(status=status, body=body, headers=None)

    def build_default_body(self, title, errors={}):
        return json.dumps({
            'title': title,
            'errors': errors
        })


class EntityNotFound(ApiError):
    def __init__(self):
        title = u'Entity not found'
        status = falcon.HTTP_404
        errors = {'entity_id': [title]}
        super(EntityNotFound, self).__init__(status, title, errors)


def internal_error_handler(ex, req, resp, params):
    """Sentry error handler."""
    # collect data
    data = {
        'request': {
            'url': req.url,
            'method': req.method,
            'query_string': req.query_string,
            'env': req.env,
            'data': req.params,
            'headers': req.headers,
        }
    }
    message = isinstance(ex, falcon.HTTPError) and ex.title or str(ex)
    # if not a HTTP status or error exception, send to Sentry and respond with HTTP 500
    if not issubclass(type(ex), (falcon.HTTPError, falcon.HTTPStatus)):
        raven_client.captureException(message=message, data=data)
        resp.status = falcon.HTTP_500
        resp.body = json.dumps({'results': 'Our engineers are working quickly to resolve the issue. If you need help or more information please contact to admin@scltrans.it'})
    else:
        raise ex


"""
API endpoints
"""

PER_PAGE_LIMIT = 100


class HealthCheckResource(object):

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'results': 'ok'})


# /v1/info
class InfoResource(object):
    def on_get(self, req, resp):
        feed = self.session.query(FeedInfo).first()
        if not feed:
            raise falcon.HTTPNotFound(title='No info', description='No info related to feed')

        feed_schema = FeedSchema()
        dump_data = feed_schema.dump(feed).data
        resp.body = json.dumps(dump_data, ensure_ascii=False)


# /v1/bip_spots/
class BipSpotCollectionResource(object):
    @use_args({
        'limit': fields.Int(),
        'page': fields.Int(),
        # option 1
        'center_lat': fields.Str(),
        'center_lon': fields.Str(),
        # option 2
    })
    def on_get(self, req, resp, args):
        page = args.get('page', 1)
        per_page_limit = args.get('limit', PER_PAGE_LIMIT)
        bip_spots = self.session.query(BipSpot).filter()

        if args.get('center_lat') and args.get('center_lon'):
            BipSpot.add_geometry_column()  # @@TODO: fix this
            pt = WKTElement('POINT({0} {1})'.format(args['center_lon'], args['center_lat']), srid=4326)
            bip_spots = bip_spots.order_by(BipSpot.geom.distance_box(pt))

        paginator = pager(bip_spots, page, per_page_limit)

        #  serializer  results
        bip_spot_schema = BipSpotSchema()
        results = bip_spot_schema.dump(paginator.items, many=True).data
        #  build body
        body = dict(
            has_next=paginator.has_next,
            total_results=paginator.total,
            total_pages=paginator.pages,
            results=results,
            page_size=len(results),
            page_number=paginator.page,
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/bip_spots/{bip_spot_code}
class BipSpotResource(object):
    def on_get(self, req, resp, bip_spot_code):
        bip_spot = self.session.query(BipSpot).filter_by(bip_spot_code=bip_spot_code).one_or_none()
        if not bip_spot:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found bip spot for Bip spot code: {}'.format(bip_spot_code)
            )

        bip_spot_schema = BipSpotSchema()
        dump_data = bip_spot_schema.dump(bip_spot).data
        resp.body = json.dumps(dump_data, ensure_ascii=False)


# /v1/trips/
class TripCollectionResource(object):
    @use_args({'limit': fields.Int(), 'page': fields.Int()})
    def on_get(self, req, resp, args):
        page = args.get('page', 1)
        per_page_limit = args.get('limit', PER_PAGE_LIMIT)
        trips = self.session.query(Trip).filter()
        paginator = pager(trips, page, per_page_limit)
        #  serializer  results
        trip_schema = TripSchema()
        results = trip_schema.dump(paginator.items, many=True).data
        #  build body
        body = dict(
            has_next=paginator.has_next,
            total_results=paginator.total,
            total_pages=paginator.pages,
            results=results,
            page_size=len(results),
            page_number=paginator.page,
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/trips/{trip_id}
class TripResource(object):
    def on_get(self, req, resp, trip_id):
        trip = self.session.query(Trip).filter_by(trip_id=trip_id).one_or_none()
        if not trip:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Trip for ID: {}'.format(trip_id)
            )

        trip_schema = TripSchema()
        dump_data = trip_schema.dump(trip).data
        resp.body = json.dumps(dump_data, ensure_ascii=False)


# /v1/trips/{trip_id}/shape
class TripShapeCollectionResource(object):
    def on_get(self, req, resp, trip_id):
        trip = self.session.query(Trip).filter_by(trip_id=trip_id).one_or_none()
        if not trip:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Trip for ID: {}'.format(trip_id)
            )
        shape_schema = ShapeSchema()
        dump_data = shape_schema.dump(trip.pattern.shape, many=True).data
        resp.body = json.dumps({'results': dump_data}, ensure_ascii=False)


# /v1/agencies
class AgencyCollectionResource(object):
    def on_get(self, req, resp):
        agencies = self.session.query(Agency).filter()
        agency_schema = AgencySchema()
        dump_data = agency_schema.dump(agencies, many=True).data
        resp.body = json.dumps({'results': dump_data}, ensure_ascii=False)


# /v1/routes/
class RouteCollectionResource(object):
    @use_args({'agency_id': fields.Str(), 'limit': fields.Int(), 'page': fields.Int()})
    def on_get(self, req, resp, args):
        page = args.get('page', 1)
        per_page_limit = args.get('limit', PER_PAGE_LIMIT)
        routes = self.session.query(Route).filter()
        if args.get('agency_id'):
            routes = routes.filter(Route.agency_id == args.get('agency_id'))
        paginator = pager(routes, page, per_page_limit)
        #  serializer  results
        route_schema = RouteSchema()
        results = route_schema.dump(paginator.items, many=True).data
        #  build body
        body = dict(
            has_next=paginator.has_next,
            total_results=paginator.total,
            total_pages=paginator.pages,
            results=results,
            page_size=len(results),
            page_number=paginator.page,
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/routes/{route_id}
class RouteResource(object):
    def on_get(self, req, resp, route_id):
        route = self.session.query(Route).filter_by(route_id=route_id).one_or_none()
        if not route:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Route for ID: {}'.format(route_id)
            )

        route_schema = RouteSchema()
        dump_data = route_schema.dump(route).data
        resp.body = json.dumps(dump_data, ensure_ascii=False)


# /v1/routes/{route_id}/directions
class RouteDirectionCollectionResource(object):
    def on_get(self, req, resp, route_id):
        route = self.session.query(Route).filter_by(route_id=route_id).one_or_none()
        if not route:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Route for ID: {}'.format(route_id)
            )
        direction_schema = DetailedDirectionSchema()
        dump_data = direction_schema.dump(route.directions, many=True).data
        body = dict(
            results=dump_data
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/routes/{route_id}/directions/<direction_id>
class RouteDirectionResource(object):
    def on_get(self, req, resp, route_id, direction_id):
        route = self.session.query(Route).filter_by(route_id=route_id).one_or_none()
        if not route:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Route for ID: {}'.format(route_id)
            )

        direction = None
        for route_direction in route.directions:
            if int(route_direction.direction_id) == int(direction_id):
                direction = route_direction

        if not route_direction:
            raise EntityNotFound()

        direction_schema = DetailedDirectionSchema()
        dump_data = direction_schema.dump(direction).data
        body = dict(
            results=dump_data
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v2/routes/{route_id}/directions
class RouteDirectionCollectionResource_v2(object):
    def on_get(self, req, resp, route_id):
        route = self.session.query(Route).filter_by(route_id=route_id).one_or_none()
        if not route:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Route for ID: {}'.format(route_id)
            )

        # @@TODO: use serializer (Schema)
        data = []
        for d in route.directions:
            direction_data = {
                'route_id': d.route_id,
                'direction_id': d.direction_id,
                'direction_name': d.direction_name,
                'direction_headsign': d.direction_headsign,
                'stop_times': d.trip_stop_times,
                'shape': d.trip_shape,
                'is_active': d.trip_is_active
            }
            data.append(direction_data)
        body = dict(
            results=data
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v2/routes/{route_id}/directions/<direction_id>
class RouteDirectionResource_v2(object):
    def on_get(self, req, resp, route_id, direction_id):
        route = self.session.query(Route).filter_by(route_id=route_id).one_or_none()
        if not route:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Route for ID: {}'.format(route_id)
            )

        direction = None
        for route_direction in route.directions:
            if int(route_direction.direction_id) == int(direction_id):
                direction = route_direction

        if not direction:
            raise EntityNotFound()

        direction_data = {
            'route_id': direction.route_id,
            'direction_id': direction.direction_id,
            'direction_name': direction.direction_name,
            'direction_headsign': direction.direction_headsign,
            'stop_times': direction.trip_stop_times,
            'shape': direction.trip_shape,
            'is_active': direction.trip_is_active
        }

        body = dict(
            results=direction_data
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/routes/{route_id}/trips
class RouteTripsResource(object):
    @use_args({'is_active': fields.Int()})
    def on_get(self, req, resp, args, route_id):
        if args.get('is_active'):
            trips = Trip.get_active_trips_for_route(self.session, route_id)
        else:
            trips = self.session.query(Trip).filter(
                Trip.route_id == route_id
            )

        trip_schema = TripSchema()
        dump_data = trip_schema.dump(trips, many=True).data
        body = dict(
            results=dump_data
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/stops/
class StopCollectionResource(object):

    @use_args({
        'limit': fields.Int(),
        'is_active': fields.Int(),
        'page': fields.Int(),
        'agency_id': fields.Str(),
        # option 1
        'bbox': fields.Raw(),
        # option 2
        'center_lat': fields.Str(),
        'center_lon': fields.Str(),
        'radius': fields.Int(),
    })
    def on_get(self, req, resp, args):
        page = args.get('page', 1)
        per_page_limit = args.get('limit', PER_PAGE_LIMIT)
        stops = self.session.query(Stop).filter()
        if args.get('agency_id'):
            stops = stops.filter(Stop.agency_id == args.get('agency_id'))
        if args.get('bbox'):
            bounding_box = BoundingBox(args.get('bbox'))
            polygon_text = bounding_box.to_polygon_text()
            bbox = WKTElement(polygon_text, srid=4326)
            stops = stops.filter(Stop.geom.contained(bbox))
        elif args.get('center_lat') and args.get('center_lon'):
            if args.get('radius'):
                radius = float(args.get('radius')) / 1000.0
                bounding_box = get_bounding_box(
                    latitude_in_degrees=args.get('center_lat'),
                    longitude_in_degrees=args.get('center_lon'),
                    half_side_in_km=radius
                )
                polygon_text = bounding_box.to_polygon_text()
                bbox = WKTElement(polygon_text, srid=4326)
                stops = stops.filter(Stop.geom.contained(bbox))
            else:
                pt = WKTElement('POINT({0} {1})'.format(args['center_lon'], args['center_lat']), srid=4326)
                stops = stops.order_by(Stop.geom.distance_box(pt))

        paginator = pager(stops, page, per_page_limit)

        stop_schema = StopSchema()
        items = paginator.items
        if args.get('is_active'):
            items = filter(lambda x: x.is_active(), items)
        results = stop_schema.dump(items, many=True).data

        #  build body
        body = dict(
            has_next=paginator.has_next,
            total_results=paginator.total,
            total_pages=paginator.pages,
            results=results,
            page_size=len(results),
            page_number=paginator.page,
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/stops/{stop_id}
class StopResource(object):
    def on_get(self, req, resp, stop_id):
        stop = self.session.query(Stop).filter_by(stop_id=stop_id).one_or_none()
        if not stop:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Stop for ID: {}'.format(stop_id)
            )

        stop_schema = StopSchema()
        dump_data = stop_schema.dump(stop).data
        resp.body = json.dumps(dump_data, ensure_ascii=False)


# /v1/stops/{stop_id}/stop_routes
class StopRouteCollectionResource(object):
    def on_get(self, req, resp, stop_id):
        stop = self.session.query(Stop).filter_by(stop_id=stop_id).one_or_none()
        if not stop:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Stop for ID: {}'.format(stop_id)
            )
        stop_route_schema = StopRouteSchema()
        dump_data = stop_route_schema.dump(stop.stop_routes, many=True).data
        resp.body = json.dumps(dump_data, ensure_ascii=False)


# /v2/stops/{stop_id}/stop_routes
class StopRouteCollectionResource_v2(object):
    def on_get(self, req, resp, stop_id):
        stop = self.session.query(Stop).filter_by(stop_id=stop_id).one_or_none()
        if not stop:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Stop for ID: {}'.format(stop_id)
            )
        stop_route_schema = StopRouteSchema()
        results = stop_route_schema.dump(stop.stop_routes, many=True).data
        body = dict(results=results,)
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/stops/{stop_id}/routes
class StopRoutesResource(object):
    def on_get(self, req, resp, stop_id):
        stop_routes = RouteStop.unique_routes_at_stop(
            session=self.session,
            stop_id=stop_id
        )
        route_schema = RouteSchema()
        results = route_schema.dump(stop_routes, many=True).data
        body = dict(results=results,)
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/stops/{stop_id}/schedule
class StopScheduleCollectionResource(object):
    @use_args({'limit': fields.Int(), 'date': fields.Date(), 'arrival_time_after': fields.Time()})
    def on_get(self, req, resp, args, stop_id):

        stop_schedule = StopSchedule(stop_id)
        stop_schedule.as_dict(self.session)
        body = dict(results=stop_schedule.as_dict(self.session),)
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/stops/{stop_id}/schedule/{route_id}
class StopScheduleResource(object):
    def on_get(self, req, resp, stop_id, route_id):
        date = req.params.get('date')
        if date:
            try:
                date = arrow.get(date, 'YYYY-MM-DD').date()
            except arrow.parser.ParserError:
                pass
        limit = req.params.get('limit', PER_PAGE_LIMIT * 2)  # TODO: temporary solution
        stop_times = StopTime.get_departure_schedule(
            session=self.session,
            stop_id=stop_id,
            route_id=route_id,
            date=date,
            limit=limit
        )
        stop_time_schema = StopTimeSchema()
        results = stop_time_schema.dump(stop_times, many=True).data
        body = dict(results=results,)
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/stops/{stop_id}/trips
class StopTripsCollectionResource(object):
    @use_args({'is_active': fields.Int(), 'route_id': fields.Str()})
    def on_get(self, req, resp, args, stop_id):
        trips = Trip.get_trips_for_stop(
            session=self.session,
            stop_id=stop_id,
            route_id=args.get('route_id'),
            only_active=args.get('is_active', False)
        )
        trip_schema = TripSchema()
        results = trip_schema.dump(trips, many=True).data
        body = dict(results=results,)
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/trips/{trip_id}/stops
class TripStopsCollectionResource(object):

    def on_get(self, req, resp, trip_id):
        trip = self.session.query(Trip).filter(
            Trip.trip_id == trip_id
        ).one_or_none()

        if not trip:
            raise falcon.HTTPNotFound(
                title='Not found',
                description='Not found Trip for ID: {}'.format(trip_id)
            )

        stops = []
        for stop_time in trip.stop_times:
            stops.append(stop_time.stop)

        stops = self.session.query(Stop).filter(Stop.stop_id.in_([stop.stop_id for stop in stops]))

        #  serializer  results
        stop_schema = StopSchema()
        results = stop_schema.dump(stops, many=True).data

        #  build body
        body = dict(
            results=results,
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/trips/{trip_id}/stop_times
class TripStopTimesCollectionResource(object):
    def on_get(self, req, resp, trip_id):
        stop_times = self.session.query(StopTime).filter(StopTime.trip_id == trip_id).order_by(StopTime.stop_sequence)
        stop_time_schema = StopTimeSchema()
        results = stop_time_schema.dump(stop_times, many=True).data
        body = dict(results=results,)
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/map
class TransportMapCollectionResource(object):
    @use_args(
        {
            # option 1
            'bbox': fields.Raw(),
            # option 2
            'center_lat': fields.Str(),
            'center_lon': fields.Str(),
            'radius': fields.Int(),
            # optional elements
            'include_stop_routes': fields.Int(),
            'include_bip_spots': fields.Int(),
            'include_buses': fields.Int()
        }
    )
    def on_get(self, req, resp, args):
        results = {}
        # create polygon
        # bbox = left,bottom,right,top
        # bbox = min Longitude , min Latitude , max Longitude , max Latitude

        if not (args.get('bbox') or (args.get('center_lat') and args.get('center_lon'))):
            raise falcon.HTTPBadRequest(
                title='Missing params',
                description='you must define bbox or (center_lon and center_lat)'
            )

        if args.get('bbox'):
            bounding_box = BoundingBox(args.get('bbox'))
        else:
            radius = 1.0
            if args.get('radius'):
                radius = float(args.get('radius')) / 1000.0
            bounding_box = get_bounding_box(
                latitude_in_degrees=args.get('center_lat'),
                longitude_in_degrees=args.get('center_lon'),
                half_side_in_km=radius
            )

        polygon_text = bounding_box.to_polygon_text()
        bbox = WKTElement(polygon_text, srid=4326)
        stops = self.session.query(Stop).filter()
        stops = stops.filter(Stop.geom.contained(bbox))

        # get routes, @@TODO: improve this
        if args.get('include_stop_routes'):
            stop_schema = StopWithStopRoutesSchema()
        else:
            stop_schema = StopSchema()
        stop_results = stop_schema.dump(stops, many=True).data
        results['stops'] = stop_results

        # get bip points
        bip_spots = None
        if args.get('include_bip_spots'):
            BipSpot.add_geometry_column()  # @@TODO: fix this
            bip_spots = self.session.query(BipSpot).filter()
            bip_spots = bip_spots.filter(BipSpot.geom.contained(bbox))
            bip_spot_schema = BipSpotSchema()
            bip_spot_results = bip_spot_schema.dump(bip_spots, many=True).data
            results['bip_spots'] = bip_spot_results

        # get buses
        buses = None
        if args.get('include_buses'):
            buses = self.session.query(Bus).filter()
            buses = buses.filter(Bus.geom.contained(bbox))
            bus_schema = BusSchema()
            bus_results = bus_schema.dump(buses, many=True).data
            results['buses'] = bus_results

        # serialize response
        body = dict(
            results=results,
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/stops/{stop_id}/next_arrivals
class StopArrivalCollectionResource(object):
    @use_args({'route_id': fields.Int()})
    def on_get(self, req, resp, args, stop_id):
        route_id = args.get('route_id')
        # live information
        try:
            predictor = Predictor(
                client_id=int(os.getenv("PREDICTOR_WS_CLIENT_ID")),
                resolution=os.getenv('PREDICTOR_WS_RESOLUTION'),
                registered_IP=os.getenv("PREDICTOR_WS_REGISTERED_IP")
            )
            live_arrivals = predictor.get(stop_id, route_id)
            next_arrivals = NextArrivals(live_arrivals, [])
            body = dict(
                results=next_arrivals.get_combined_results(),
            )
            resp.body = json.dumps(body, ensure_ascii=False)
        except Exception, e:
            if 'Connection timed out' in str(e):
                print "time out..."
                print str(e)
                resp.status = falcon.HTTP_REQUEST_TIMEOUT
                resp.body = json.dumps({'title': 'smsbus webservice timeout'})
            else:
                print "undhandled exception...", str(e)
                raise Exception(str(e))


# /v1/buses
class BusCollectionResource(object):
    @use_args({
        'limit': fields.Int(),
        'page': fields.Int(),
        'route_id': fields.Str(),
        'direction_id': fields.Int(),
        # option 1
        'bbox': fields.Raw(),
        # option 2
        'center_lat': fields.Str(),
        'center_lon': fields.Str(),
        'radius': fields.Int(),
    })
    def on_get(self, req, resp, args):
        page = args.get('page', 1)
        per_page_limit = args.get('limit', PER_PAGE_LIMIT)

        buses = self.session.query(Bus).filter()
        if args.get('bbox'):
            bounding_box = BoundingBox(args.get('bbox'))
            polygon_text = bounding_box.to_polygon_text()
            bbox = WKTElement(polygon_text, srid=4326)
            buses = buses.filter(Bus.geom.contained(bbox))
        elif args.get('center_lat') and args.get('center_lon'):
            if args.get('radius'):
                radius = float(args.get('radius')) / 1000.0
                bounding_box = get_bounding_box(
                    latitude_in_degrees=args.get('center_lat'),
                    longitude_in_degrees=args.get('center_lon'),
                    half_side_in_km=radius
                )
                polygon_text = bounding_box.to_polygon_text()
                bbox = WKTElement(polygon_text, srid=4326)
                buses = buses.filter(Bus.geom.contained(bbox))
            else:
                pt = WKTElement('POINT({0} {1})'.format(args['center_lon'], args['center_lat']), srid=4326)
                buses = buses.order_by(Bus.geom.distance_box(pt))

        if args.get('direction_id') != None:
            buses = buses.filter(Bus.direction_id == args['direction_id'])

        if args.get('route_id'):
            buses = buses.filter(Bus.original_route_id == args['route_id'].upper())

        # detect temporary condition of duplicated records
        if buses.distinct(Bus.fetched_at).count() > 1:
            last_fetch = self.session.query(func.max(Bus.fetched_at)).filter().scalar()
            buses = buses.filter(Bus.fetched_at == last_fetch)

        bus_schema = BusSchema()
        paginator = pager(buses, page, per_page_limit)

        #  serializer  results
        bus_schema = BusSchema()
        results = bus_schema.dump(paginator.items, many=True).data
        #  build body
        body = dict(
            has_next=paginator.has_next,
            total_results=paginator.total,
            total_pages=paginator.pages,
            results=results,
            page_size=len(results),
            page_number=paginator.page,
        )
        resp.body = json.dumps(body, ensure_ascii=False)


# /v1/buses/{bus_plate_number}
class BusResource(object):
    def on_get(self, req, resp, bus_plate_number):
        bus_schema = BusSchema()
        bus = self.session.query(Bus).filter(
            Bus.bus_plate_number == bus_plate_number
        ).order_by('fetched_at desc').first()

        dump_data = bus_schema.dump(bus).data
        resp.body = json.dumps(dump_data, ensure_ascii=False)


"""
# Internal use endpoint
"""
BASE_SHIELD_URL = 'https://img.shields.io/badge/{subject}-{title}-{color}.svg'


class GTFSVersionShieldResource(object):
    def on_get(self, req, resp):
        feed_info = self.session.query(FeedInfo).first()
        shield_url = BASE_SHIELD_URL.format(subject='GTFS', title=feed_info.feed_version, color='green')
        raise falcon.HTTPMovedPermanently(shield_url)


class GTFSFetchedAtInfoResource(object):
    def on_get(self, req, resp):
        feed_info = self.session.query(FeedInfo).first()
        fetched_at = ''
        if feed_info.feed_last_fetched_at:
            fetched_at = arrow.get(feed_info.feed_last_fetched_at).format('YYYY/MM/DD HH:MM')
        shield_url = BASE_SHIELD_URL.format(subject='Last fetch', title=fetched_at, color='yellow')
        raise falcon.HTTPMovedPermanently(shield_url)


"""
App construction & route registration
"""


def add_routes(app):

    app.add_route('/', HealthCheckResource())
    app.add_route('/v1/ping', HealthCheckResource())
    # GTFS resources
    app.add_route('/v1/info', InfoResource())
    app.add_route('/v1/agencies', AgencyCollectionResource())

    app.add_route('/v1/stops', StopCollectionResource())
    app.add_route('/v1/stops/{stop_id}', StopResource())
    app.add_route('/v1/stops/{stop_id}/trips', StopTripsCollectionResource())
    app.add_route('/v1/stops/{stop_id}/stop_routes', StopRouteCollectionResource())
    app.add_route('/v2/stops/{stop_id}/stop_routes', StopRouteCollectionResource_v2())
    # prediction webservice related
    app.add_route('/v1/stops/{stop_id}/next_arrivals', StopArrivalCollectionResource())

    app.add_route('/v1/routes', RouteCollectionResource())
    app.add_route('/v1/routes/{route_id}', RouteResource())
    app.add_route('/v1/routes/{route_id}/trips', RouteTripsResource())
    app.add_route('/v1/routes/{route_id}/directions', RouteDirectionCollectionResource())
    app.add_route('/v1/routes/{route_id}/directions/{direction_id}', RouteDirectionResource())
    app.add_route('/v2/routes/{route_id}/directions', RouteDirectionCollectionResource_v2())
    app.add_route('/v2/routes/{route_id}/directions/{direction_id}', RouteDirectionResource_v2())
    app.add_route('/v1/trips/', TripCollectionResource())
    app.add_route('/v1/trips/{trip_id}', TripResource())  # @@TODO: order by sequence
    app.add_route('/v1/trips/{trip_id}/stops', TripStopsCollectionResource())  # TODO: order by sequence
    app.add_route('/v1/trips/{trip_id}/stop_times', TripStopTimesCollectionResource())
    app.add_route('/v1/trips/{trip_id}/shape', TripShapeCollectionResource())

    # positioning webservice related
    app.add_route('/v1/buses', BusCollectionResource())
    app.add_route('/v1/buses/{bus_plate_number}', BusResource())
    # special endpoints: Schedule, BipPoints
    app.add_route('/v1/map', TransportMapCollectionResource())
    app.add_route('/v1/stops/{stop_id}/schedule', StopScheduleCollectionResource())
    app.add_route('/v1/stops/{stop_id}/schedule/{route_id}', StopScheduleResource())
    # external resources
    app.add_route('/v1/bip_spots', BipSpotCollectionResource())
    app.add_route('/v1/bip_spots/{bip_spot_code}', BipSpotResource())

    # internal endpoints
    app.add_route('/shields/fetched_at', GTFSFetchedAtInfoResource())
    app.add_route('/shields/gtfs_version', GTFSVersionShieldResource())


def create_app():
    app = falcon.API(
        middleware=[
            SQLAlchemySessionManager(Session),
        ]
    )
    add_routes(app)
    global adapter
    adapter_to_set = Database()
    adapter = adapter_to_set

    # activate raven (Sentry) if requested
    if os.environ.get('SENTRY_ENABLED'):
        from raven.base import Client
        global raven_client
        raven_client = Client(os.getenv('SENTRY_CLIENT'))
        app.add_error_handler(Exception, internal_error_handler)

    if os.environ.get('NEWRELIC_ENABLED'):
        app = newrelic.agent.WSGIApplicationWrapper(app)

    return app
