# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import datetime as dt
import os
import simplejson
from sqlalchemy import inspect as sqlalchemy_inspect

Base = declarative_base()

#
# database connection
#


class CombinedConnection(object):

    def __init__(self):
        # get DB URI
        self.db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
        if not self.db_uri:
            raise Exception("No DB URI specified!")

        self.engine = create_engine(
            self.db_uri,
            pool_size=0,
            max_overflow=-1,
            echo=False,
            json_serializer=simplejson.dumps,
            json_deserializer=simplejson.loads,
        )
        self.session_maker = sessionmaker(bind=self.engine)

    def create_db(self, base):
        base.metadata.create_all(bind=self.engine)

    def clear_tables(self, base, force=False):
        if 'amazonaws' in self.db_uri and not force:  # @@TODO: temporary solution
            raise Exception("forbidden action on Production DB")
        base.metadata.drop_all(bind=self.engine)
        base.metadata.create_all(bind=self.engine)

    def make_session(self):
        return self.session_maker(autoflush=False)

    def get_session(self):
        return self.make_session()

    def close(self):
        # close all sessions
        self.session_maker.close_all()

        # close connection pool
        self.engine.dispose()


class Adapter(object):

    def __init__(self, connection):
        self.connection = connection
        self.authenticate_without_secret = False

        # connect to database if not already
        if self.connection is None:
            self.connection = CombinedConnection()


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    @property
    def object_session(self):
        return sqlalchemy_inspect(self).session

    """
    @classmethod
    def update_or_create(cls, defaults=None, **kwargs):
        query = db.session.query(cls).filter_by(**defaults)
        if not defaults:
            defaults = {}
        defaults.update(kwargs)
        if query.count() > 0:
            # TODO: handle multiple updates
            for entity in query:
                entity.update(**kwargs)
        else:
            cls.create(**defaults)

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()
    """


class Model(CRUDMixin, Base):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True
    metadata = MetaData()


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)


"""
def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)
"""
