"""A handler for interacting with OpenAI's API and the GPT model"""

import json
from typing import Callable

from openai import OpenAI
from secrets_handler import SecretsHandler


class OpenAIHandler:
    """
    A static class to handle all OpenAI API interactions.

    Contains a definition for a static _client_instance. This should only be
    accessed via the `get_client()` function, which will automatically fill
    this field if it does not yet exist. Any other accesses to this instance
    are unsafe and should not be used.

    `OpenAIHandler.get_genres()` is what should be used to retrieve a list of
    genres given a sanitized user input.
    """

    GPT_MODEL = "gpt-3.5-turbo"
    """The AI model to retrieve responses from"""

    PROMPT = SecretsHandler.get_gpt_prompt()
    """The system prompt to feed the AI model"""

    PROMPT_CHECK: list[tuple[Callable[[str], bool], str]] = [
        (lambda x: bool(x), "No prompt was entered."),
        (lambda x: len(x) > 5, "That prompt was too short. Min 5 chars."),
        (lambda x: len(x) < 200, "That prompt was too long. Max 200 chars."),
        (
            lambda x: all(chr not in "^*_=+;\\|" for chr in x),
            "The prompt cannot contain the following characters: "
            + "^*_=+;\\|",
        ),
    ]
    """
    Defines the checks to make for a prompt as a list of lambdas returning
    bools and the associated error messages
    """

    def __init__(self) -> None:
        """
        Raises a TypeError.
        OpenAIHandler instances must not be created as this is a singleton
        """
        raise TypeError(
            "OpenAIHandler instances should not be created. "
            + "Consider using the `get_client()` function."
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
        openai.OpenAI
            The static OpenAI client
        """
        OpenAIHandler._client_instance = OpenAI(
            api_key=SecretsHandler.get_openai_key()
        )

        return OpenAIHandler._client_instance

    @staticmethod
    def sanitize_input(unsanitized_input: str) -> str:
        """
        Given an unsanitized input, return its sanitized counterpart and
        perform checks to ensure that it is valid

        Parameters
        ----------
        unsanitized_input : str
            The input to sanitize

        Returns
        -------
        str
            The newly sanitized input

        Raises
        ------
        ValueError
            The reason why the input couldn't be sanitized
        """
        sanitized_input = unsanitized_input.strip()

        for check, error_message in OpenAIHandler.PROMPT_CHECK:
            if not check(sanitized_input):
                raise ValueError(error_message)

        return sanitized_input

    @staticmethod
    def get_genres(sanitized_input: str) -> list[str]:
        """
        Retrieves a response from the supplied GPT model given an input.

        This input must be pre-sanitized as it will be given directly to the
        model.

        GPT chat completion is non-deterministic by nature. Meaning, the same
        user input may result in a different genres list. We try to mitigate
        this by providing a `seed` value to the API call, but no guarantees
        are made by the OpenAI documentation:
        https://platform.openai.com/docs/guides/text-generation/reproducible-outputs

        Parameters
        ----------
        sanitized_input : str
            The user input (probably an emotion or a phrase describing one)
            to pass to the GPT model

        Returns
        -------
        list[str]
            A list of genres retrieved via the user's input. Unless GPT messes
            up, this list should contain 5 genres

        Raises
        ------
        ValueError
            if no response was provided by the OpenAI API,
            if the provided response couldn't be parsed into JSON,
            if the parsed JSON did not contain the `genres` key
            if no genres were found
        """
        # Retrieve a response from GPT
        client = OpenAIHandler.get_client()
        response = client.chat.completions.create(
            model=OpenAIHandler.GPT_MODEL,
            response_format={"type": "json_object"},
            # seed=69,
            messages=[
                {"role": "system", "content": OpenAIHandler.PROMPT},
                {"role": "user", "content": sanitized_input},
            ],
        )

        # Ensure a response was found
        found_content = response.choices[0].message.content
        if not found_content:
            raise ValueError(
                "Something went wrong retrieving a response from GPT. "
                + "No response was provided."
            )

        # Ensure the response is JSON
        try:
            content_json = json.loads(found_content)
        except Exception:
            raise ValueError(
                "Something went wrong retrieving a response from GPT. "
                + "The provided response could not be parsed into JSON."
            )

        # Ensure the JSON contains the genres
        if "genres" not in content_json:
            raise ValueError(
                "Something went wrong retrieving a response from GPT. "
                + f"The parsed JSON `{content_json}` "
                + "does not contain the `genres` key."
            )

        # Ensure that genres is a list
        content_genres = content_json["genres"]
        if not isinstance(content_genres, list):
            raise ValueError(
                "Something went wrong retrieving a response from GPT. "
                + f"Genres retrieved are not a list: `{content_genres}`."
            )

        # Ensure that each genre is a string and fix its casing
        content_genres = [str(genre).lower() for genre in content_genres]

        if not content_genres:
            raise ValueError("No genres could be found from the given input.")

        # Return the genres themselves
        return content_genres
