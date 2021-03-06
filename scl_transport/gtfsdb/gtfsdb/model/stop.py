import logging
import datetime
from collections import defaultdict

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, Numeric, String, PickleType, Boolean
from sqlalchemy.orm import joinedload_all, object_session, relationship

from ..settings import config
from ..schemas import StopRouteSchema_v2
from ..data_augmenters import (
    RouteStopDirectionAugmenter,
    RouteStopAugmenter
)
from .. import util
from .base import Base

log = logging.getLogger(__name__)


class Stop(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stops.txt'

    __tablename__ = 'stops'
    __table_args__ = {'extend_existing': config.EXISTING_SCHEMA_FLAG}

    stop_id = Column(String(255), primary_key=True, index=True, nullable=False)
    stop_code = Column(String(50))
    stop_name = Column(String(255), nullable=False)
    stop_desc = Column(String(255))
    stop_lat = Column(Numeric(12, 9), nullable=False)
    stop_lon = Column(Numeric(12, 9), nullable=False)
    zone_id = Column(String(50))
    stop_url = Column(String(255))
    location_type = Column(Integer, index=True, default=0)
    parent_station = Column(String(255))
    stop_timezone = Column(String(50))
    wheelchair_boarding = Column(Integer, default=0)
    platform_code = Column(String(50))
    direction = Column(String(50))
    position = Column(String(50))
    agency_id = Column(String(255), index=True, nullable=True)

    # internal use
    _stop_routes = Column("stop_routes", PickleType)  # cache
    route_directions = Column(PickleType)
    multi_directional = Column(Boolean, nullable=True)  # support more than 1 direction for the same route

    stop_features = relationship(
        'StopFeature',
        primaryjoin='Stop.stop_id==StopFeature.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=True, viewonly=True)

    stop_times = relationship(
        'StopTime',
        primaryjoin='Stop.stop_id==StopTime.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=True, viewonly=True)

    directions = relationship(
        'StopDirection',
        primaryjoin='Stop.stop_id==StopDirection.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=True, viewonly=True, lazy='joined')

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = Column(Geometry(geometry_type='POINT', srid=config.SRID))

    @classmethod
    def add_geom_to_dict(cls, row):
        args = (config.SRID, row['stop_lon'], row['stop_lat'])
        row['geom'] = 'SRID={0};POINT({1} {2})'.format(*args)

    @property
    def stop_routes(self):
        from .route_stop import RouteStop
        if not self._stop_routes:
            stop_routes = self.session.query(RouteStop).filter(RouteStop.stop_id == self.stop_id)
            stop_route_schema = StopRouteSchema_v2()
            results = stop_route_schema.dump(stop_routes, many=True).data
            self._stop_routes = results
            self.object_session.add(self)
            self.object_session.commit()
        return self._stop_routes

    @property
    def stop_routes_old(self):
        stop_routes = self.stop_routes
        for stop_route in stop_routes:
            stop_route.pop('is_last_stop')
            stop_route.pop('is_first_stop')
        return stop_routes

    @property
    def headsigns(self):
        """ Returns a dictionary of all unique (route_id, headsign) tuples used
            at the stop and the number of trips the head sign is used
        """
        if not hasattr(self, '_headsigns'):
            from gtfsdb.model.stop_time import StopTime
            self._headsigns = defaultdict(int)
            session = object_session(self)
            #log.info("QUERY StopTime")
            q = session.query(StopTime)
            q = q.options(joinedload_all('trip.route'))
            q = q.filter_by(stop_id=self.stop_id)
            for r in q:
                headsign = r.stop_headsign or r.trip.trip_headsign
                self._headsigns[(r.trip.route, headsign)] += 1
        return self._headsigns

    @property
    def agencies(self):
        """ return list of agency ids with routes hitting this stop
            @todo: rewrite the cache to use timeout checking in Base.py
        """
        try:
            self._agencies
        except AttributeError:
            self._agencies = []
            if self.routes:
                for r in self.routes:
                    if r.agency_id not in self._agencies:
                        self.agencies.append(r.agency_id)
        return self._agencies

    def is_active(self, date=None):
        """ :return False whenever we see that the stop has zero stop_times on the given input date
                    (which defaults to 'today')

            @NOTE: use caution with this routine.  calling this for multiple stops can really slow things down,
                   since you're querying large trip and stop_time tables, and asking for a schedule of each stop
                   I used to call this multiple times via route_stop to make sure each stop was active ... that
                   was really bad performance wise.
        """
        _is_active = False
        if date is None:
            date = datetime.date.today()

        #import pdb; pdb.set_trace()
        from .stop_time import StopTime
        st = StopTime.get_departure_schedule(self.session, self.stop_id, date, limit=1)
        if st and len(st) > 0:
            _is_active = True
        return _is_active

    def is_multi_directional(self, session):
        hash_s = {}
        from .route_stop import RouteStop
        for route_stop in session.query(RouteStop).filter(RouteStop.stop_id == self.stop_id):
            key = '{}'.format(route_stop.route_id, route_stop.direction_id)
            if hash_s.get(key):
                return True
            hash_s[key] = 1
        return False

    @classmethod
    def active_stops(cls, session, limit=None, active_filter=True, date=None):
        """ check for active stops
        """
        ret_val = None

        # step 1: get stops
        q = session.query(Stop)
        if limit:
            q = q.limit(limit)
        stops = q.all()

        # step 2: filter active stops only ???
        if active_filter:
            ret_val = []
            for s in stops:
                if s.is_active(date):
                    ret_val.append(s)
        else:
            ret_val = stops

        return ret_val

    @classmethod
    def active_stop_ids(cls, session, limit=None, active_filter=True):
        """ return an array of stop_id / agencies pairs
            {stop_id:'2112', agencies:['C-TRAN', 'TRIMET']}
        """
        ret_val = []
        stops = cls.active_stops(session, limit, active_filter)
        for s in stops:
            ret_val.append({"stop_id": s.stop_id, "agencies": s.agencies})
        return ret_val


class StopDirection(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stop_directions.txt'

    __tablename__ = 'stop_directions'

    stop_id = Column(String(255), primary_key=True, index=True, nullable=False)
    direction_id = Column(Integer, primary_key=True, index=True, nullable=False)
    direction_name = Column(String(255))
    direction_headsign = Column(String(255))

    stop = relationship(
        'Stop',
        primaryjoin='StopDirection.stop_id==Stop.stop_id',
        foreign_keys='(StopDirection.stop_id)',
        uselist=False, viewonly=True, lazy='joined')

    @classmethod
    def post_process(cls, db, **kwargs):
        log.debug('{0}.post_process'.format(cls.__name__))
