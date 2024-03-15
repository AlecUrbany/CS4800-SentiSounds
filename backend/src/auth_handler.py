"""A handler for signing up, authenticating emails, and logging in"""

import random
import re
import smtplib
import ssl
from datetime import datetime, timedelta

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

    PASSWORD_REGEX = re.compile(
        r".+"
    )
    """A regex statement defining a valid password"""

    PLAIN_TEXT = (
        "Subject: {}\nTo: {}\n\n{}"
    )
    """A frame for the email to send a to-be authenticated user"""

    # email_address: (code, expiry time)
    ACTIVE_AUTHS: dict[str, tuple[str, float]] = {}
    """A dictionary of currently authenticating users"""

    @staticmethod
    def valid_password(password: str) -> bool:
        """
        Given a password string, return if it's valid

        This does not check for the *existence* of the address, but rather
        checks against an password pattern

        Parameters
        ----------
        password : str
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

        This does not check for the *existence* of the address, but rather
        checks against an email address pattern

        Parameters
        ----------
        email_address : str
            The email address to check

        Returns
        -------
        bool
            Whether or not the address is valid
        """
        return bool(AuthHandler.EMAIL_REGEX.match(email_address))

    @staticmethod
    def sign_up(
                email_address: str,
                password: str,
                first_name: str,
                last_initial: str = ""
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
            If an invalid email address, password, or name is provided. Or
            if an email could not be sent
        """
        if not first_name:
            raise ValueError("The first name entered was too short.")

        if len(first_name) > 29:
            raise ValueError("The first name entered was too long.")

        if len(last_initial) > 1:
            raise ValueError("The last name entered was too long.")

        if not AuthHandler.valid_email(email_address):
            raise ValueError("An invalid email address was entered.")

        if not AuthHandler.valid_password(password):
            raise ValueError("An invalid password was entered.")

        auth_code = AuthHandler.generate_random_code(email_address)

        try:
            AuthHandler.send_authentication_email(email_address, auth_code)
        except Exception:
            raise ValueError(
                "Something went wrong sending the authentication email"
            )

    @staticmethod
    async def log_in(
                email_address: str,
                password: str
            ) -> bool:
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
                email_address, password
            )

        return bool(found)

    @staticmethod
    async def authenticate_user(
                email_address: str,
                password: str,
                entered_auth_code: str,
                first_name: str,
                last_initial: str = ""
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
            If the incorrect code was entered or something went wrong adding
            the user to the database
        """
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
                    email_address, password, display_name
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
                SecretsHandler.get_email_passkey()
            )
            s.sendmail(
                sender,
                email_address,
                AuthHandler.PLAIN_TEXT.format(
                    "Authenticate your SentiSounds Account!",
                    email_address,
                    "Thank you for registering with SentiSounds!\n" +
                    "You have 1 minute to enter this authentication code: " +
                    auth_code + "\n"
                )
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

    # TODO: Spotify Authentication
    # TODO: Figure out the flow of how authentication should work
    # TODO: Cache taken email addresses to return an error on signup