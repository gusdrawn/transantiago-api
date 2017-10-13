# -*- coding: utf-8 -*-

import json
import falcon
import arrow
import os

from scl_transport.api.utils import pager

from scl_transport.gtfsdb.gtfsdb import (
    Stop,
    StopTime,
    Trip,
    Route,
    FeedInfo,
    StopSchedule,
    Database,
    RouteStop,
)

from marshmallow import Schema, fields
from webargs.falconparser import use_args
from sqlalchemy.orm import scoped_session
from geoalchemy2.elements import WKTElement


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

    # decide message to use
    message = isinstance(ex, falcon.HTTPError) and ex.title or str(ex)

    # if not a HTTP status or error exception, send to Sentry and respond with HTTP 500
    if not issubclass(type(ex), (falcon.HTTPError, falcon.HTTPStatus)):
        raven_client.captureException(message=message, data=data)
        resp.status = falcon.HTTP_500
        resp.body = ('A server error occurred. Please contact the administrator.')
    else:
        raise ex


"""
Schemas
"""


class AgencySchema(Schema):
    agency_id = fields.Str()
    agency_name = fields.Str()
    agency_url = fields.Str()
    agency_timezone = fields.Str()
    agency_lang = fields.Str()
    agency_phone = fields.Str()
    agency_fare_url = fields.Str()


class StopSchema(Schema):
    stop_id = fields.Str()
    stop_code = fields.Str()
    stop_name = fields.Str()
    stop_lat = fields.Str()
    stop_desc = fields.Str()
    stop_lon = fields.Str()
    zone_id = fields.Str()
    parent_station = fields.Str()
    direction = fields.Str()
    position = fields.Str()
    #headsigns = fields.List(fields.Str())
    stop_url = fields.Str(allow_none=True)

    #is_active = fields.Boolean()


class RouteDirectionSchema(Schema):
    route_id = fields.Str()
    direction_id = fields.Int()
    direction_name = fields.Str()


class RouteSchema(Schema):
    route_id = fields.Str()
    agency_id = fields.Str()
    route_short_name = fields.Str()
    route_long_name = fields.Str()
    route_desc = fields.Str()
    route_type = fields.Str()
    route_url = fields.Str()
    route_color = fields.Str()
    route_text_color = fields.Str()
    route_sort_order = fields.Int()
    min_headway_minutes = fields.Int()
    # extra fields
    is_active = fields.Boolean()
    start_date = fields.Date()
    end_date = fields.Date()
    directions = fields.List(fields.Nested(RouteDirectionSchema))


class ServiceSchema(Schema):
    service_id = fields.Str()
    monday = fields.Boolean()
    tuesday = fields.Boolean()
    wednesday = fields.Boolean()
    thursday = fields.Boolean()
    friday = fields.Boolean()
    saturday = fields.Boolean()
    sunday = fields.Boolean()
    start_date = fields.Date()
    end_date = fields.Date()


class FrequencySchema(Schema):
    start_time = fields.Time()
    end_time = fields.Time()
    headway_secs = fields.Integer()
    exact_times = fields.Boolean()


class TripSchema(Schema):
    trip_id = fields.Str()
    route = fields.Nested(RouteSchema)
    service = fields.Nested(ServiceSchema)

    trip_headsign = fields.Str()
    trip_short_name = fields.Str()
    direction_id = fields.Str()
    frequency = fields.Nested(FrequencySchema)

    trip_len = fields.Integer()
    is_valid = fields.Boolean()

    start_time = fields.Time()
    end_time = fields.Time()

    start_stop = fields.Nested(StopSchema)
    end_stop = fields.Nested(StopSchema)


class StopTimeSchema(Schema):
    stop = fields.Nested(StopSchema)
    trip = fields.Nested(TripSchema)
    arrival_time = fields.Time()
    departure_time = fields.Time()
    stop_sequence = fields.Integer()
    stop_headsign = fields.Str()


class FeedSchema(Schema):
    feed_publisher_name = fields.Str()
    feed_publisher_url = fields.Str()
    feed_lang = fields.Str()
    feed_start_date = fields.Date()
    feed_end_date = fields.Date()
    feed_version = fields.Str()


"""
API endpoints
"""

PER_PAGE_LIMIT = 50


class HealthCheckResource(object):

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'pong'


class InfoResource(object):
    def on_get(self, req, resp):
        feed = self.session.query(FeedInfo).first()
        if not feed:
            raise EntityNotFound()

        feed_schema = FeedSchema()
        dump_data = feed_schema.dump(feed).data
        resp.body = json.dumps(dump_data)


class TripCollectionResource(object):
    @use_args({'limit': fields.Int(), 'page': fields.Int()})  # validate input data
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
        resp.body = json.dumps(body)


class TripResource(object):
    def on_get(self, req, resp, trip_id):
        trip = self.session.query(Trip).filter_by(trip_id=trip_id).one_or_none()
        if not trip:
            raise EntityNotFound()

        trip_schema = TripSchema()
        dump_data = trip_schema.dump(trip).data
        resp.body = json.dumps(dump_data)


