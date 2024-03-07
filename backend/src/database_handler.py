"""Made with the gracious help of the Novus (Discord API Wrapper) library"""

from typing import Any, TYPE_CHECKING

import asyncpg
from asyncpg.pool import PoolAcquireContext
import asyncio

from secrets_handler import SecretsHandler


class DatabaseHandler:

    pool: asyncpg.Pool | None = None

    @classmethod
    def acquire(cls, *args: Any, **kwargs: Any) -> PoolAcquireContext:
        """
        Retrives a connection to the Database pool. To use this connection:

        ```
        async with DatabaseHandler.acquire() as conn:
            await conn.execute(...)
        ```

        This will deal with connecting, executing the DB query (...), and
        closing the connection after it has been used.

        Parameters passed will be passed to asyncpg.Pool.acquire()
        """
        if not cls.pool:
            raise ValueError(
                "The DB pool was not pre-initialized. " +
                "Ensure an async call to `_initialize_pool` is being made."
            )

        return cls.pool.acquire(*args, **kwargs)

    @staticmethod
    async def initialize_pool() -> asyncpg.Pool:
        """
        Safely initializes the DB pool.

        If it exists, it will be returned. Otherwise, it will first be created.

        Returns
        -------
        asyncpy.Pool
            The found/created DB pool
        """
        return DatabaseHandler.pool or await DatabaseHandler._initialize_pool()

    @staticmethod
    async def _initialize_pool() -> asyncpg.Pool:
        """
        Initializes the DB pool. This involves a call to asyncpg's `create_pool`
        function.

        This will also set the DatabaseHandler.pool field

        Returns
        -------
        asyncpy.Pool
            The created DB pool
        """
        try:
            created = await asyncpg.create_pool(
                DatabaseHandler._get_database_dsn(),
                max_size=10,
                min_size=10
            )
            assert created

        except Exception as e:
            raise RuntimeError(
                f"Something went wrong creating the DB pool: " + str(e)
            )

        DatabaseHandler.pool = created
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
        return (
            "postgres://{}:{}@localhost:5432/{}"
        ).format(
            SecretsHandler.get_database_user(),
            SecretsHandler.get_database_password(),
            SecretsHandler.get_database_name()
        )

asyncio.run(DatabaseHandler.initialize_pool())