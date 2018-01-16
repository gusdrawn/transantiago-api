import datetime
import time
import logging

from sqlalchemy import Column
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.types import Integer, String
from sqlalchemy.sql import func

from redis import Redis
import pickle
import os

from ..schemas import StopTimeSchema_v2, ShapeSchema
from ..settings import config
from .base import Base

log = logging.getLogger(__name__)
__all__ = ['RouteType', 'Route', 'RouteDirection', 'RouteFilter']


"""
Utils
"""


class RouteDirectionCache(object):
    _event_hash = None
    _connection = None

    def __init__(self, route_id, direction_id):
        self.redis_key = 'rdc|{}|{}'.format(route_id, direction_id)

    @property
    def is_enabled(self):
        if os.getenv('REDIS_CACHE_HOST') and os.getenv('REDIS_CACHE_PORT'):
            return True
        return False

    @property
    def connection(self):
        if not self.is_enabled:
            return None
        if not self._connection:
            self._connection = Redis(
                host=os.getenv('REDIS_CACHE_HOST'),
                port=int(os.getenv('REDIS_CACHE_PORT')),
                db=0
            )
        return self._connection

    def exists(self):
        return self.connection.exists(self.redis_key)

    # @@TODO: getter/setter
    def get_key(self):
        return pickle.loads(self.connection.get(self.redis_key))

    def set_key(self, data, cache_expiration):
        self.connection.set(self.redis_key, pickle.dumps(data), cache_expiration)

    def delete_key(self):
        self.connection.delete(self.redis_key)


"""
Models
"""


class RouteType(Base):
    datasource = config.DATASOURCE_LOOKUP
    filename = 'route_type.txt'
    __tablename__ = 'route_type'
    __table_args__ = {'extend_existing': config.EXISTING_SCHEMA_FLAG}

    route_type = Column(Integer, primary_key=True, index=True, autoincrement=False)
    route_type_name = Column(String(255))
    route_type_desc = Column(String(1023))