class RouteCollectionResource(object):
    @use_args({'limit': fields.Int(), 'page': fields.Int()})  # validate input data
    def on_get(self, req, resp, args):
        page = args.get('page', 1)
        per_page_limit = args.get('limit', PER_PAGE_LIMIT)
        routes = self.session.query(Route).filter()
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
        resp.body = json.dumps(body)


class RouteResource(object):
    def on_get(self, req, resp, route_id):
        route = self.session.query(Route).filter_by(route_id=route_id).one_or_none()
        if not route:
            raise EntityNotFound()

        route_schema = RouteSchema()
        dump_data = route_schema.dump(route).data
        resp.body = json.dumps(dump_data)


class StopCollectionResource(object):

    @use_args({'limit': fields.Int(), 'page': fields.Int(), 'lat': fields.Str(), 'lon': fields.Str()})
    def on_get(self, req, resp, args):
        page = args.get('page', 1)
        per_page_limit = args.get('limit', PER_PAGE_LIMIT)
        stops = self.session.query(Stop).filter()

        if args.get('lat') and args.get('lon'):
            pt = WKTElement('POINT({0} {1})'.format(args['lon'], args['lat']), srid=4326)
            stops = stops.order_by(Stop.geom.distance_box(pt))

        paginator = pager(stops, page, per_page_limit)
        #  serializer  results
        stop_schema = StopSchema()
        results = stop_schema.dump(paginator.items, many=True).data
        #  build body
        body = dict(
            has_next=paginator.has_next,
            total_results=paginator.total,
            total_pages=paginator.pages,
            results=results,
            page_size=len(results),
            page_number=paginator.page,
        )
        resp.body = json.dumps(body)


class StopResource(object):
    def on_get(self, req, resp, stop_id):
        stop = self.session.query(Stop).filter_by(stop_id=stop_id).one_or_none()
        if not stop:
            raise EntityNotFound()

        stop_schema = StopSchema()
        dump_data = stop_schema.dump(stop).data
        resp.body = json.dumps(dump_data)


class StopRoutesResource(object):
    def on_get(self, req, resp, stop_id):
        stop_routes = RouteStop.unique_routes_at_stop(
            session=self.session,
            stop_id=stop_id
        )
        route_schema = RouteSchema()
        results = route_schema.dump(stop_routes, many=True).data
        body = dict(results=results,)
        resp.body = json.dumps(body)


class StopScheduleCollectionResource(object):
    @use_args({'limit': fields.Int(), 'date': fields.Date(), 'arrival_time_after': fields.Time()})
    def on_get(self, req, resp, args, stop_id):

        stop_schedule = StopSchedule(stop_id)
        stop_schedule.as_dict(self.session)
        body = dict(results=stop_schedule.as_dict(self.session),)
        resp.body = json.dumps(body)


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
        resp.body = json.dumps(body)


class TripStopsCollectionResource(object):

    @use_args({'limit': fields.Int(), 'page': fields.Int()})
    def on_get(self, req, resp, args, trip_id):
        page = args.get('page', 1)
        per_page_limit = args.get('limit', PER_PAGE_LIMIT)

        trip = self.session.query(Trip).filter(
            Trip.trip_id == trip_id
        ).one_or_none()
        stops = []
        for stop_time in trip.stop_times:
            stops.append(stop_time.stop)

        stops = self.session.query(Stop).filter(Stop.stop_id.in_([stop.stop_id for stop in stops]))

        paginator = pager(stops, page, per_page_limit)
        #  serializer  results
        stop_schema = StopSchema()
        results = stop_schema.dump(paginator.items, many=True).data

        #  build body
        body = dict(
            has_next=paginator.has_next,
            total_results=paginator.total,
            total_pages=paginator.pages,
            results=results,
            page_size=len(results),
            page_number=paginator.page,
        )
        resp.body = json.dumps(body)



"""
App construction & route registration
"""


def add_routes(app):
    app.add_route('/api/v1/ping', HealthCheckResource())
    app.add_route('/api/v1/info', InfoResource())
    app.add_route('/api/v1/stops/', StopCollectionResource())
    app.add_route('/api/v1/stops/{stop_id}', StopResource())
    app.add_route('/api/v1/stops/{stop_id}/routes', StopRoutesResource())
    app.add_route('/api/v1/stops/{stop_id}/schedule', StopScheduleCollectionResource())
    app.add_route('/api/v1/stops/{stop_id}/schedule/{route_id}', StopScheduleResource())
    app.add_route('/api/v1/routes/', RouteCollectionResource())
    app.add_route('/api/v1/routes/{route_id}', RouteResource())
    app.add_route('/api/v1/trips/', TripCollectionResource())
    app.add_route('/api/v1/trips/{trip_id}', TripResource())  # TODO: order by sequence
    app.add_route('/api/v1/trips/{trip_id}/stops', TripStopsCollectionResource())  # TODO: order by sequence


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
        raven_client = Client()
        app.add_error_handler(Exception, internal_error_handler)

    return app
