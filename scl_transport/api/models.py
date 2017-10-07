# -*- coding: utf-8 -*-
"""Main models."""
import arrow
import time
import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Date,
    Time,
    ForeignKey
)
from sqlalchemy.orm import relationship
from scl_transport.database import Model, SurrogatePK
from sqlalchemy import and_
#from geoalchemy2 import Geometry

# agency_id,agency_name,agency_url,agency_timezone
# TS,Transantiago,http://www.transantiago.cl,America/Santiago
class Agency(SurrogatePK, Model):
    __tablename__ = 'agency'
    agency_id = Column(String, primary_key=True)
    agency_name = Column(String)
    agency_url = Column(String)
    agency_timezone = Column(String)

    def __repr__(self):
        return '<Agency({agency_id})>'.format(agency_id=self.agency_id)


# service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
# L_V33,1,1,1,1,1,0,0,20170704,20171231
# ISO 8601 weekday representation
DAYS_INDEX_MAP = {
    'monday': 1,
    'tuesday': 2,
    'wednesday': 3,
    'thursday': 4,
    'friday': 5,
    'saturday': 6,
    'sunday': 7,
}


class Service(SurrogatePK, Model):  # Calendar??
    __tablename__ = 'service'
    service_id = Column(String, primary_key=True)
    monday = Column(Boolean)
    tuesday = Column(Boolean)
    wednesday = Column(Boolean)
    thursday = Column(Boolean)
    friday = Column(Boolean)
    saturday = Column(Boolean)
    sunday = Column(Boolean)
    start_date = Column(Date)
    end_date = Column(Date)
    calendar_dates = relationship("CalendarDate")
    service_dates = relationship("ServiceDate")

    def __repr__(self):
        return '<Service({service_id})>'.format(service_id=self.service_id)

    def get_available_weekdays(self):  # TODO: oneliner
        idxs = []
        for day, day_idx in DAYS_INDEX_MAP.items():
            if getattr(self, day):
                idxs.append(day_idx)
        return idxs


class CalendarDate(SurrogatePK, Model):
    __tablename__ = 'calendar_date'
    _date = Column(Date)
    id = Column(Integer, primary_key=True)
    exception_type = Column(String)
    service_id = Column(String, ForeignKey('service.service_id'), nullable=True)
    service = relationship("Service")

# feed_publisher_name,feed_publisher_url,feed_lang,feed_start_date,feed_end_date,feed_version
#Transantiago,http://www.transantiago.cl,es,20170705,20171231,V33.20170807
class Feed(SurrogatePK, Model):
    __tablename__ = 'feed'
    id = Column(Integer, primary_key=True)
    feed_publisher_name = Column(String)
    feed_publisher_url = Column(String)
    feed_lang = Column(String)
    feed_start_date = Column(Date)
    feed_end_date = Column(Date)
    feed_version = Column(String)

    def __repr__(self):
        return '<Feed({feed_version})>'.format(feed_version=self.feed_version)


# route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_color,route_text_color
# 101,TS,101,Recoleta - Cerrillos,,3,,00D5FF,000000
class Route(SurrogatePK, Model):
    __tablename__ = 'route'
    route_id = Column(String, primary_key=True)
    agency_id = Column(String, ForeignKey('agency.agency_id'), nullable=True)
    agency = relationship("Agency")
    route_short_name = Column(String)
    route_long_name = Column(String)
    route_desc = Column(String)
    route_type = Column(String)
    route_url = Column(String)
    route_color = Column(String)
    route_text_color = Column(String)

    def __repr__(self):
        return '<Route({route_short_name})>'.format(route_short_name=self.route_short_name)


# shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence
# B31NI_V33,-33.4451920005,-70.6455860001,1
class Shape(SurrogatePK, Model):
    __tablename__ = 'shape'
    shape_id = Column(String, primary_key=True)
    shape_pt_sequence = Column(Integer)
    shape_pt_lat = Column(String)
    shape_pt_lon = Column(String)

    def __repr__(self):
        return '<Shape({shape_id})>'.format(shape_id=self.shape_id)


# route_id,service_id,trip_id,trip_headsign,direction_id,shape_id
# 101,L_V33,101-I-L_V33-B00,Cerrillos,0,101I_V33
class Trip(SurrogatePK, Model):
    __tablename__ = 'trip'
    trip_id = Column(String, primary_key=True)
    route_id = Column(String, ForeignKey('route.route_id'), nullable=True)
    route = relationship("Route")

    service_id = Column(String, ForeignKey('service.service_id'), nullable=True)
    service = relationship("Service")

    shape_id = Column(String, ForeignKey('shape.shape_id'), nullable=True)
    shape = relationship("Shape")

    trip_headsign = Column(String)
    direction_id = Column(String)
    frequency = relationship("Frequency", uselist=False)

    @property
    def stops(self):
        return self.object_session.query(Stop).join(StopTime).join(Trip).filter(
            Trip.trip_id == self.trip_id
        ).order_by(StopTime.stop_sequence)

    def __repr__(self):
        return '<Trip({trip_id})>'.format(trip_id=self.trip_id)


