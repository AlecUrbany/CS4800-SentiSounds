"""A handler for interacting with the PostgreSQL Database asynchronously"""
from __future__ import annotations
from typing import Any

import asyncpg
from secrets_handler import SecretsHandler


class PoolAcquireContext:
    """
    A class to show Python that our asyncpg pool can be used in an asynchronous
    context to obtain a connection from the pool.
    """

    async def __aenter__(self) -> asyncpg.Connection:
        """Defines an asynchronous context-based entrance to the pool"""
        ...

    async def __aexit__(self, *_: Any) -> None:
        """Defines an asynchronous context-based exit from the pool"""
        ...


class DatabaseHandler:
    """
    A static class that deals with Database maintenence. When a DB operation
    is requested by any point of the application, it must first call the
    `get_pool()` function. On first run, this will ensure that a DB pool and
    the necessary tables (defined in the DATABASE_FILE) have been created.

    This pool allows for a set of connections to the DB to be created. They
    will also be context-managed via an asynchronous context (async with)
    """

    DATABASE_FILE: str = "database.pgsql"
    """A file containing an SQL query to execute on pool creation"""

    SETUP_QUERY: str = ""
    """The query extracted from the database file"""

    pool: asyncpg.Pool | None = None
    """A pool of DB connections"""

    @classmethod
    def acquire(cls, *args: Any, **kwargs: Any) -> PoolAcquireContext:
        """
        Retrives a connection to the Database pool. To use this connection:

        >>> async with DatabaseHandler.acquire() as conn:
        >>>    await conn.execute(...)

        This will deal with connecting, executing the DB query (...), and
        closing the connection after it has been used.

        Parameters passed will be passed to asyncpg.Pool.acquire()
        """
        if not cls.pool:
            raise ValueError(
                "The DB pool was not pre-initialized. "
                + "Ensure an async call to `_initialize_pool` is being made."
            )

        return cls.pool.acquire(*args, **kwargs)  # type: ignore

    @staticmethod
    async def get_pool() -> asyncpg.Pool:
        """
        Safely initializes the DB pool.

        If it exists, it will be returned. Otherwise, it will first be created.

        Returns
        -------
        asyncpg.Pool
            The found/created DB pool
        """
        return DatabaseHandler.pool or await DatabaseHandler._initialize_pool()

    @staticmethod
    async def _initialize_pool() -> asyncpg.Pool:
        """
        Initializes the DB pool. This involves an asyncpg ``create_pool`` call.

        This will also set the DatabaseHandler.pool field

        Returns
        -------
        asyncpg.Pool
            The created DB pool
        """
        try:
            created = await asyncpg.create_pool(
                DatabaseHandler._get_database_dsn()
            )
            assert created
            DatabaseHandler.pool = created

            await DatabaseHandler._create_tables()

        except Exception as e:
            raise RuntimeError(
                "Something went wrong creating the DB pool: " + str(e)
            )

        return created

    @staticmethod
    def _get_database_dsn() -> str:
        """
        Retrieves the database DSN based on the
        username, password, and database name found in the secrets file.

        Returns
        -------
        str
            The database DSN
        """
        return ("postgres://{}:{}@{}:{}/{}").format(
            SecretsHandler.get_database_user(),
            SecretsHandler.get_database_password(),
            SecretsHandler.get_database_host(),
            SecretsHandler.get_database_port(),
            SecretsHandler.get_database_name(),
        )

    @staticmethod
    async def _create_tables() -> None:
        """
        Sets up the database with whatever is in the DATABASE_FILE.
        Generally, this will consist of table and extention creations.

        Raises
        ------
        RuntimeError
            If something goes wrong during the creation process
        """
        if not DatabaseHandler.SETUP_QUERY:
            with open(DatabaseHandler.DATABASE_FILE, "r") as file:
                DatabaseHandler.SETUP_QUERY = file.read()

        try:
            async with DatabaseHandler.acquire() as conn:
                await conn.execute(DatabaseHandler.SETUP_QUERY)
        except Exception as e:
            raise RuntimeError(
                "Something went wrong creating the DB tables: " + str(e)
            )
