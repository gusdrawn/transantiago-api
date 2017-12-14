from sqlalchemy import Column
from geoalchemy2 import Geometry
from ..settings import config
from .base import Base
from sqlalchemy.types import Integer, String

import logging
log = logging.getLogger(__name__)


class BipSpot(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'bip_spot.csv'

    __tablename__ = 'bip_spot'
    __table_args__ = {'extend_existing': config.EXISTING_SCHEMA_FLAG}
    bip_spot_code = Column(String(255), nullable=False, primary_key=True)
    bip_spot_entity = Column(String(255), nullable=False)
    bip_spot_fantasy_name = Column(String(255), nullable=False)
    bip_spot_address = Column(String(255), nullable=True)
    bip_spot_commune = Column(String(255), nullable=True)
    bip_opening_time = Column(String(255), nullable=True)
    bip_spot_east_ref = Column(String(255), nullable=True)
    bip_spot_north_ref = Column(String(255), nullable=True)
    bip_spot_lon = Column(String(255), nullable=False)
    bip_spot_lat = Column(String(255), nullable=False)

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = Column(Geometry(geometry_type='POINT', srid=config.SRID))

    @classmethod
    def add_geom_to_dict(cls, row):
        args = (config.SRID, row['bip_spot_lon'], row['bip_spot_lat'])
        row['geom'] = 'SRID={0};POINT({1} {2})'.format(*args)

    @classmethod
    def get_fieldnames(cls, fieldnames):
        return [
            'bip_spot_code',
            'bip_spot_entity',
            'bip_spot_fantasy_name',
            'bip_spot_address',
            'bip_spot_commune',
            'bip_opening_time',
            'bip_spot_east_ref',
            'bip_spot_north_ref',
            'bip_spot_lon',
            'bip_spot_lat'
        ]