class ServiceDate(SurrogatePK, Model):
    __tablename__ = 'service_date'
    id = Column(Integer, primary_key=True)

    service_id = Column(String, ForeignKey('service.service_id'), nullable=True)
    service = relationship("Service")
    valid_date = Column(Date)

    @classmethod
    def _update_or_create(cls, session, defaults=None, **kwargs):
        query = session.query(cls).filter_by(**defaults)
        if not defaults:
            defaults = {}
        defaults.update(kwargs)
        if query.count() > 0:
            # TODO: handle multiple updates
            for entity in query:
                entity.update(session, **kwargs)
        else:
            cls.create(session, **defaults)

    def save(self, session, commit=True):
        session.add(self)
        if commit:
            session.commit()
        return self

    @classmethod
    def generate(cls, session, feed_id):
        feed = session.query(Feed).get(feed_id)

        from_date = arrow.get(feed.feed_start_date)
        to_date = arrow.get(feed.feed_end_date)

        for service in session.query(Service).all():
            weekday_to_generate = service.get_available_weekdays()

            for day in arrow.Arrow.range('day', from_date, to_date):
                weekday = day.isoweekday()
                if weekday not in weekday_to_generate:
                    continue

                defaults = {'valid_date': day.date(), 'service_id': service.service_id}
                service_date = ServiceDate(**defaults)
                session.add(service_date)
                session.commit()


# trip_id,start_time,end_time,headway_secs,exact_times
# 101-I-L_V33-B00,00:00:00,01:00:00,1200,0
class Frequency(SurrogatePK, Model):
    __tablename__ = 'frequency'
    id = Column(Integer, primary_key=True)
    trip_id = Column(String, ForeignKey('trip.trip_id'), nullable=True)
    trip = relationship("Trip")
    start_time = Column(Time)
    end_time = Column(Time)
    headway_secs = Column(Integer)
    exact_times = Column(Boolean)


# stop_id,stop_code,stop_name,stop_lat,stop_lon,stop_url
# PB1,PB1,PB1-Venezuela Esq. / Bolivia,-33.4045537555341,-70.623095148163,
class Stop(SurrogatePK, Model):
    __tablename__ = 'stop'
    stop_id = Column(String, primary_key=True)
    stop_code = Column(String)
    stop_name = Column(String)
    stop_lat = Column(String)
    stop_lon = Column(String)
    #stop_location = Column(Geometry('POINT'))
    stop_url = Column(String, nullable=True)

    def __repr__(self):
        return '<Stop({stop_code})>'.format(stop_code=self.stop_code)


