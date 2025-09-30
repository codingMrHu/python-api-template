# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-17 10:31:24
# @Version: 1.0
# @License: H
# @Desc:

from typing import TYPE_CHECKING

from app.utils.logger import logger
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


class DatabaseService():
    name: str = 'database_service'

    def __init__(self, database_url: str):
        self.database_url = database_url

        self.engine = self._create_engine()

    def _create_engine(self) -> 'Engine':
        """Create the engine for the database."""
        if self.database_url and self.database_url.startswith('sqlite'):
            connect_args = {'check_same_thread': False}
        else:
            connect_args = {}
        return create_engine(self.database_url, connect_args=connect_args, pool_size=100, max_overflow=20, pool_pre_ping=True)

    def __enter__(self):
        self._session = Session(self.engine)
        return self._session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:  # If an exception has been raised
            logger.error(
                f'Session rollback because of exception: {exc_type.__name__} {exc_value}')
            self._session.rollback()
        else:
            self._session.commit()
        self._session.close()

    def get_session(self):
        with Session(self.engine) as session:
            yield session

    def create_db_and_tables(self):
        logger.debug(
            f'Creating database and tables --{len(SQLModel.metadata.sorted_tables)}')
        for table in SQLModel.metadata.sorted_tables:
            logger.debug(f'Creating table {table}')
            try:
                table.create(self.engine, checkfirst=True)
            except OperationalError as oe:
                logger.warning(
                    f'Table {table} already exists, skipping. Exception: {oe}')
            except Exception as exc:
                logger.error(f'Error creating table {table}: {exc}')
                raise RuntimeError(f'Error creating table {table}') from exc

        logger.debug('Database and tables created successfully')
