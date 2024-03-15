from __future__ import annotations

import json


class SecretsHandler:

    SECRETS_FILE = "secrets.json"

    @staticmethod
    def _get_json_value(key: str, sub: str) -> str:
        """
        Returns any value from the provided SECRETS_FILE
        given a key and sub-key

        Parameters
        ----------
        key: str
        sub: str
            The key and sub-key pair of the value to extract, such that
            json[key][sub] contains the requested value
        """
        with open(SecretsHandler.SECRETS_FILE) as s:
            json_data = json.load(s)
            return json_data[key][sub]

    @classmethod
    def get_openai_key(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the OpenAI API key using key open-ai and sub-key api-key

        Returns
        -------
        str
            The OpenAI API key
        """
        return cls._get_json_value("open-ai", "api-key")

    @classmethod
    def get_gpt_prompt(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the OpenAI GPT prompt using key open-ai and sub-key prompt

        Returns
        -------
        str
            The OpenAI GPT prompt
        """
        return cls._get_json_value("open-ai", "prompt")

    @classmethod
    def get_spotify_client_id(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the Spotify API key using key spotify and sub-key api-key

        Returns
        -------
        str
            The Spotify API key
        """
        return cls._get_json_value("spotify", "client_id")

    @classmethod
    def get_spotify_client_secret(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the Spotify API key using key spotify and sub-key api-key

        Returns
        -------
        str
            The Spotify API key
        """
        return cls._get_json_value("spotify", "client_secret")

    @classmethod
    def get_database_user(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the database username using key database and sub-key username

        Returns
        -------
        str
            The database username
        """
        return cls._get_json_value("database", "username")

    @classmethod
    def get_database_password(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the database password using key database and sub-key password

        Returns
        -------
        str
            The database password
        """
        return cls._get_json_value("database", "password")

    @classmethod
    def get_database_name(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the database name using key database and
        sub-key database-name

        Returns
        -------
        str
            The database name
        """
        return cls._get_json_value("database", "database-name")

    @classmethod
    def get_database_host(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the database host using key database and sub-key host

        Returns
        -------
        str
            The database host
        """
        return cls._get_json_value("database", "host")

    @classmethod
    def get_database_port(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the database port using key database and sub-key port

        Returns
        -------
        str
            The database port
        """
        return cls._get_json_value("database", "port")

    @classmethod
    def get_email_address(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the email address using key email and sub-key address

        Returns
        -------
        str
            The email address
        """
        return cls._get_json_value("email", "address")

    @classmethod
    def get_email_password(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the email password using key email and sub-key password

        Returns
        -------
        str
            The email password
        """
        return cls._get_json_value("email", "password")

    @classmethod
    def get_email_passkey(cls: type[SecretsHandler]) -> str:
        """
        Retrieves the email passkey using key email and sub-key passkey

        This is what's actually used to log-in and send emails via SMTP.

        Research Less Secure Apps via Google.

        Returns
        -------
        str
            The email passkey
        """
        return cls._get_json_value("email", "passkey")
