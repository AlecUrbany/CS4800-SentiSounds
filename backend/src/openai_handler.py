from openai import OpenAI
import json

from secrets_handler import SecretsHandler

class OpenAIHandler:
    """
    A static class to handle all OpenAI API interactions.

    Contains a definition for a static _client_instance. This should only be
    accessed via the `get_client()` function, which will automatically fill
    this field if it does not yet exist. Any other accesses to this instance
    are unsafe and should not be used.
    """

    GPT_MODEL = "gpt-3.5-turbo"
    PROMPT = SecretsHandler.get_gpt_prompt()

    def __init__(self) -> None:
        raise TypeError(
            "OpenAIHandler instances should not be created.",
            "Consider using `get_client()`"
        )

    # A static reference to the OpenAI client
    _client_instance: OpenAI | None = None

    @staticmethod
    def get_client() -> OpenAI:
        """
        Retrieves or creates the OpenAI client instance

        Returns
        -------
        OpenAI
            The static OpenAI client
        """
        if OpenAIHandler._client_instance:
            return OpenAIHandler._client_instance

        return OpenAIHandler._initialize_client()

    @staticmethod
    def _initialize_client() -> OpenAI:
        """
        Initializes the OpenAI client.

        This function should never be called outside of this class. To retrieve
        the client safely, use the `get_client` function.

        Returns
        -------
        OpenAI
            The static OpenAI client
        """
        OpenAIHandler._client_instance = OpenAI(
            api_key=SecretsHandler.get_openai_key()
        )

        return OpenAIHandler._client_instance