class RouteDirection(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'route_directions.txt'

    __tablename__ = 'route_directions'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    direction_id = Column(Integer, primary_key=True, index=True, nullable=False)
    direction_name = Column(String(255))
    direction_headsign = Column(String(255))
    # cache
    _active_trip = None
    _stop_times = None

    _cached_stop_times = None
    _cached_shape = None
    _cached_is_active = None

    route = relationship(
        'Route',
        primaryjoin='RouteDirection.route_id==Route.route_id',
        foreign_keys='(RouteDirection.route_id)',
        uselist=False, viewonly=True, lazy='joined')

    @classmethod
    def post_process(cls, db, **kwargs):
        log.debug('{0}.post_process'.format(cls.__name__))
        cls.populate(db.session)

    @property
    def is_active(self):
        if self.active_trip:
            return True
        return False

    @property
    def active_trip(self):
        from .trip import Trip
        if not self._active_trip:
            active_trips = Trip.get_active_trips_for_route(self.object_session, self.route_id, int(self.direction_id))
            if active_trips:
                self._active_trip = active_trips[0]
        return self._active_trip

    @property
    def _active_shape(self):
        if self.active_trip:
            return self.active_trip.pattern.shape
        return None

    @property
    def _active_stop_times(self):
        from .stop_time import StopTime
        if not self._active_trip:
            return None
        if not self._stop_times:
            self._stop_times = self.object_session.query(StopTime).filter(
                StopTime.trip_id == self._active_trip.trip_id
            ).order_by(StopTime.stop_sequence)
        return self._stop_times

    @property
    def trip_sample(self):
        from .trip import Trip
        return self.object_session.query(Trip).filter(
            Trip.route_id == self.route_id,
            Trip.direction_id == int(self.direction_id)
        ).first()

    @property
    def active_stop_times(self):
        if self._active_stop_times:
            return self._active_stop_times
        # fallback, get an arbitrary trip
        from .stop_time import StopTime
        return self.object_session.query(StopTime).filter(
            StopTime.trip_id == self.trip_sample.trip_id
        ).order_by(StopTime.stop_sequence)

    @property
    def active_shape(self):
        # @@TODO: temporary solution
        if self._active_shape:
            return self._active_shape
        return self.trip_sample.pattern.shape

    def _set_data(self):
        if not self._cached_stop_times or not self._cached_shape:
            route_direction_cache = RouteDirectionCache(route_id=self.route_id, direction_id=int(self.direction_id))
            if not route_direction_cache.is_enabled or not route_direction_cache.exists():
                from .trip import Trip
                # get processed data for RouteDirection
                trip, stop_times, is_active, cache_expiration = Trip.get_trip_data_for_route(
                    self.object_session,
                    self.route_id,
                    int(self.direction_id)
                )
                # serialize response
                stop_times_schema = StopTimeSchema_v2()
                stop_times_data = stop_times_schema.dump(stop_times, many=True).data
                shape_schema = ShapeSchema()
                shape_data = shape_schema.dump(trip.pattern.shape, many=True).data
                data = {
                    'stop_times': stop_times_data,
                    'shape': shape_data,
                    'is_active': is_active
                }
                # set cache
                if route_direction_cache.is_enabled:
                    route_direction_cache.set_key(data, cache_expiration)
                # set values
                self._cached_stop_times = stop_times_data
                self._cached_shape = shape_data
                self._cached_is_active = is_active
            else:
                # hit cache
                data = route_direction_cache.get_key()
                self._cached_stop_times = data['stop_times']
                self._cached_shape = data['shape']
                self._cached_is_active = data['is_active']

    @property
    def trip_shape(self):
        if not self._cached_shape:
            self._set_data()
        return self._cached_shape

    @property
    def trip_stop_times(self):
        if not self._cached_stop_times:
            self._set_data()
        return self._cached_stop_times

    @property
    def trip_is_active(self):
        if not self._cached_is_active:
            self._set_data()
        return self._cached_is_active

    @classmethod
    def populate(cls, session):
        """
        Populate RouteDirection.direction_headsign using stop_time.headsign or trip.trip_headsign (fallback)
        """
        from .stop_time import StopTime
        from .trip import Trip

        stop_times = session.query(StopTime).filter().distinct(StopTime.stop_id)
        results_to_update = []
        # collect headsigns from StopTime
        for stop_time in stop_times:
            stop_times_for_stop = session.query(StopTime).filter(StopTime.stop_id == stop_time.stop_id)
            results = {}
            for unique_stop_time in stop_times_for_stop:
                headsign = stop_time.get_headsign()
                direction_id = stop_time.trip.direction_id
                key = '{}|{}'.format(stop_time.trip.route_id, direction_id)
                if not results.get(key):
                    results[key] = headsign
                else:
                    if results[key] != headsign:
                        log.warning('{0}.post_process -> multiple headsigns for route'.format(cls.__name__))
            for r, headsign in results.items():
                results_to_update.append({
                    'route_id': r.split('|')[0],
                    'direction_id': r.split('|')[1],
                    'direction_headsign': headsign
                })

        for result in results_to_update:
            # update Route Direction
            route_direction = session.query(RouteDirection).filter(
                RouteDirection.route_id == result['route_id'],
                RouteDirection.direction_id == int(result['direction_id'])
            ).first()
            route_direction.direction_headsign = result['direction_headsign']
            session.add(route_direction)

        session.commit()

        # collect headsigns from Trip for remaining records (empty RouteDirection.direction_headsign)
        results_to_update = []
        empty_route_directions = session.query(RouteDirection).filter(RouteDirection.direction_headsign == None)
        for route_direction in empty_route_directions:
            # analyze all trips with match for route_direction
            trips = session.query(Trip).filter(Trip.route_id == route_direction.route_id)
            trip_headsigns = []
            for trip in trips:
                if trip.direction_id != route_direction.direction_id:
                    continue
                trip_headsigns.append(trip.trip_headsign)

            result = {}
            if len(set(trip_headsigns)) > 1:
                print route_direction.route_id, trip_headsigns
            elif len(set(trip_headsigns)) == 1:
                key = "{}|{}".format(route_direction.route_id, route_direction.direction_id)
                result[key] = trip_headsigns[0]
            else:
                log.warning('{}.post_process -> No info for'.format(cls.__name__, route_direction.route_id))
            for r, headsign in result.items():
                results_to_update.append({
                    'route_id': r.split('|')[0],
                    'direction_id': r.split('|')[1],
                    'direction_headsign': headsign
                })

        for result in results_to_update:
            # update Route Direction
            route_direction = session.query(RouteDirection).filter(
                RouteDirection.route_id == result['route_id'],
                RouteDirection.direction_id == int(result['direction_id'])
            ).first()
            route_direction.direction_headsign = result['direction_headsign']
            session.add(route_direction)

        session.commit()

        # safety check
        if session.query(RouteDirection).filter(RouteDirection.direction_headsign.is_(None)).count():
            log.warning('{}.post_process -> RouteDirection without direction_headsign'.format(cls.__name__))


class Route(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'routes.txt'

    __tablename__ = 'routes'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    agency_id = Column(String(255), index=True, nullable=True)
    route_short_name = Column(String(255))
    route_long_name = Column(String(255))
    route_desc = Column(String(1023))
    route_type = Column(Integer, index=True, nullable=False)
    route_url = Column(String(255))
    route_color = Column(String(6))
    route_text_color = Column(String(6))
    route_sort_order = Column(Integer, index=True)
    min_headway_minutes = Column(Integer)  # Trillium extension.

    trips = relationship(
        'Trip',
        primaryjoin='Route.route_id==Trip.route_id',
        foreign_keys='(Route.route_id)',
        uselist=True, viewonly=True)

    directions = relationship(
        'RouteDirection',
        primaryjoin='Route.route_id==RouteDirection.route_id',
        foreign_keys='(Route.route_id)',
        uselist=True, viewonly=True, lazy='joined')

    @property
    def route_name(self, fmt="{self.route_short_name}-{self.route_long_name}"):
        """ build a route name out of long and short names...
        """
        if not self.is_cached_data_valid('_route_name'):
            log.warn("query route name")
            ret_val = self.route_long_name
            if self.route_long_name and self.route_short_name:
                ret_val = self.route_short_name + "-" + self.route_long_name
            elif self.route_long_name is None:
                ret_val = self.route_short_name
            self._route_name = ret_val
            self.update_cached_data('_route_name')

        return self._route_name

    def direction_name(self, direction_id, def_val=''):
        ret_val = def_val
        try:
            dir = self.directions.filter(RouteDirection.direction_id==direction_id)
            if dir and dir.direction_name:
                ret_val = dir.direction_name
        except:
            pass
        return ret_val

    def is_active(self, date=None):
        """ :return False whenever we see that the route start and end date are outside the
                    input date (where the input date defaults to 'today')
        """
        _is_active = True
        if self.start_date and self.end_date:
            _is_active = False
            if date is None:
                date = datetime.date.today()
            if self.start_date <= date <= self.end_date:
                _is_active = True
        return _is_active

    @property
    def _get_start_end_dates(self):
        """find the min & max date using Trip & UniversalCalendar"""
        if not self.is_cached_data_valid('_start_date'):
            from gtfsdb.model.calendar import UniversalCalendar
            q = self.session.query(func.min(UniversalCalendar.date), func.max(UniversalCalendar.date))
            q = q.filter(UniversalCalendar.trips.any(route_id=self.route_id))
            self._start_date, self._end_date = q.one()
            self.update_cached_data('_start_date')

        return self._start_date, self._end_date

    @property
    def start_date(self):
        return self._get_start_end_dates[0]

    @property
    def end_date(self):
        return self._get_start_end_dates[1]

    @classmethod
    def load_geoms(cls, db):
        """load derived geometries, currently only written for PostgreSQL"""
        from gtfsdb.model.shape import Pattern
        from gtfsdb.model.trip import Trip

        if db.is_geospatial and db.is_postgresql:
            start_time = time.time()
            session = db.session
            routes = session.query(Route).all()
            for route in routes:
                s = func.st_collect(Pattern.geom)
                s = func.st_multi(s)
                s = func.st_astext(s).label('geom')
                q = session.query(s)
                q = q.filter(Pattern.trips.any((Trip.route == route)))
                route.geom = q.first().geom
                session.merge(route)
            session.commit()
            processing_time = time.time() - start_time
            log.debug('{0}.load_geoms ({1:.0f} seconds)'.format(
                cls.__name__, processing_time))

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            cls.geom = deferred(Column(Geometry('MULTILINESTRING')))

    @classmethod
    def active_routes(cls, session, date=None):
        """ returns list of routes that are seen as 'active' based on dates and filters
        """
        ret_val = []

        # step 1: grab all stops
        routes = session.query(Route).filter(~Route.route_id.in_(session.query(RouteFilter.route_id))).order_by(Route.route_sort_order).all()

        # step 2: default date
        if date is None or not isinstance(date, datetime.date):
            date = datetime.date.today()

        # step 3: filter routes by active date
        #         NOTE: r.start_date and r.end_date are properties, so have to do in code vs. query
        for r in routes:
            if r:
                # step 3a: filter based on date (if invalid looking date objects, just pass the route on)
                if r.start_date and r.end_date:
                    if r.start_date <= date <= r.end_date:
                        ret_val.append(r)
                else:
                    ret_val.append(r)
        return ret_val

    @classmethod
    def active_route_ids(cls, session):
        """ return an array of route_id / agency_id pairs
            {route_id:'2112', agency_id:'C-TRAN'}
        """
        ret_val = []
        routes = cls.active_routes(session)
        for r in routes:
            ret_val.append({"route_id":r.route_id, "agency_id": r.agency_id})
        return ret_val


class RouteFilter(Base):
    """ list of filters to be used to cull routes from certain lists
        e.g., there might be Shuttles that you never want to be shown...you can load that data here, and
        use it in your queries
    """
    datasource = config.DATASOURCE_LOOKUP
    filename = 'route_filter.txt'
    __tablename__ = 'route_filters'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    agency_id = Column(String(255), index=True, nullable=True)
    description = Column(String)