# trip_id,arrival_time,departure_time,stop_id,stop_sequence
# 101-I-L_V33-B00,00:00:00,00:00:00,PB1,1
DUMMY_BASE_DATE = '2017/01/01'  # Temporal solution
class StopTime(SurrogatePK, Model):
    __tablename__ = 'stop_time'
    id = Column(Integer, primary_key=True)
    trip_id = Column(String, ForeignKey('trip.trip_id'), nullable=True)
    trip = relationship("Trip")
    arrival_time = Column(Time)
    departure_time = Column(Time)
    stop_id = Column(String, ForeignKey('stop.stop_id'), nullable=True)
    stop = relationship("Stop")
    stop_sequence = Column(Integer)

    def __repr__(self):
        return '<StopTime(Stop[{stop_id}] - Trip[{trip_id}])>'.format(
            stop_id=self.stop_id,
            trip_id=self.trip_id
        )


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
        return dt

    def _get_time_seconds(self, input_time):
        return datetime.timedelta(
            hours=input_time.hour,
            minutes=input_time.minute,
            seconds=input_time.second
        ).total_seconds()

    def _filter_on_frequency(self, now, query, route_id):
        results = []
        first = query.join(Frequency).filter(
            Trip.route_id == route_id,
            Frequency.start_time <= now.time(),
            Frequency.end_time >= now.time()
        ).order_by(Frequency.start_time)

        second = query.join(Frequency).filter(
            Trip.route_id == route_id,
            Frequency.start_time > now.time(),
        ).order_by(Frequency.start_time).order_by(Frequency.start_time)
        if first.count():
            results.append(first.first())
        if second.count():
            results.append(second.first())
        return results

    def _next_route_schedule(self, now, route_id, stop_time):
        if not stop_time:
            return []
        print stop_time.id
        print stop_time.trip.frequency.start_time
        print stop_time.trip.frequency.end_time
        arrival_time = stop_time.arrival_time
        arrival_seconds_offset = self._get_time_seconds(arrival_time)
        init_datetime = arrow.get(self._build_datetime(now.date(), stop_time.trip.frequency.start_time))
        end_datetime = arrow.get(self._build_datetime(now.date(), stop_time.trip.frequency.end_time))
        print init_datetime
        print end_datetime
        next_schedule = []
        #num = int((self._get_time_seconds(stop_time.trip.frequency.end_time) - self._get_time_seconds(stop_time.trip.frequency.start_time)) / stop_time.trip.frequency.headway_secs)
        for schedule in range(100):
            if len(next_schedule) > 5:
                break
            if init_datetime > end_datetime:
                print init_datetime, end_datetime
                break
            datetime_to_cast = init_datetime.replace(seconds=arrival_seconds_offset)
            print "datetime_to_cast", datetime_to_cast
            if datetime_to_cast >= now.datetime:
                next_schedule.append({
                    'route_id': stop_time.trip.route_id,
                    'stop_id': stop_time.stop_id,
                    'trip_id': stop_time.trip_id,
                    'arrival_at_timestamp': datetime_to_cast.timestamp,
                    'arrival_at_str': arrow.get(datetime_to_cast).format('YYYY/MM/DD HH:mm:ss'),
                    #'arrival_at_humanized': arrow.get(datetime_to_cast).humanize(locale='es')
                })
            init_datetime = arrow.get(init_datetime).replace(seconds=stop_time.trip.frequency.headway_secs)
        print "until", stop_time.trip.frequency.end_time
        return next_schedule

    def _populate_route_schedule(self, now, route_id, next_stop_times):
        next_schedule = []
        if not next_stop_times:
            return []
        while next_stop_times:
            stop_time = next_stop_times.pop(0)
            if len(next_schedule) > 5:
                break
            next_schedule.extend(self._next_route_schedule(now, route_id, stop_time))
        return next_schedule

    def _get_now(self):
        now = arrow.now('America/Santiago')
        n = arrow.get(now.naive)
        return n

    def to_dict(self, session):
        #now = arrow.now('America/Santiago')
        #now = arrow.now()
        now = self._get_now()
        stop_id = self.stop_id
        given_route_id = self.route_id

        # 1) filtrar los trips para route (route optional)
        print "1)",
        start_time = time.time()
        query = session.query(StopTime).filter(StopTime.stop_id == stop_id)
        print "--- %s seconds ---" % (time.time() - start_time)
        start_time = time.time()
        print "2)",
        # 2) filtrar solo Trips valid on date x -> sacar de ServiceDate [Corner case dia siguiente]
        # today or tomorrow[corner cases]
        if given_route_id:
            query = query.join(Trip).join(Service).join(ServiceDate).filter(
                Trip.route_id == given_route_id,
                and_(
                    ServiceDate.valid_date >= now.date(),
                    ServiceDate.valid_date <= now.replace(days=1).date()
                )
            ).order_by(ServiceDate.valid_date)
        else:
            query = query.join(Trip).join(Service).join(ServiceDate).filter(
                and_(
                    ServiceDate.valid_date >= now.date(),
                    ServiceDate.valid_date <= now.replace(days=1).date()
                )
            ).order_by(ServiceDate.valid_date)

        # 3) filtrar solo los que estan dentro de horario y/o siguiente? -> sacar de Frequency
        # Intentar completar X registros por route_id
        print "--- %s seconds ---" % (time.time() - start_time)
        start_time = time.time()
        print "3)",
        distinct_route_ids = []
        for stop_time in query:
            if stop_time.trip.route_id not in distinct_route_ids:
                distinct_route_ids.append(stop_time.trip.route_id)

        print "--- %s seconds ---" % (time.time() - start_time)
        start_time = time.time()
        print "4)",
        route_stop_time_map = {}
        for route_id in distinct_route_ids:
            if given_route_id and route_id != given_route_id:
                continue
            route_stop_time_map[route_id] = self._filter_on_frequency(now, query, route_id)
        print "--- %s seconds ---" % (time.time() - start_time)
        start_time = time.time()
        print "5)",
        # 4) extraer mas cercano mayor a now(), ejm: a cada 5 minutos (Frequency.headway_secs) en el 65min(StopTime.arrival_time) desde inicio ruta
        results = []
        for route_id, stop_times in route_stop_time_map.items():
            results.extend(self._populate_route_schedule(now, route_id, stop_times))
        results = sorted(results, key=lambda k: k['arrival_at_timestamp']) 
        print "--- %s seconds ---" % (time.time() - start_time)
        start_time = time.time()
        return results
