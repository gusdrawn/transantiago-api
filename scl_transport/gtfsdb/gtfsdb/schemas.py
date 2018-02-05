from marshmallow import Schema, fields

"""
Constants
"""


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


"""
@@TODO: create a file by schema_version
"""

"""
Schemas v1
"""


class AgencySchema_v1(Schema):
    agency_id = fields.Str()
    agency_name = fields.Str()
    agency_url = fields.Str()


class ShapeSchema_v1(Schema):
    shape_id = fields.Str()
    shape_pt_lat = fields.Str()
    shape_pt_lon = fields.Str()
    shape_pt_sequence = fields.Int()


class DirectionSchema_v1(Schema):
    route_id = fields.Str()
    direction_id = fields.Int()
    direction_name = fields.Str()
    direction_headsign = fields.Str()


class RouteSchema_v1(Schema):
    route_id = fields.Str()
    agency_id = fields.Str()
    route_short_name = fields.Str()
    route_long_name = fields.Str()
    route_desc = fields.Str()
    route_type = fields.Str()
    route_url = fields.Str()
    route_color = fields.Str()
    route_text_color = fields.Str()
    # extra fields
    start_date = fields.Date()
    end_date = fields.Date()
    directions = fields.List(fields.Nested(DirectionSchema_v1))


class StopSchema_v1(Schema):
    stop_id = fields.Str()
    stop_code = fields.Str()
    stop_name = fields.Str()
    stop_lat = fields.Str()
    stop_lon = fields.Str()
    agency_id = fields.Str()


class ServiceSchema_v1(Schema):
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


class FrequencySchema_v1(Schema):
    start_time = fields.Time()
    end_time = fields.Time()
    headway_secs = fields.Integer()
    exact_times = fields.Boolean()


class TripSchema_v1(Schema):
    trip_id = fields.Str()
    service_id = fields.Str()
    route_id = fields.Str()
    direction_id = fields.Str()
    trip_headsign = fields.Str()
    trip_short_name = fields.Str()
    frequency = fields.Nested(FrequencySchema_v1)
    trip_len = fields.Integer()
    trip_headsign = fields.Str()
    start_time = fields.Time()
    end_time = fields.Time()


class StopArrivalSchema_v1(Schema):
    calculated_at = fields.Str()
    arrival_estimation = fields.Str()
    bus_plate_number = fields.Str()
    bus_distance = fields.Str()
    route_id = fields.Str()
    is_live = fields.Boolean()


class StopArrivalSchema_v2(StopArrivalSchema_v1):
    direction_id = fields.Integer()


class StopTimeSchema_v1(Schema):
    stop = fields.Nested(StopSchema_v1)
    trip = fields.Nested(TripSchema_v1)
    arrival_time = fields.Time()
    departure_time = fields.Time()
    stop_sequence = fields.Integer()
    stop_headsign = fields.Str()


class FeedSchema_v1(Schema):
    feed_publisher_name = fields.Str()
    feed_publisher_url = fields.Str()
    feed_lang = fields.Str()
    feed_start_date = fields.Date()
    feed_end_date = fields.Date()
    feed_version = fields.Str()


class BipSpotSchema_v1(Schema):
    bip_spot_code = fields.Str()
    bip_spot_entity = fields.Str()
    bip_spot_fantasy_name = fields.Str()
    bip_spot_address = fields.Str()
    bip_spot_commune = fields.Str()
    bip_opening_time = fields.Str()
    bip_spot_lon = fields.Str()
    bip_spot_lat = fields.Str()


class BusSchema_v1(Schema):
    bus_plate_number = fields.Str()
    direction_id = fields.Integer()
    bus_movement_orientation = fields.Integer()
    operator_number = fields.Integer()
    bus_speed = fields.Float()
    bus_lat = fields.Str()
    bus_lon = fields.Str()
    original_route_id = fields.Str(dump_to='route_id')
    # dates
    captured_at = fields.DateTime(format=DATETIME_FORMAT)
    added_at = fields.DateTime(format=DATETIME_FORMAT)


class DetailedDirectionSchema_v1(DirectionSchema_v1):
    active_shape = fields.List(fields.Nested(ShapeSchema_v1), load_from='active_shape', dump_to='shape')
    active_stop_times = fields.List(
        fields.Nested(StopTimeSchema_v1),
        load_from='active_stop_times',
        dump_to='stop_times'
    )
    is_active = fields.Boolean()


class StopRouteSchema_v1(Schema):
    route = fields.Nested(RouteSchema_v1)
    direction = fields.Nested(DirectionSchema_v1)


class StopWithStopRoutesSchema_v1(StopSchema_v1):
    stop_routes_old = fields.Raw(dump_to='routes')


"""
Schemas v2
"""


class StopWithStopRoutesSchema_v2(StopSchema_v1):
    stop_routes = fields.Raw(dump_to='routes')


class StopRouteSchema_v2(Schema):
    route = fields.Nested(RouteSchema_v1)
    direction = fields.Nested(DirectionSchema_v1)
    is_first_stop = fields.Boolean()
    is_last_stop = fields.Boolean()


class StopTimeSchema_v2(Schema):
    stop_id = fields.Str()
    trip_id = fields.Str()
    arrival_time = fields.Time()
    departure_time = fields.Time()
    stop_sequence = fields.Integer()
