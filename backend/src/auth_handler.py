"""A handler for signing up, authenticating emails, and logging in"""

import json
import random
import re
import smtplib
import ssl
from datetime import datetime, timedelta
from typing import Callable

from database_handler import DatabaseHandler
from secrets_handler import SecretsHandler


class AuthHandler:
    """
    A static class to handle non-Spotify user authentication.

    The general flow of authentication is as follows:
    A user signs-up with a valid email, password, and display name and they
    will be sent an email containing a verification code
    The user then enters this verification code within an alloted time limit
    to finally be let into the database
    On login, the user must enter the correct pair of email address and
    password to be allowed access.

    As such, the sign-up function takes an email address, password, first name,
    and last initial.
    The authentication function takes the same sign-up parameters *and* the
    entered authentication code
    The login function takes an email and password
    """

    EMAIL_REGEX = re.compile(
        r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", flags=re.IGNORECASE
    )
    """A regex statement defining a valid email address"""

    EMAIL_CHECK: list[tuple[Callable[[str], bool], str]] = [
        (lambda x: bool(x), "No email address was entered."),
        (
            lambda x: bool(AuthHandler.EMAIL_REGEX.match(x)),
            "An invalid email address was entered.",
        ),
    ]
    """
    Defines the checks to make for an email as a list of lambdas returning
    bools and the associated error messages
    """

    PASSWORD_CHECK: list[tuple[Callable[[str], bool], str]] = [
        (lambda x: bool(x), "No password was entered."),
        (
            lambda x: any(chr.islower() for chr in x),
            "Password must contain at least one lowercase letter a-z",
        ),
        (
            lambda x: any(chr.isupper() for chr in x),
            "Password must contain at least one uppercase letter a-z",
        ),
        (
            lambda x: any(chr.isdigit() for chr in x),
            "Password must contain at least one digit 0-9",
        ),
        (
            lambda x: any(chr in "~!@#$%^&*-_+" for chr in x),
            "Password must contain at least one special character "
            + "e.g. ~!@#$%^&*-_+",
        ),
        (lambda x: len(x) > 7, "Password must be at least 7 characters long"),
    ]
    """
    Defines the checks to make for a password as a list of lambdas returning
    bools and the associated error messages
    """

    PLAIN_TEXT = "Subject: {}\nTo: {}\n\n{}"
    """A frame for the email to send a to-be authenticated user"""

    # email_address: (code, expiry time)
    ACTIVE_AUTHS: dict[str, tuple[str, float]] = {}
    """A dictionary of currently authenticating users"""

    @staticmethod
    def valid_password(password: str) -> bool:
        """
        Given a password string, return if it's valid

        Parameters
        ----------
        password : str
            The password to check

        Returns
        -------
        bool
            If a return value is given, it is guaranteed to be True. If the
            password is invalid, an error will be raised

        Raises
        ------
        ValueError
            The reason why the password wasn't valid (if it is not)
        """
        for check, error_message in AuthHandler.PASSWORD_CHECK:
            if not check(password):
                raise ValueError(error_message)
        return True

    @staticmethod
    def valid_email(email_address: str) -> bool:
        """
        Given an email address string, return if it's valid

        This does not check for the *existence* of the email address, but
        rather checks against an email address pattern

        Parameters
        ----------
        email_address : str
            The email address to check

        Returns
        -------
        bool
            If a return value is given, it is guaranteed to be True. If the
            password is invalid, an error will be raised

        Raises
        ------
        ValueError
            The reason why the email address wasn't valid (if it is not)
        """
        for check, error_message in AuthHandler.EMAIL_CHECK:
            if not check(email_address):
                raise ValueError(error_message)
        return True

    @staticmethod
    def check_identifiers(
        email_address: str,
        password: str,
        first_name: str,
        last_initial: str = "",
    ) -> None:
        """
        Checks the validity of a user's email address, password, and display
        name.

        This function does not return a value, but rather throws an error
        depending on which field was invalid.

        Raises
        ------
        ValueError
            If the first name is too short (empty)
            If the first name is too long (longer than 29 characters)
            If the last initial is too long (longer than 1 character)
            If the email does not pass the email checker `valid_email`
            If the password does not pass the password checker `valid_password`
        """
        if not first_name:
            raise ValueError("The first name entered was too short.")

        if len(first_name) > 29:
            raise ValueError("The first name entered was too long.")

        if len(last_initial) > 1:
            raise ValueError("The last initial entered was too long.")

        try:
            AuthHandler.valid_email(email_address)
        except Exception as e:
            raise ValueError("The email address is invalid: " + str(e))

        try:
            AuthHandler.valid_password(password)
        except Exception as e:
            raise ValueError("That password is invalid: " + str(e))

    @staticmethod
    def sign_up(
        email_address: str,
        password: str,
        first_name: str,
        last_initial: str = "",
    ) -> None:
        """
        Creates a sign-in session and waits for an authentication code

        Parameters
        ----------
        email_address : str
            The email address of the user. Must pass validity via `valid_email`
        password : str
            The password of the user. Must pass validity via `valid_password`
        first_name : str
            The user's first name. Must be >= 1 and <= 29 characters
        last_initial : str, default=""
            The user's last initial

        Raises
        ------
        ValueError
            If an invalid email address, password, or name is provided
            If an email could not be sent
        """

        AuthHandler.check_identifiers(
            email_address, password, first_name, last_initial
        )

        auth_code = AuthHandler.generate_random_code(email_address)

        try:
            AuthHandler.send_authentication_email(email_address, auth_code)
        except Exception as e:
            raise ValueError(
                "Something went wrong sending the authentication email: "
                + str(e)
            )

    @staticmethod
    async def log_in(email_address: str, password: str) -> bool:
        """
        Attempts to log-in given a user's credentials

        Parameters
        ----------
        email_address : str
            The email address associated with the target user
        password : str
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
                email_address,
                password,
            )

        return bool(found)

    @staticmethod
    async def authenticate_user(
        email_address: str,
        password: str,
        entered_auth_code: str,
        first_name: str,
        last_initial: str = "",
    ) -> None:
        """
        Attempt to authenticate a user's login via the code they were sent

        Ensure you are first calling sign_up(...) to generate an authentication
        code

        Parameters
        ----------
        email_address : str
            The email address of the user
        password : str
            The password of the user
        entered_auth_code : str
            The authentication code the user entered
        first_name : str
            The user's first name
        last_initial : str, default=""
            The user's last initial

        Raises
        ------
        ValueError
            If an invalid email address, password, or name is provided
            If the incorrect code was entered or something went wrong adding
            the user to the database
        """

        AuthHandler.check_identifiers(
            email_address, password, first_name, last_initial
        )

        display_name = first_name + (
            f" {last_initial}." if last_initial else ""
        )

        if email_address not in AuthHandler.ACTIVE_AUTHS:
            raise ValueError(
                "This email address does not have any active codes"
            )

        needed, expiry = AuthHandler.ACTIVE_AUTHS[email_address]
        if needed != entered_auth_code or datetime.now().timestamp() > expiry:
            raise ValueError(
                "An incorrect code was entered, or the code has expired"
            )

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
                    email_address,
                    password,
                    display_name,
                )
            except Exception:
                raise ValueError(
                    "This email address was already found in the database."
                )

    @staticmethod
    def send_authentication_email(email_address: str, auth_code: str) -> None:
        """
        Send a confirmation email to a user with a code

        Raises
        ------
        SMTPHeloError
            The server didn't reply properly to the helo greeting.
        SMTPRecipientsRefused
            The server rejected ALL recipients (no mail was sent).
        SMTPSenderRefused
            The server didn't accept the from_addr.
        SMTPDataError
            The server replied with an unexpected error code
            (other than a refusal of a recipient).
        SMTPNotSupportedError
            The mail_options parameter includes 'SMTPUTF8'
            but the SMTPUTF8 extension is not supported by the server.
        """
        port = 465
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as s:
            s.login(
                sender := SecretsHandler.get_email_address(),
                SecretsHandler.get_email_passkey(),
            )
            s.sendmail(
                sender,
                email_address,
                AuthHandler.PLAIN_TEXT.format(
                    "Authenticate your SentiSounds Account!",
                    email_address,
                    "Thank you for registering with SentiSounds!\n"
                    + "You have 1 minute to enter this authentication code: "
                    + auth_code
                    + "\n",
                ),
            )

    @staticmethod
    def generate_random_code(email_address: str) -> str:
        """
        Generates a random code and stores it in the authentication cache

        Parameters
        ----------
        email_address : str
            The email address that this code belongs to

        Returns
        -------
        str
            The generated code
        """
        random_code = "".join([str(random.randint(0, 9)) for _ in range(5)])
        expiry_time = (datetime.now() + timedelta(minutes=1)).timestamp()

        AuthHandler.ACTIVE_AUTHS[email_address] = (random_code, expiry_time)
        return random_code

    @staticmethod
    async def save_spotify_token(email_address: str, token: dict) -> None:
        """
        Given an email address, save the user's Spotify token

        Parameters
        ----------
        email_address : str
            The email address of the user
        token : str
            The user's Spotify token
        """

        async with DatabaseHandler.acquire() as conn:
            await conn.execute(
                """
                UPDATE
                    user_auth
                SET
                    spotify_token = $1
                WHERE
                    email_address = $2
                """,
                json.dumps(token),
                email_address,
            )

    @staticmethod
    async def get_spotify_token(email_address: str) -> dict:
        """
        Given an email address, return the user's Spotify token

        Parameters
        ----------
        email_address : str
            The email address of the user

        Returns
        -------
        str
            The user's Spotify token
        """
        async with DatabaseHandler.acquire() as conn:
            found = await conn.fetch(
                """
                SELECT
                    spotify_token
                FROM
                    user_auth
                WHERE
                    email_address = $1
                """,
                email_address,
            )
            return json.loads(found[0]["spotify_token"])

    @staticmethod
    def check_and_save_spotify_token(
        email_address: str, old_token: dict, new_token: dict
    ) -> None:
        """
        Given an email address, check if the user's Spotify token has changed
        and save it

        Parameters
        ----------
        email_address : str
            The email address of the user
        old_token : dict
            The user's old Spotify token
        new_token : dict
            The user's new Spotify token
        """
        if old_token is not None and old_token != new_token:
            AuthHandler.save_spotify_token(email_address, new_token)
