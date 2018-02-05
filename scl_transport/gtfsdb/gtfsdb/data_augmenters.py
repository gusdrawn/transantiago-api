from sqlalchemy.sql.expression import func

from .model.route_stop import RouteStop
from .model.trip import Trip
from .model.stop_time import StopTime


class RouteStopDirectionAugmenter(object):
    _data = None

    def __init__(self, session, stop_id):
        self.session = session
        self.stop_id = stop_id

    @property
    def data(self):
        if not self._data:
            self._data = {}
            q = self.session.query(RouteStop).filter(
                RouteStop.stop_id == self.stop_id
            ).distinct(RouteStop.route_id)
            for route_stop in q:
                route_id = route_stop.route_id
                self._data[route_id] = self.set_stop_route(route_id)
        return self._data

    def set_stop_route(self, route_id):
        from .route_stop import RouteStop
        q = self.session.query(RouteStop).filter(
            RouteStop.stop_id == self.stop_id,
            RouteStop.route_id == route_id
        )
        if q.count() == 1:
            return q.one().direction_id

        one_first_stop = self.session.query(RouteStop).filter(
            RouteStop.stop_id == self.stop_id,
            RouteStop.route_id == route_id,
            RouteStop.is_multi_direction == True,
            RouteStop.is_first_stop == True
        ).count() == 1
        one_non_first_stop = self.session.query(RouteStop).filter(
            RouteStop.stop_id == self.stop_id,
            RouteStop.route_id == route_id,
            RouteStop.is_multi_direction == True,
            RouteStop.is_first_stop == False
        ).count() == 1
        if one_first_stop and one_non_first_stop:
            return self.session.query(RouteStop).filter(
                RouteStop.stop_id == self.stop_id,
                RouteStop.route_id == route_id,
                RouteStop.is_multi_direction == True,
                RouteStop.is_first_stop == False
            ).first().direction_id

        return None


class RouteStopAugmenter(object):
    """
    Utility class to analyse RouteStop records identifying if this stop is terminal and/or initial for the given route
    """
    _terminal_count = None
    _always_terminal = None
    _is_terminal = None
    _route_trip_ids = None

    def __init__(self, session, route_stop):
        self.session = session
        self.stop_id = route_stop.stop_id
        self.route_id = route_stop.route_id
        self.direction_id = route_stop.direction_id

    def _get_route_trip_ids(self):
        if not self._route_trip_ids:
            trips = self.session.query(Trip).filter(
                Trip.route_id == self.route_id,
                Trip.direction_id == self.direction_id
            )
            self._route_trip_ids = [trip.trip_id for trip in trips]
        return self._route_trip_ids

    @property
    def _stop_times_for_route(self, filter_direction=True):
        return self.session.query(StopTime).filter(
            StopTime.stop_id == self.stop_id,
            StopTime.trip_id.in_(self._get_route_trip_ids())
        )

    def initial_count(self):
        return self.session.query(StopTime).filter(
            StopTime.stop_id == self.stop_id,
            StopTime.trip_id.in_(self._get_route_trip_ids()),
            StopTime.stop_sequence == 1
        ).count()

    def is_initial_stop(self):
        return self.initial_count() > 0

    def is_permanent_initial_stop(self):
        if not self.is_initial_stop():
            return False
        algo = self.session.query(StopTime).filter(
            StopTime.stop_id == self.stop_id,
            StopTime.trip_id.in_(self._get_route_trip_ids())
        ).count()
        return self.initial_count() == algo - self.terminal_count()

    def _calc_terminal_data(self):
        terminal_count = 0
        always_terminal = True
        is_terminal = False
        for record in self._stop_times_for_route:
            max_sequence = self.session.query(func.max(StopTime.stop_sequence)).filter(
                StopTime.trip_id == record.trip_id
            ).scalar()
            if max_sequence == record.stop_sequence:
                terminal_count += 1
                is_terminal = True
            elif record.stop_sequence != 1:
                always_terminal = False
        self._terminal_count = terminal_count
        self._is_terminal = is_terminal
        self._always_terminal = always_terminal

    def terminal_count(self):
        if not self._terminal_count:
            self._calc_terminal_data()
        return self._terminal_count

    def is_terminal_stop(self):
        if not self._is_terminal:
            self._calc_terminal_data()
        return self._is_terminal

    def is_permanent_terminal_stop(self):
        if not self._always_terminal:
            self._calc_terminal_data()
        if not self._is_terminal:
            return False
        return self._always_terminal

    def is_multi_direction(self):
        if self.session.query(RouteStop).filter(RouteStop.stop_id == self.stop_id, RouteStop.route_id == self.route_id).count() > 1:
            return True
        return False
