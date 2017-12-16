# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse

from .settings import config
from .model.base import Base
from .api import database_load
import arrow
from .util import printProgressBar


def gtfsdb_load():
    args, kwargs = get_args()
    database_load(args.file, **kwargs)


def get_args():
    """ database load command-line arg parser and help util...
    """
    tables = sorted([t.name for t in Base.metadata.sorted_tables])
    parser = argparse.ArgumentParser(
        prog='gtfsdb-load',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', help='URL or local path to GTFS zip FILE')
    parser.add_argument('--batch_size', '-b', default=config.DEFAULT_BATCH_SIZE,
                        help='BATCH SIZE to use for memory management')
    parser.add_argument('--database_url', '-d', default=config.DEFAULT_DATABASE_URL,
                        help='DATABASE URL with appropriate privileges')
    parser.add_argument('--is_geospatial', '-g', action='store_true',
                        default=config.DEFAULT_IS_GEOSPATIAL,
                        help='Database supports GEOSPATIAL functions')
    parser.add_argument('--schema', '-s', default=config.DEFAULT_SCHEMA,
                        help='Database SCHEMA name')
    parser.add_argument('--tables', choices=tables, default=None, nargs='*',
                        help='Limited list of TABLES to load, if blank, load all tables')
    parser.add_argument('--ignore_blocks', '-nb', default=False, action='store_true',
                        help="don't bother populating the derrived block table")
    args = parser.parse_args()

    kwargs = dict(
        batch_size=args.batch_size,
        schema=args.schema,
        is_geospatial=args.is_geospatial,
        tables=args.tables,
        url=args.database_url,
        ignore_blocks=args.ignore_blocks,
    )
    return args, kwargs


def route_stop_load():
    """ written as a test / debug method for RS table loader """
    from gtfsdb import Database, RouteStop
    kwargs = get_args()[1]
    db = Database(**kwargs)
    RouteStop.load(db, **kwargs)


def detect_non_existing_bus_routes():
    from . import Database, Bus, Route
    from sqlalchemy import func
    kwargs = {}
    db = Database(**kwargs)
    with_errors = []
    correct = []
    for bus in db.session.query(Bus).filter():
        if not db.session.query(Route).filter(func.upper(Route.route_id) == bus.original_route_id).count():
            with_errors.append(bus.original_route_id)
        else:
            correct.append(bus.original_route_id)
    with_errors = list(set(with_errors))
    correct = list(set(correct))
    from pprint import pprint
    pprint(with_errors)
    print("errors::", len(with_errors))
    print("correct::", len(correct))


def create_cached_routes():
    from . import Database, Stop
    kwargs = {}
    db = Database(**kwargs)
    stops = db.session.query(Stop).filter()
    total = stops.count()
    printProgressBar(0, total, prefix='Progress:', suffix='Complete', length=50)
    i = 0
    for stop in stops:
        _ = stop.stop_routes
        printProgressBar(i + 1, total, prefix='Progress:', suffix='Complete', length=50)
        i += 1


def populate_stop_directions():
    from . import Database, Stop
    kwargs = {}
    db = Database(**kwargs)
    stops = db.session.query(Stop).filter()
    total = stops.count()
    printProgressBar(0, total, prefix='Progress:', suffix='Complete', length=50)
    i = 0
    for stop in stops:
        agency_id = ''
        for stop_route in stop.stop_routes:
            if agency_id and stop_route['route']['agency_id'] != agency_id:
                print('error on stop {} - route {}'.format(stop.stop.id, stop_route['route']['route_id']))
            agency_id = stop_route['route']['agency_id']
        stop.agency_id = agency_id
        db.session.add(stop)
        db.session.commit()
        printProgressBar(i + 1, total, prefix='Progress:', suffix='Complete', length=50)
        i += 1


def check_multi_direction_routes():
    from . import Database, Stop, Trip, StopTime, StopDirection
    results = {}
    kwargs = {}
    db = Database(**kwargs)
    #StopDirection.__table__.create(bind=db.engine)
    stops = {}
    total = db.session.query(StopTime).count()
    printProgressBar(0, total, prefix='Progress:', suffix='Complete', length=50)
    i = 0
    for stop_time in db.session.query(StopTime).filter():
        stop_id = stop_time.stop_id
        if not stops.get(stop_id):
            stops[stop_id] = {}
        direction_id = stop_time.trip.direction_id
        trip_headsign = stop_time.trip.trip_headsign
        if not stops[stop_id].get(direction_id):
            stops[stop_id][direction_id] = trip_headsign
        printProgressBar(i + 1, total, prefix='Progress:', suffix='Complete', length=50)
        i += 1

    DIRECTION_MAP = {
        0: 'Outbound',
        1: 'Inbound'
    }

    stop_directions = []
    for stop_id, stop_content in stops.items():
        for direction_id, direction_headsign in stop_content.items():
            stop_directions.append(
                StopDirection(
                    stop_id=stop_id,
                    direction_id=int(direction_id),
                    direction_name=DIRECTION_MAP.get(int(direction_id)),
                    direction_headsign=direction_headsign
                )
            )

    db.session.bulk_save_objects(stop_directions)

    db.session.commit()


def get_agency_id_for_stop():
    from . import Database, Stop
    kwargs = {}
    db = Database(**kwargs)
    stops = {}
    for stop in db.session.query(Stop).filter():
        stop_id = stop.stop_id
        for route in stop.cached_routes:
            if not stops.get(stop_id):
                stops[stop_id] = []
            if route['agency_id'] not in stops[stop_id]:
                stops[stop_id].append(route['agency_id'])

    for stop_id, stop_agencies in stops.items():
        if len(stop_agencies) > 1:
            raise Exception("multiple agencies for stop")

    for stop_id, stop_agencies in stops.items():
        if stop_agencies:
            agency_id = stop_agencies[0]
            db.session.query(Stop).filter(Stop.stop_id == stop_id).update({"agency_id": (agency_id)})
    db.session.commit()


def bip_spot_load(directory):
    from . import Database, BipSpot
    kwargs = {'gtfs_directory': directory, 'is_geospatial': True}
    db = Database(**kwargs)
    BipSpot.add_geometry_column()
    BipSpot.__table__.create(bind=db.engine)
    BipSpot.load(db, **kwargs)


def review_content():
    from . import Database, RouteDirection
    kwargs = {'is_geospatial': True}
    db = Database(**kwargs)
    RouteDirection.populate(db.session)


def _build_dt(input_time):
    input_date = arrow.now().date()
    dt = arrow.get(input_date)
    dt = dt.replace(hour=input_time.hour)
    dt = dt.replace(minute=input_time.minute)
    dt = dt.replace(second=input_time.second)
    return arrow.get(dt)


def _intersection(trip_1, trip_2):
    start_trip_1 = _build_dt(trip_1.frequency.start_time)
    end_trip_1 = _build_dt(trip_1.frequency.end_time)
    start_trip_2 = _build_dt(trip_2.frequency.start_time)
    end_trip_2 = _build_dt(trip_2.frequency.end_time)
    if end_trip_2 >= start_trip_1 and end_trip_2 <= end_trip_1:
        return True
    if start_trip_2 <= end_trip_1 and start_trip_2 >= start_trip_1:
        True
    return False


def multi_direction_analysis():
    from . import Database, Trip
    kwargs = {'is_geospatial': False}
    db = Database(**kwargs)
    route_id = '101'
    trips = db.session.query(Trip).filter(Trip.route_id == route_id).order_by(Trip.service_id)
    copy_trips = trips
    for trip in trips:
        for copy_trip in copy_trips:
            if trip.trip_id == copy_trip.trip_id:
                continue
            if trip.service_id != copy_trip.service_id:
                continue
            if trip.direction_id == copy_trip.direction_id:
                continue
            if _intersection(copy_trip, trip) and trip.direction_id != copy_trip.direction_id:
                print("#" * 50)
                print(copy_trip.trip_id, copy_trip.service_id, copy_trip.direction_id, copy_trip.frequency.start_time, copy_trip.frequency.end_time)
                print(trip.trip_id, copy_trip.service_id, trip.direction_id, trip.frequency.start_time, trip.frequency.end_time)


def db_connect_tester():
    """ simple routine to connect to an existing database and list a few stops
        bin/connect-tester --database_url sqlite:///gtfs.db _no_gtfs_zip_needed_
    """
    from gtfsdb import Database, Stop, Route, StopTime
    args, kwargs = get_args()
    db = Database(**kwargs)
    for s in db.session.query(Stop).limit(2):
        print(s.stop_name)
    for r in db.session.query(Route).limit(2):
        print(r.route_name)
    #import pdb; pdb.set_trace()
    stop_times = StopTime.get_departure_schedule(db.session, stop_id='11411')
    for st in stop_times:
        print(st.get_direction_name())
        break
