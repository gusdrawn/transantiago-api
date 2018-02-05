from scl_transport.gtfsdb.gtfsdb import (
    Stop,
    Bus
)

from scl_transport.gtfsdb.gtfsdb.schemas import (
    StopArrivalSchema_v1,
    # v2
    StopArrivalSchema_v2
)


class NextArrival(object):
    _direction_id = None

    def __init__(self, data):
        self.data = data

    @property
    def is_live(self):
        return True

    @property
    def route_id(self):
        return self.data['route_id']

    @property
    def bus_distance(self):
        return self.data['bus_distance']

    @property
    def bus_plate_number(self):
        return self.data['bus_plate_number']

    @property
    def arrival_estimation(self):
        return self.data['route_arrival_prediction'] or self.data['message']

    @property
    def calculated_at(self):
        return self.data['calculated_at']

    @property
    def direction_id(self):
        return self._direction_id

    @direction_id.setter
    def direction_id(self, value):
        self._direction_id = value


class NextArrivalsSerializer_v1(object):
    def __init__(self, session, stop_id):
        self.session = session
        self.stop_id = stop_id

    @property
    def schema(self):
        return StopArrivalSchema_v1

    def get_items(self, items):
        return self.schema().dump(items, many=True).data


class NextArrivalsSerializer_v2(object):
    def __init__(self, session, stop_id):
        self.session = session
        self.stop_id = stop_id

    @property
    def schema(self):
        return StopArrivalSchema_v2

    def get_items(self, items):
        # augment with direction_id
        stop = self.session.query(Stop).filter(Stop.stop_id == self.stop_id.upper()).first()
        if not stop:
            return self.schema().dump(items, many=True).data
        route_directions = stop.route_directions
        for item in items:
            if route_directions.get(item.route_id):
                item.direction_id = route_directions.get(item.route_id)
            elif item.bus_plate_number:
                bus = self.session.query(Bus).filter(
                    Bus.bus_plate_number == item.bus_plate_number
                )
                if bus.count():
                    try:
                        item.direction_id = bus.first().direction_id
                    except Exception:
                        pass
        return self.schema().dump(items, many=True).data


serializer = {
    1: NextArrivalsSerializer_v1,
    2: NextArrivalsSerializer_v2
}


class NextArrivals(object):
    def __init__(self, session, data, stop_id, version=1):
        self.data = data
        self.items = []
        self.stop_id = stop_id
        self.session = session
        self.version = version

    def get_serializer_class(self):
        return serializer.get(self.version)

    def get(self):
        self.items = []
        # 1: augment live data
        for live_arrival in self.data['routes']:
            if live_arrival['code'] in ('00', '01', '9', '09', '10', '11', '12'):  # live data
                next_arrival = NextArrival(live_arrival)
                self.items.append(next_arrival)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(self.session, self.stop_id)
        return serializer.get_items(self.items)
