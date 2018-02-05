from .util import printProgressBar
from .data_augmenters import (
    RouteStopAugmenter,
    RouteStopDirectionAugmenter
)

from gtfsdb import (
    StopTime,
    StopDirection,
    RouteStop,
    Stop
)


def run_post_process(session):
    # populate stop directions
    populate_stop_directions(session)
    # mark initial/terminal stop_routes
    flag_initial_terminal_stop_routes(session)
    # populate stop sessions
    populate_stop_routes(session)
    # populate stop agency ids
    populate_stop_agency_id(session)
    # mark multidirectional stops
    flag_multi_directional_stops(session)
    # popuplate stop route directions
    populate_stop_route_directions(session)


def populate_stop_directions(session):
    stops = {}
    total = session.query(StopTime).count()
    printProgressBar(0, total, prefix='Generating stop directions:', suffix='Complete', length=50)
    i = 0
    for stop_time in session.query(StopTime).filter():
        stop_id = stop_time.stop_id
        if not stops.get(stop_id):
            stops[stop_id] = {}
        direction_id = stop_time.trip.direction_id
        trip_headsign = stop_time.trip.trip_headsign
        if not stops[stop_id].get(direction_id):
            stops[stop_id][direction_id] = trip_headsign
        printProgressBar(i + 1, total, prefix='Generating stop directions:', suffix='Complete', length=50)
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

    session.bulk_save_objects(stop_directions)
    session.commit()


def populate_stop_routes(session):
    """
    Pre-caching stop routes
    """
    stops = session.query(Stop).filter()
    total = stops.count()
    printProgressBar(0, total, prefix='Generating stop routes:', suffix='Complete', length=50)
    i = 0
    for stop in stops:
        _ = stop.stop_routes
        printProgressBar(i + 1, total, prefix='Generating stop routes:', suffix='Complete', length=50)
        i += 1


def populate_stop_agency_id(session):
    stops = {}
    for stop in session.query(Stop).filter():
        stop_id = stop.stop_id
        for stop_route in stop.stop_routes:
            if not stops.get(stop_id):
                stops[stop_id] = []
            if stop_route['route']['agency_id'] not in stops[stop_id]:
                stops[stop_id].append(stop_route['route']['agency_id'])

    for stop_id, stop_agencies in stops.items():
        if len(stop_agencies) > 1:
            raise Exception("multiple agencies for stop")

    total = len(stops.keys())
    i = 0
    printProgressBar(0, total, prefix='Generating stop agency_id:', suffix='Complete', length=50)
    for stop_id, stop_agencies in stops.items():
        if stop_agencies:
            agency_id = stop_agencies[0]
            session.query(Stop).filter(Stop.stop_id == stop_id).update({"agency_id": (agency_id)})
            printProgressBar(i + 1, total, prefix='Generating stop agency_id:', suffix='Complete', length=50)
            i += 1
    session.commit()


def flag_multi_directional_stops(session):
    total = session.query(Stop).filter().count()
    printProgressBar(0, total, prefix='Marking multi-directional stops:', suffix='Complete', length=50)
    i = 0
    for stop in session.query(Stop).filter():
        printProgressBar(
            i + 1,
            total,
            prefix='Marking multi-directional stops:',
            suffix='Complete',
            length=50
        )
        if stop.is_multi_directional(session):
            stop.multi_directional = True
        else:
            stop.multi_directional = False
        session.add(stop)
        i += 1
    session.commit()


def populate_stop_route_directions(session):
    total = session.query(Stop).filter().count()
    printProgressBar(0, total, prefix='Populating stop route directions:', suffix='Complete', length=50)
    i = 0
    for stop in session.query(Stop).filter():
        printProgressBar(
            i + 1,
            total,
            prefix='Populating route stops terminals:',
            suffix='Complete',
            length=50
        )
        r = RouteStopDirectionAugmenter(session=session, stop_id=stop.stop_id)

        stop.route_directions = r.data
        session.add(stop)
        i += 1
    session.commit()


def flag_initial_terminal_stop_routes(session):
    total = session.query(RouteStop).filter().count()
    printProgressBar(0, total, prefix='Populating route stops terminals:', suffix='Complete', length=50)
    i = 0
    for route_stop in session.query(RouteStop).filter():
        printProgressBar(
            i + 1,
            total,
            prefix='Populating route stops terminals:',
            suffix='Complete',
            length=50
        )
        route_stop_augmenter = RouteStopAugmenter(session=session, route_stop=route_stop)
        route_stop.is_first_stop = route_stop_augmenter.is_initial_stop()
        route_stop.is_last_stop = route_stop_augmenter.is_terminal_stop()
        route_stop.is_multi_direction = route_stop_augmenter.is_multi_direction()

        # internal flags
        route_stop.is_permanent_first_stop = route_stop_augmenter.is_permanent_initial_stop()
        route_stop.is_permanent_last_stop = route_stop_augmenter.is_permanent_terminal_stop()
        session.add(route_stop)
        i += 1

    session.commit()
