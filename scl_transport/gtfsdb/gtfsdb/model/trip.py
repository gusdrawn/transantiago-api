import logging

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from datetime import datetime, date

from ..settings import config
from ..util import get_now_datetime
from .base import Base

log = logging.getLogger(__name__)


class Trip(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'trips.txt'

    __tablename__ = 'trips'
    __table_args__ = {'extend_existing': config.EXISTING_SCHEMA_FLAG}

    trip_id = Column(String(255), primary_key=True, index=True, nullable=False)
    route_id = Column(String(255), index=True, nullable=False)
    service_id = Column(String(255), index=True, nullable=False)
    direction_id = Column(Integer, index=True)
    block_id = Column(String(255), index=True)
    shape_id = Column(String(255), index=True, nullable=True)
    trip_type = Column(String(255))

    trip_headsign = Column(String(255))
    trip_short_name = Column(String(255))
    bikes_allowed = Column(Integer, default=0)
    wheelchair_accessible = Column(Integer, default=0)

    pattern = relationship(
        'Pattern',
        primaryjoin='Trip.shape_id==Pattern.shape_id',
        foreign_keys='(Trip.shape_id)',
        lazy='select',
        uselist=False, viewonly=True)

    route = relationship(
        'Route',
        primaryjoin='Trip.route_id==Route.route_id',
        foreign_keys='(Trip.route_id)',
        lazy='select',
        uselist=False, viewonly=True)

    stop_times = relationship(
        'StopTime',
        primaryjoin='Trip.trip_id==StopTime.trip_id',
        foreign_keys='(Trip.trip_id)',
        order_by='StopTime.stop_sequence',
        lazy='select',
        uselist=True, viewonly=True)

    frequency = relationship(
        'Frequency',
        primaryjoin='Frequency.trip_id==Trip.trip_id',
        foreign_keys='(Frequency.trip_id)',
        lazy='select',
        uselist=False, viewonly=True)

    universal_calendar = relationship(
        'UniversalCalendar',
        primaryjoin='Trip.service_id==UniversalCalendar.service_id',
        foreign_keys='(Trip.service_id)',
        lazy='select',
        uselist=True, viewonly=True)

    @classmethod
    def post_process(cls, db, **kwargs):
        trips = db.session.query(Trip).all()
        for t in trips:
            if not t.is_valid:
                log.warn("invalid trip: {0} only has {1} stop_time record (i.e., maybe the stops are coded as "
                         "non-public, and thus their stop time records didn't make it into the gtfs)"
                         .format(t.trip_id, t.trip_len))

    @property
    def start_stop(self):
        return self.stop_times[0].stop

    @property
    def end_stop(self):
        return self.stop_times[-1].stop

    @property
    def start_time(self):
        return self.stop_times[0].departure_time

    @property
    def end_time(self):
        return self.stop_times[-1].arrival_time

    @property
    def trip_len(self):
        ret_val = 0
        if self.stop_times:
            ret_val = len(self.stop_times)
        return ret_val

    @property
    def is_valid(self):
        # trip has to have multiple stop times to be valid, else it's not a trip...
        return self.trip_len >= 2

    @classmethod
    def get_active_trips_for_route(cls, session, route_id, direction_id=None):
        from .stop_time import StopTime
        stop_times = StopTime.get_active_stop_times_for_route(session, route_id, direction_id)
        return [stop_time.trip for stop_time in stop_times]

    @classmethod
    def get_trip_data_for_route(cls, session, route_id, direction_id):
        from .stop_time import StopTime
        from .frequency import Frequency
        now = get_now_datetime()
        # get stop times for <route_id>, <direction_id>
        trips = session.query(Trip).filter(Trip.route_id == route_id, Trip.direction_id == int(direction_id))
        trip_ids = [trip.trip_id for trip in trips]
        stop_times_results = StopTime.get_departure_schedule(session, date=now.date(), trip_ids=trip_ids)

        # filter stop times on Frequency
        stop_times = session.query(StopTime).join(Trip, Trip.trip_id == StopTime.trip_id).filter(
            Trip.trip_id.in_(trip_ids)
        )
        stop_times = stop_times.join(StopTime.frequency).filter(
            StopTime.id.in_([stop_time.id for stop_time in stop_times_results]),
            Frequency.start_time <= now.time(),
            Frequency.end_time >= now.time()
        )
        # fallback: get an arbitrary trip (is_active=False) if there is not an active trip
        if not stop_times.count():
            cache_expiration = 60  # the result is only valid 60 in this case
            is_active = False
            trip = session.query(Trip).filter(
                Trip.route_id == route_id,
                Trip.direction_id == int(direction_id)
            ).first()
            stop_times = session.query(StopTime).filter(
                StopTime.trip_id == trip.trip_id).order_by(StopTime.stop_sequence)
            return trip, stop_times, is_active, 60
        else:
            is_active = True
            trip = stop_times.first().trip
            # check if extra filter for stoptimes is required
            if stop_times.distinct(StopTime.trip_id).count() > 1:
                stop_times = stop_times.filter(StopTime.trip_id == trip.trip_id)
            # get validity (cache) in seconds
            frequency = session.query(Frequency).filter(Frequency.trip_id == trip.trip_id).first()
            end_t = datetime.combine(date.today(), frequency.end_time)
            now_t = datetime.combine(date.today(), now.time())
            cache_expiration = (end_t - now_t).seconds
            return trip, stop_times, is_active, cache_expiration

    @classmethod
    def get_trips_for_stop(cls, session, stop_id, route_id=None, only_active=False):
        from .stop_time import StopTime
        if only_active:
            stop_times = StopTime.get_active_stop_times_for_stop(
                session=session,
                stop_id=stop_id,
                route_id=route_id
            )
            return [stop_time.trip for stop_time in stop_times]
        else:
            # @@TODO: improve route_id filter (query instead this)
            stop_times = session.query(StopTime).filter(
                StopTime.stop_id == stop_id
            ).distinct(StopTime.trip_id)
            if route_id:
                return [stop_time.trip for stop_time in stop_times if stop_time.trip.route_id == route_id]
            return [stop_time.trip for stop_time in stop_times]
