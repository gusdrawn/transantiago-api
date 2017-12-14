# -*- coding: utf-8 -*-

import datetime
import logging
log = logging.getLogger(__name__)

import time
import arrow
from sqlalchemy import Column, and_
from sqlalchemy.orm import relationship, joinedload_all
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Boolean, Integer, Numeric, String, Time, BigInteger

from ..settings import config
from ..util import convert_str_to_time
from .base import Base
from .frequency import Frequency
from .trip import Trip


def _get_now():
    now = arrow.now('America/Santiago')
    n = arrow.get(now.naive)
    return n


class StopTime(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stop_times.txt'

    __tablename__ = 'stop_times'
    __table_args__ = {'extend_existing': config.EXISTING_SCHEMA_FLAG}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trip_id = Column(String(255), primary_key=True, index=True, nullable=False)
    stop_id = Column(String(255), index=True, nullable=False)
    stop_sequence = Column(Integer, primary_key=True, nullable=False)
    arrival_time = Column(Time)
    departure_time = Column(Time, index=True)
    stop_headsign = Column(String(255))
    pickup_type = Column(Integer, default=0)
    drop_off_type = Column(Integer, default=0)
    shape_dist_traveled = Column(Numeric(20, 10))
    timepoint = Column(Boolean, index=True, default=False)

    stop = relationship(
        'Stop',
        primaryjoin='Stop.stop_id==StopTime.stop_id',
        foreign_keys='(StopTime.stop_id)',
        uselist=False, viewonly=True)

    trip = relationship(
        'Trip',
        primaryjoin='Trip.trip_id==StopTime.trip_id',
        foreign_keys='(StopTime.trip_id)',
        uselist=False, viewonly=True)

    # @@TODO: temporary
    frequency = relationship(
        'Frequency',
        primaryjoin='Frequency.trip_id==StopTime.trip_id',
        foreign_keys='(Frequency.trip_id)',
        uselist=False, viewonly=True)

    def __init__(self, *args, **kwargs):
        super(StopTime, self).__init__(*args, **kwargs)
        if 'timepoint' not in kwargs:
            self.timepoint = 'arrival_time' in kwargs

    def __repr__(self):
        """Default repr"""
        if hasattr(self, "id"):
            return "<%s %s>" % (self.__class__.__name__, self.id)
        else:
            return super(StopTime, self).__repr__()

    def get_headsign(self):
        """ get the headsign at this stop ... rule is that if stop is empty, use trip headsign """
        ret_val = self.stop_headsign
        if not ret_val:
            ret_val = self.trip.trip_headsign
        return ret_val

    def get_direction_name(self, def_val="", banned=['Shuttle', 'MAX Shuttle', 'Garage', 'Center Garage', 'Merlo Garage', 'Powell Garage']):
        """ returns either the headsign (priority) or the route direction name (when banned)
            (as long as one of these names are not banned and not the same name as the route name)
        """
        ret_val = def_val
        try:
            # step 0: create a banned list with the addition of our route_long_name
            banned = banned + [self.trip.route.route_long_name]

            headsign = self.get_headsign()
            if headsign and not any([headsign in s for s in banned]):
                # step 1: use the headsign as the direction name, just as long as the headsign is
                #         not null and not the same as the route name
                ret_val = headsign
            else:
                # step 2: lets use the direction name, if available
                d = self.trip.route.directions[self.trip.direction_id]
                if d.direction_name and not any([d.direction_name in s for s in banned]):
                    ret_val = d.direction_name.lstrip('to ').lstrip('To ')
        except Exception, e:
            log.debug(e)
            pass
        return ret_val

    def is_boarding_stop(self):
        """ return whether the vehicle that is stopping at this stop, and at this time, is an
            in-revenue vehicle that a customer can actually board...

            pickup_type = 1 - No pickup available

            departure_time = None

            NOTE: in gtfsdb, we NULL out the departure times when the vehicle doesn't
                  pick up anyone (e.g., at route end points, there are no departures...)

            @see: https://developers.google.com/transit/gtfs/reference#stop_times_fields
        """
        ret_val = True
        if self.pickup_type == 1 or self.departure_time is None:
            ret_val = False
        return ret_val

    @classmethod
    def post_process(cls, db, **kwargs):
        log.debug('{0}.post_process'.format(cls.__name__))
        #cls.null_out_last_stop_departures(db) ## commented out due to other processes
        pass

    @classmethod
    def null_out_last_stop_departures(cls, db):
        """ delete all 'depature_time' values that appear for the last stop
            time of a given trip (e.g., the trip ends there, so there isn't a
            further vehicle departure / customer pickup for that stop time / trip pair)...

            -- query below shows null'd out stop times
            select * from ott.stop_times
            where COALESCE(arrival_time,'')='' or COALESCE(departure_time,'')=''

            NOTE: we know this breaks the current GTFS spec, which states that departure &
                  arrival times must both exist for every stop time.  Sadly, GTFS is kinda wrong...
        """
        # step 1: remove the departure times at the end of a trip
        log.info("QUERY StopTime for all trip end times")
        sq = db.session.query(StopTime.trip_id, func.max(StopTime.stop_sequence).label('end_sequence'))
        sq = sq.group_by(StopTime.trip_id).subquery()
        q = db.session.query(StopTime)
        q = q.filter_by(trip_id=sq.c.trip_id, stop_sequence=sq.c.end_sequence)
        for st in q:
            if st.pickup_type == 1:
                st.departure_time = None

        # remove the arrival times at the start of a trip
        log.info("QUERY StopTime for all trip start times")
        sq = db.session.query(StopTime.trip_id, func.min(StopTime.stop_sequence).label('start_sequence'))
        sq = sq.group_by(StopTime.trip_id).subquery()
        q = db.session.query(StopTime)
        q = q.filter_by(trip_id=sq.c.trip_id, stop_sequence=sq.c.start_sequence)
        for st in q:
            if st.drop_off_type == 1:
                st.arrival_time = None

        db.session.flush()
        db.session.commit()
        db.session.close()

    @classmethod
    def get_service_keys_from_list(cls, stop_times):
        ret_val = []
        for s in stop_times:
            k = s.trip.service_id
            if k not in ret_val:
                ret_val.append(k)
        return ret_val


    @classmethod
    def get_departure_schedule(
        cls,
        session,
        stop_id=None,
        date=None,
        route_id=None,
        trip_ids=None,
        limit=None
    ):
        """ helper routine which returns the stop schedule for a give date
        """
        from .trip import Trip

        # step 0: make sure we have a valid date
        if date is None:
            date = datetime.date.today()

        # step 1: get stop times based on date
        #log.debug("QUERY StopTime")
        q = session.query(StopTime)
        if stop_id:
            q = q.filter_by(stop_id=stop_id)

        if trip_ids:
            q = q.filter(StopTime.trip_id.in_(trip_ids))

        q = q.filter(StopTime.departure_time is not None)

        # step 2: apply an optional route filter
        if route_id:
            q = q.filter(
                and_(
                    Trip.route_id == route_id,
                    StopTime.trip.has(Trip.universal_calendar.any(date=date))
                )
            )
        else:
            q = q.filter(StopTime.trip.has(Trip.universal_calendar.any(date=date)))

        # step 3: options to speed up /q
        q = q.options(joinedload_all('trip'))

        # step 4: order the stop times
        if limit is None or limit > 1:
            q = q.order_by(StopTime.departure_time)

        # step 5: limit results
        if limit:
            q = q.limit(limit)

        stop_times = q.all()
        ret_val = cls.block_filter(session, stop_id, stop_times)
        return ret_val

    @classmethod
    def get_active_stop_times_for_route(cls, session, route_id, direction_id=None):
        now = _get_now()
        trips = session.query(Trip).filter(Trip.route_id == route_id)
        if direction_id:
            trips = trips.filter(Trip.direction_id == int(direction_id))
        trip_ids = [trip.trip_id for trip in trips]

        stop_times_results = cls.get_departure_schedule(session, date=now.date(), trip_ids=trip_ids)
        # 2) filter
        stop_times = session.query(StopTime).join(StopTime.frequency).filter(
            StopTime.id.in_([stop_time.id for stop_time in stop_times_results]),
            Frequency.start_time <= now.time(),
            Frequency.end_time >= now.time()
        ).distinct(StopTime.trip_id)
        results = []
        if route_id:
            for stop_time in stop_times:
                if stop_time.trip.route_id == route_id:
                    results.append(stop_time)
                    return results
        else:
            results = stop_times.all()
        return results

    @classmethod
    def get_active_stop_times_for_stop(cls, session, stop_id, route_id=None):
        now = _get_now()
        # 1) get stop_time valid on date
        stop_times_results = cls.get_departure_schedule(session, stop_id=stop_id, date=now.date(), route_id=route_id)
        # 2) filter
        stop_times = session.query(StopTime).join(StopTime.frequency).filter(
            StopTime.id.in_([stop_time.id for stop_time in stop_times_results]),
            Frequency.start_time <= now.time(),
            Frequency.end_time >= now.time()
        )
        results = []
        if route_id:
            for stop_time in stop_times:
                if stop_time.trip.route_id == route_id:
                    results.append(stop_time)
                    return results
        else:
            results = stop_times.all()
        return results

    @classmethod
    def block_filter(cls, session, stop_id, stop_times):
        """ we don't want to show stop times that are arrivals, so we look at the blocks and figure out whether
            the input stop is the ending stop, and that there's a next trip starting at this same stop.
        """
        ret_val = stop_times
        if stop_times and len(stop_times) > 1:
            from scl_transport.gtfsdb.gtfsdb.model.block import Block
            keys = cls.get_service_keys_from_list(stop_times)
            blocks = Block.blocks_by_end_stop_id(session, stop_id, service_keys=keys)
            if blocks:
                ret_val = []
                for s in stop_times:
                    block = None
                    for b in blocks:
                        if s.trip_id == b.trip_id and s.trip.block_id == b.block_id:
                            block = b
                            blocks.remove(b)
                            break

                    if block is None:
                        ret_val.append(s)
                    elif not block.is_arrival(stop_id):
                            ret_val.append(s)
                            # @todo maybe monkey patch stop_time with block, so we know about last trip

                            # this is an arrival trip, and the next trip
                            # (don't return the stop_time as a departure)
                            # this is the last trip of the day (so return it)
        return ret_val


LIMIT_PER_ROUTE = 2


class StopSchedule(object):
    def __init__(self, stop_id, route_id=None, from_datetime=None):
        self.stop_id = stop_id
        self.route_id = route_id
        self.from_datetime = from_datetime

    def _build_datetime(self, input_date, input_time):
        dt = arrow.get(input_date)
        dt = dt.replace(hour=input_time.hour)
        dt = dt.replace(minute=input_time.minute)
        dt = dt.replace(second=input_time.second)
        return arrow.get(dt)

    def _get_time_seconds(self, input_time):
        return datetime.timedelta(
            hours=input_time.hour,
            minutes=input_time.minute,
            seconds=input_time.second
        ).total_seconds()

    def _filter_on_frequency(self, now, query, route_id):
        results = []
        # @@TODO: improve this query (avoid post-process)
        stop_times = query.join(StopTime.frequency).filter(
            Trip.route_id == route_id,
            Frequency.start_time <= now.time(),
            Frequency.end_time >= now.time()
        ).order_by(StopTime.trip_id, Frequency.start_time)

        for stop_time in stop_times:
            if stop_time.trip.route_id == route_id:
                results.append(stop_time)
                return results
        return results

    def _next_route_schedule(self, now, route_id, stop_time):
        if not stop_time:
            return []

        arrival_time = stop_time.arrival_time
        arrival_seconds_offset = self._get_time_seconds(arrival_time)
        start_datetime = self._build_datetime(now.date(), stop_time.frequency.start_time)
        end_datetime = self._build_datetime(now.date(), stop_time.frequency.end_time)

        route_schedule = []

        # get closest
        headway_secs = stop_time.trip.frequency.headway_secs
        n = (now - start_datetime).seconds / headway_secs
        start_datetime = start_datetime.replace(seconds=n * headway_secs)

        for i in range(100):
            if len(route_schedule) >= LIMIT_PER_ROUTE:
                break
            if start_datetime > end_datetime:
                # @@TODO: is this possible?
                break
            datetime_to_cast = start_datetime.replace(seconds=arrival_seconds_offset)
            if datetime_to_cast.second > 30:  # round
                formatted_arrival_time = arrow.get(datetime_to_cast).replace(minutes=1).format('HH:mm')
            else:
                formatted_arrival_time = arrow.get(datetime_to_cast).format('HH:mm')
            if datetime_to_cast >= now.datetime:
                calculated_at = now.format('YYYY-MM-DD HH:mm:ss')

                if headway_secs:
                    headway_mins = int(headway_secs) / 60
                    if int(headway_secs) % 60 > 30:
                        headway_mins += 1
                    arrival_prediction_message = 'Cada {} min.'.format(headway_mins)
                else:
                    arrival_prediction_message = ''

                route_schedule.append({
                    'calculated_at': calculated_at,
                    'arrival_prediction_message': arrival_prediction_message,
                    'route_id': stop_time.trip.route_id,
                    'stop_id': stop_time.stop_id,
                    'trip_id': stop_time.trip_id,
                    'headway_secs': headway_secs,
                    'arrival_timestamp': datetime_to_cast.timestamp,
                    'arrival_date': arrow.get(datetime_to_cast).format('YYYY-MM-DD'),
                    'arrival_time': formatted_arrival_time
                })
            start_datetime = arrow.get(start_datetime).replace(seconds=stop_time.frequency.headway_secs)
        return route_schedule

    def _populate_route_schedule(self, now, route_id, next_stop_times):
        route_schedule = []
        if not next_stop_times:
            return []
        while next_stop_times:
            stop_time = next_stop_times.pop(0)
            if len(route_schedule) >= LIMIT_PER_ROUTE:
                break
            route_schedule.extend(self._next_route_schedule(now, route_id, stop_time))
        return route_schedule

    def _get_now(self):
        now = arrow.now('America/Santiago')
        n = arrow.get(now.naive)
        return n

    def as_dict(self, session):
        now = self._get_now()
        stop_id = self.stop_id
        given_route_id = self.route_id

        stop_times = StopTime.get_departure_schedule(
            session=session,
            stop_id=stop_id,
            date=now.date(),
            route_id=self.route_id
        )

        # 1) build base query
        stop_time_ids = [stop_time.id for stop_time in stop_times]
        query = session.query(StopTime).filter(StopTime.id.in_(stop_time_ids))

        # 2) get distinct routes, TODO: query
        distinct_route_ids = []
        for stop_time in query:
            if stop_time.trip.route_id not in distinct_route_ids:
                distinct_route_ids.append(stop_time.trip.route_id)

        # 3) TODO: get distinct trips
        query = query.distinct(StopTime.trip_id)

        # 4) get stop_times for route in frequency <route_id>: <first_stop_time>, <optional_second_stop_time>
        route_stop_time_map = {}
        for route_id in distinct_route_ids:
            if given_route_id and route_id != given_route_id:
                continue
            route_stop_time_map[route_id] = self._filter_on_frequency(now, query, route_id)

        # 4) extraer mas cercano mayor a now(), ejm: a cada 5 minutos (Frequency.headway_secs) en el 65min(StopTime.arrival_time) desde inicio ruta
        results = []
        for route_id, stop_times in route_stop_time_map.items():
            route_schedule = self._populate_route_schedule(now, route_id, stop_times)
            results.extend(route_schedule)
        results = sorted(results, key=lambda k: k['arrival_timestamp'])

        return results
