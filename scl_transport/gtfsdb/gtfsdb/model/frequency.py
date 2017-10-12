from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Time

from .. import config
from .base import Base


class Frequency(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'frequencies.txt'

    __tablename__ = 'frequencies'
    __table_args__ = {'extend_existing': config.EXISTING_SCHEMA_FLAG}

    trip_id = Column(String(255), primary_key=True)
    start_time = Column(Time, primary_key=True)
    end_time = Column(Time)
    headway_secs = Column(Integer)
    exact_times = Column(Integer)

    trip = relationship(
        'Trip',
        primaryjoin='Frequency.trip_id==Trip.trip_id',
        foreign_keys='(Frequency.trip_id)',
        uselist=False, viewonly=True)
