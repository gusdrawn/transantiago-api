import logging
import uuid
from geoalchemy2 import Geometry

from sqlalchemy import Column
from sqlalchemy.types import DateTime, Integer, String, Float

from .frequency import config
from .base import Base

log = logging.getLogger(__name__)

__all__ = ['Bus']


class Bus(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'bus.txt'  # TODO: remove this

    __tablename__ = 'bus'
    __table_args__ = ({'extend_existing': config.EXISTING_SCHEMA_FLAG})

    uuid = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    bus_plate_number = Column(String(15), index=True)
    direction_id = Column(Integer, nullable=True)
    bus_movement_orientation = Column(Integer, nullable=True)
    operator_number = Column(Integer, nullable=True)
    bus_speed = Column(Float, nullable=True)

    bus_lat = Column(String(100))
    bus_lon = Column(String(100))

    # route ids
    original_route_id = Column(String(50))
    console_route_id = Column(String(50))
    synoptic_route_id = Column(String(50))
    # dates
    captured_at = Column(DateTime, nullable=True)
    added_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, nullable=False, index=True)

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = Column(Geometry(geometry_type='POINT', srid=config.SRID))

    @classmethod
    def get_geom(cls, row):
        args = (config.SRID, row['bus_lon'], row['bus_lat'])
        return 'SRID={0};POINT({1} {2})'.format(*args)
