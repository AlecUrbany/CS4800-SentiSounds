import json

class SecretsHandler:

    SECRETS_FILE = "secrets.json"

    @staticmethod
    def _get_json_value(key: str, sub: str) -> str:
        """
        Returns any value from the provided SECRETS_FILE given a key and sub-key

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

    @staticmethod
    def get_openai_key() -> str:
        """
        Retrieves the OpenAI API key using key open-ai and sub-key api-key

        Returns
        -------
        str
            The OpenAI API key
        """
        return SecretsHandler._get_json_value("open-ai", "api-key")

    @staticmethod
    def get_gpt_prompt() -> str:
        """
        Retrieves the OpenAI GPT prompt using key open-ai and sub-key prompt

        Returns
        -------
        str
            The OpenAI GPT prompt
        """
        return SecretsHandler._get_json_value("open-ai", "prompt")

    @staticmethod
    def get_spotify_client_id() -> str:
        """
        Retrieves the Spotify API key using key spotify and sub-key api-key

        Returns
        -------
        str
            The Spotify API key
        """
        return SecretsHandler._get_json_value("spotify", "client_id")

    @staticmethod
    def get_spotify_client_secret() -> str:
        """
        Retrieves the Spotify API key using key spotify and sub-key api-key

        Returns
        -------
        str
            The Spotify API key
        """
        return SecretsHandler._get_json_value("spotify", "client_secret")

    @staticmethod
    def get_database_user() -> str:
        """
        Retrieves the database username using key database and sub-key username

        Returns
        -------
        str
            The database username
        """
        return SecretsHandler._get_json_value("database", "username")

    @staticmethod
    def get_database_password() -> str:
        """
        Retrieves the database password using key database and sub-key password

        Returns
        -------
        str
            The database password
        """
        return SecretsHandler._get_json_value("database", "password")

    @staticmethod
    def get_database_name() -> str:
        """
        Retrieves the database name using key database and sub-key database-name

        Returns
        -------
        str
            The database name
        """
        return SecretsHandler._get_json_value("database", "database-name")

    @staticmethod
    def get_email_address() -> str:
        """
        Retrieves the email address using key email and sub-key address

        Returns
        -------
        str
            The email address
        """
        return SecretsHandler._get_json_value("email", "address")

    @staticmethod
    def get_email_password() -> str:
        """
        Retrieves the email password using key email and sub-key password

        Returns
        -------
        str
            The email password
        """
        return SecretsHandler._get_json_value("email", "password")

    @staticmethod
    def get_email_passkey() -> str:
        """
        Retrieves the email passkey using key email and sub-key passkey

        This is what's actually used to log-in and send emails via SMTP.

        Research Less Secure Apps via Google.

        Returns
        -------
        str
            The email passkey
        """
        return SecretsHandler._get_json_value("email", "passkey")
