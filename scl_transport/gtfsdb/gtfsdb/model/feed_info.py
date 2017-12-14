from sqlalchemy import Column
from sqlalchemy.types import Date, String, DateTime

from ..settings import config
from .base import Base


class FeedInfo(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'feed_info.txt'

    __tablename__ = 'feed_info'
    __table_args__ = {'extend_existing': config.EXISTING_SCHEMA_FLAG}

    feed_publisher_name = Column(String(255), primary_key=True)
    feed_publisher_url = Column(String(255), nullable=False)
    feed_lang = Column(String(255), nullable=False)
    feed_start_date = Column(Date)
    feed_end_date = Column(Date)
    feed_version = Column(String(255))
    feed_license = Column(String(255))
    #
    feed_download_url = Column(String(255))
    feed_last_fetched_at = Column(DateTime, nullable=True, default=None)
