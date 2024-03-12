import re
import smtplib
import ssl
import random

from database_handler import DatabaseHandler
from secrets_handler import SecretsHandler

class AuthHandler:

    # Regex to maintain secure and valid emails and passwords
    EMAIL_REGEX = re.compile(
        r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", flags=re.IGNORECASE
    )
    PASSWORD_REGEX = re.compile(
        r".+"
    )

    # The authentication email to send users
    PLAIN_TEXT = (
        "Subject: {}\n\n{}"
    )

    # A dictionary of currently authenticating users
    # email_address: (code, expiry time)
    ACTIVE_AUTHS: dict[str, tuple[int, int]] = {}

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
            ) -> int:
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

        authentication_code =

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

    @staticmethod
    def send_authentication_email(email_address: str) -> bool:
        """
        Send a confirmation email to a user with a code

        Returns
        -------
        bool
            Whether or not the email was successfully sent
        """

        try:
            port = 465
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as s:
                s.login(
                    sender:=SecretsHandler.get_email_address(),
                    SecretsHandler.get_email_passkey()
                )
                s.sendmail(
                    sender,
                    email_address,
                    AuthHandler.PLAIN_TEXT.format(
                        "Authenticate your SentiSounds Account!",
                        "Thank you for registering with SentiSounds!\n" +
                        "You have 1 minute to enter this code to authenticate: 1234\n"
                    )
                )
            return True

        except:
            return False

    @staticmethod
    def generate_random_code(email_address: str):
        ...

    # TODO: Spotify Authentication

if __name__ == "__main__":
    print(AuthHandler.send_authentication_email("jojomedhat2004@gmail.com"))