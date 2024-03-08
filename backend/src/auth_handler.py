import re

from database_handler import DatabaseHandler

class AuthHandler:

    EMAIL_REGEX = re.compile(
        r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", flags=re.IGNORECASE
    )
    PASSWORD_REGEX = re.compile(
        r".+"
    )

    @staticmethod
    def valid_password(password: str) -> bool:
        """
        Given a password string, return if it's valid

        This does not check for the *existence* of the address, rather it simply
        checks against an password pattern

        Parameters
        ----------
        password: str
            The password to check

        Returns
        -------
        bool
            Whether or not the address is valid
        """
        return bool(AuthHandler.PASSWORD_REGEX.match(password))

    @staticmethod
    def valid_email(email_address: str) -> bool:
        """
        Given an email address string, return if it's valid

        This does not check for the *existence* of the address, rather it simply
        checks against an email address pattern

        Parameters
        ----------
        email_address: str
            The email address to check

        Returns
        -------
        bool
            Whether or not the address is valid
        """
        return bool(AuthHandler.EMAIL_REGEX.match(email_address))

    @staticmethod
    async def sign_up(
                email_address: str,
                password: str,
                first_name: str,
                last_initial: str = ""
            ) -> bool:
        """
        Adds a new user to the database's user_auth store

        Parameters
        ----------
        email_address: str
            The email address of the user. Must pass validity via `valid_email`
        password: str
            The password of the user. Must pass validity via `valid_password`
        first_name: str
            The user's first name. Must be <= 29 characters (32 - 3)
        last_initial: str = ""
            The user's last initial

        Returns
        -------
        bool
            Whether or not the user was successfully added. Generally, this
            would mean the user was not already present in the DB

        Raises
        ------
        ValueError
            If an invalid email address, password, or name is provided
        """

        if len(first_name) > 29:
            raise ValueError("The first name entered was too long.")

        if len(last_initial) > 1:
            raise ValueError("The last name entered was too long.")

        display_name = first_name + (
            f" {last_initial}." if last_initial else ""
        )

        if not AuthHandler.valid_email(email_address):
            raise ValueError("An invalid email address was entered.")

        if not AuthHandler.valid_password(password):
            raise ValueError("An invalid password was entered.")

        async with DatabaseHandler.acquire() as conn:
            try:
                await conn.execute(
                    """
                    INSERT INTO
                        user_auth
                        (
                            email_address,
                            hashed_password,
                            display_name
                        )
                    VALUES
                        (
                            $1,
                            crypt($2, gen_salt('bf')),
                            $3
                        )
                    """,
                    email_address, password, display_name
                )
            except:
                return False

        return True

    @staticmethod
    async def log_in(
                email_address: str,
                password: str
            ) -> bool:
        """
        Attempts to log-in given a user's credentials

        Parameters
        ----------
        email_address: str
            The email address associated with the target user
        password: str
            The password to validate against

        Returns
        -------
        bool
            Whether or not the log-in was successful
        """
        async with DatabaseHandler.acquire() as conn:
            found = await conn.fetch(
                """
                SELECT
                    1
                FROM
                    user_auth
                WHERE
                    email_address = $1
                AND
                    hashed_password = crypt($2, hashed_password)
                """,
                email_address, password
            )

        return bool(found)

    # TODO: Spotify Authentication
    # TODO: Email Validation (send them an email, wait for them to enter the code)