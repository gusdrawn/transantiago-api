import math


class BoundingBox(object):
    def __init__(self, bbox=None):
        self.lat_min = None
        self.lon_min = None
        self.lat_max = None
        self.lon_max = None

        if bbox:
            if isinstance(bbox, list):
                self.lon_min, self.lat_min, self.lon_max, self.lat_max = bbox
            elif isinstance(bbox, basestring):
                self.lon_min, self.lat_min, self.lon_max, self.lat_max = bbox.split(",")

    def to_polygon_text(self):
        if not all([self.lat_min, self.lon_min, self.lat_max, self.lon_max]):
            return None

        return 'POLYGON(({lon_min} {lat_min},{lon_min} {lat_max},{lon_max} {lat_max},{lon_max} {lat_min},{lon_min} {lat_min}))'.format(
            lon_min=self.lon_min,
            lat_min=self.lat_min,
            lat_max=self.lat_max,
            lon_max=self.lon_max
        )


def get_bounding_box(latitude_in_degrees, longitude_in_degrees, half_side_in_km=1.0):
    """
    assert half_side_in_km > 0
    assert latitude_in_degrees >= -90.0 and latitude_in_degrees  <= 90.0
    assert longitude_in_degrees >= -180.0 and longitude_in_degrees <= 180.0
    """
    lat = math.radians(float(latitude_in_degrees))
    lon = math.radians(float(longitude_in_degrees))
    radius = 6359.103
    # Radius of the parallel at given latitude
    parallel_radius = radius * math.cos(lat)
    lat_min = lat - half_side_in_km / radius
    lat_max = lat + half_side_in_km / radius
    lon_min = lon - half_side_in_km / parallel_radius
    lon_max = lon + half_side_in_km / parallel_radius
    rad2deg = math.degrees

    box = BoundingBox()
    box.lat_min = rad2deg(lat_min)
    box.lon_min = rad2deg(lon_min)
    box.lat_max = rad2deg(lat_max)
    box.lon_max = rad2deg(lon_max)
    return (box)
