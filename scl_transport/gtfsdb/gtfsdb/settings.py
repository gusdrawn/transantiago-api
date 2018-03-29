import logging
from ConfigParser import ConfigParser
import logging.config
import os


class Config(object):
    '''Application defaults'''
    DEFAULT_BATCH_SIZE = 10000
    DEFAULT_SCHEMA = None
    EXISTING_SCHEMA_FLAG = True

    '''Data source constants'''
    DATASOURCE_GTFS = 1
    DATASOURCE_LOOKUP = 2
    DATASOURCE_DERIVED = 3

    '''Geometry constants'''
    SRID = 4326

    '''Order list of class names, used for creating & populating tables'''
    SORTED_CLASS_NAMES = [
        'Bus',
        'RouteType',
        'RouteFilter',
        'FeedInfo',
        'Agency',
        'Block',
        'Calendar',
        'CalendarDate',
        'Route',
        'Stop',
        'StopFeature',
        'Transfer',
        'Shape',
        'Pattern',
        'Trip',
        'StopTime',
        'RouteStop',
        'RouteDirection',
        'Frequency',
        'FareAttribute',
        'FareRule',
        'UniversalCalendar',
        'StopDirection'
    ]


class LocalConfig(Config):
    DEFAULT_DATABASE_URL = 'postgresql://postgres:@localhost/scltransit'
    DEFAULT_IS_GEOSPATIAL = True


class ProductionConfig(Config):
    DEFAULT_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URI')
    DEFAULT_IS_GEOSPATIAL = True


class TestConfig(Config):
    DEFAULT_DATABASE_URL = 'postgresql://postgres:@localhost/testing'
    DEFAULT_IS_GEOSPATIAL = False


def get_config():
    env = os.getenv('ENVIRONMENT', 'test')
    if env == 'dev':
        return LocalConfig()
    elif env == 'test':
        return TestConfig()
    elif env == 'prod':
        return ProductionConfig()
    raise Exception("Invalid environment name")


config = get_config()
