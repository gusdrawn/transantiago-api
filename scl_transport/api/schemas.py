from marshmallow import Schema, fields

"""
Schemas
"""


class AgencySchema(Schema):
    agency_id = fields.Str()
    agency_name = fields.Str()
    agency_url = fields.Str()


class ShapeSchema(Schema):
    shape_id = fields.Str()
    shape_pt_lat = fields.Str()
    shape_pt_lon = fields.Str()
    shape_pt_sequence = fields.Int()


class DirectionSchema(Schema):
    route_id = fields.Str()
    direction_id = fields.Int()
    direction_name = fields.Str()
    direction_headsign = fields.Str()


class RouteSchema(Schema):
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
    directions = fields.List(fields.Nested(DirectionSchema))


class StopSchema(Schema):
    stop_id = fields.Str()
    stop_code = fields.Str()
    stop_name = fields.Str()
    stop_lat = fields.Str()
    stop_lon = fields.Str()
    agency_id = fields.Str()
    #directions = fields.List(fields.Nested(DirectionSchema))


# @@TODO: fix this, class explosion!
class StopWithStopRoutesSchema(StopSchema):
    stop_routes = fields.Raw(dump_to='routes')


class ServiceSchema(Schema):
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


class FrequencySchema(Schema):
    start_time = fields.Time()
    end_time = fields.Time()
    headway_secs = fields.Integer()
    exact_times = fields.Boolean()


class TripSchema(Schema):
    trip_id = fields.Str()
    service_id = fields.Str()
    route_id = fields.Str()
    direction_id = fields.Str()
    trip_headsign = fields.Str()
    trip_short_name = fields.Str()
    frequency = fields.Nested(FrequencySchema)
    trip_len = fields.Integer()
    trip_headsign = fields.Str()
    start_time = fields.Time()
    end_time = fields.Time()


class StopTimeSchema(Schema):
    stop = fields.Nested(StopSchema)
    trip = fields.Nested(TripSchema)
    arrival_time = fields.Time()
    departure_time = fields.Time()
    stop_sequence = fields.Integer()
    stop_headsign = fields.Str()


class FeedSchema(Schema):
    feed_publisher_name = fields.Str()
    feed_publisher_url = fields.Str()
    feed_lang = fields.Str()
    feed_start_date = fields.Date()
    feed_end_date = fields.Date()
    feed_version = fields.Str()


class BipSpotSchema(Schema):
    bip_spot_code = fields.Str()
    bip_spot_entity = fields.Str()
    bip_spot_fantasy_name = fields.Str()
    bip_spot_address = fields.Str()
    bip_spot_commune = fields.Str()
    bip_opening_time = fields.Str()
    bip_spot_lon = fields.Str()
    bip_spot_lat = fields.Str()


class BusSchema(Schema):
    bus_plate_number = fields.Str()
    direction_id = fields.Integer()
    bus_movement_orientation = fields.Integer()
    operator_number = fields.Integer()
    bus_speed = fields.Float()
    bus_lat = fields.Str()
    bus_lon = fields.Str()
    original_route_id = fields.Str(dump_to='route_id')
    # dates
    captured_at = fields.DateTime()
    added_at = fields.DateTime()


class DetailedDirectionSchema(DirectionSchema):
    active_shape = fields.List(fields.Nested(ShapeSchema), load_from='active_shape', dump_to='shape')
    active_stop_times = fields.List(fields.Nested(StopTimeSchema), load_from='active_stop_times', dump_to='stop_times')
    is_active = fields.Boolean()


class StopRouteSchema(Schema):
    route = fields.Nested(RouteSchema)
    direction = fields.Nested(DirectionSchema)


class StopTimeSchema_v2(Schema):
    stop_id = fields.Str()
    trip_id = fields.Str()
    arrival_time = fields.Time()
    departure_time = fields.Time()
    stop_sequence = fields.Integer()



