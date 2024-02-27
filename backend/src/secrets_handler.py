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
