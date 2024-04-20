import queue
import threading
from typing import Any
import json

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from secrets_handler import SecretsHandler


class YoutubeHandler:
    """
    A handler for interacting with the YouTube API.

    Contains a definition for a static _client_instance. This should only be
    accessed via the `youtube` field, which will automatically fill this field
    if it does not yet exist. Any other accesses to this instance are unsafe
    and should not be used.


    """

    api_service_name = "youtube"
    api_version = "v3"
    MAX_THREAD_COUNT: int = 5
    _youtube_instance: discovery.Resource | None = None
    request_queue: queue.Queue = queue.Queue()
    thread_pool: list[threading.Thread] = []
    _id_cache: dict[str, str] = {}

    def __init__(self):
        """
        Raises a TypeError.
        YoutubeHandler instances must not be created as this is a singleton
        """
        raise TypeError(
            "YoutubeHandler instances should not be created. "
            + "Consider using the `get_client()` function."
        )

    @staticmethod
    def get_client():
        """
        Retrieves or creates the YouTube client instance

        Returns
        -------
        googleapiclient.discovery.Resource
            The static YouTube client
        """
        if YoutubeHandler._youtube_instance:
            return YoutubeHandler._youtube_instance

        return YoutubeHandler._initialize_client()

    @staticmethod
    def _initialize_client() -> Any:
        """
        Initializes the YouTube client.
        """
        with open("cache/youtube_id_cache.json", "r") as file:
            contents = file.read()
            if contents == "":
                YoutubeHandler._id_cache = {}
            else:
                YoutubeHandler._id_cache = json.loads(contents)
        _youtube_instance: Any = discovery.build(
            YoutubeHandler.api_service_name,
            YoutubeHandler.api_version,
            developerKey=SecretsHandler.get_youtube_key(),
        )
        return _youtube_instance

    @staticmethod
    def search_for_match(song: dict):
        """
        Searches for a matching song on youtube given the song and artist name
        Adds the youtube url to the song dictionary
        if no match is found, the song is returned as None

        Returns
        -------
        googleapiclient.discovery.Resource
            The search results
        """
        youtube_url = "https://www.youtube.com/watch?v=%s"
        response = None
        if song["name"] in YoutubeHandler._id_cache:
            song["youtube_url"] = (
                youtube_url % YoutubeHandler._id_cache[song["name"]]
            )
        else:
            try:
                client = YoutubeHandler.get_client()

                response = (
                    client.search()  # type: ignore
                    .list(
                        part="id",
                        q=song["name"] + " " + song["artists"][0]["name"],
                        type="video",
                        maxResults=1,
                        order="relevance",
                        fields="items(id(videoId))",
                    )
                    .execute()
                )
            except HttpError:
                # If the request fails, it probably means the quota has been
                # exceeded If this happens too often, consider applying for a
                # quota increase at:
                # https://support.google.com/youtube/contact/yt_api_form
                # For now, we'll just ignore the error and return nothing
                pass
            if response and response["items"]:
                song["youtube_url"] = (
                    youtube_url % response["items"][0]["id"]["videoId"]
                )
                # Cache the id
                YoutubeHandler._id_cache[song["name"]] = response["items"][0][
                    "id"
                ]["videoId"]
            else:
                song["youtube_url"] = ""
        return song

    @classmethod
    def match_list(cls, songs: list[dict[str, str | bool | int]]):
        """
        Matches a list of songs to their respective youtube videos

        Parameters
        ----------
        songs : list[dict[str, str | bool | int]]
            A list of songs to match
        """

        for song in songs:
            cls.request_queue.put(song)
        for _ in range(cls.MAX_THREAD_COUNT):
            thread = threading.Thread(target=cls._process_queue)
            thread.start()
            cls.thread_pool.append(thread)

        cls.request_queue.join()

        for _ in range(cls.MAX_THREAD_COUNT):
            cls.request_queue.put(
                None
            )  # Add a None to the queue for each thread to stop processing

    @classmethod
    def _process_queue(cls):
        """
        Processes the request queue
        """
        while True:
            # Get a request from the queue
            song = cls.request_queue.get()

            # If the queue is empty, break the loop
            if song is None:
                break

            cls.search_for_match(song)
            # Mark the task as done
            cls.request_queue.task_done()

    @classmethod
    def save_cache(cls):
        """
        Saves the id cache to a file
        """
        with open("cache/youtube_id_cache.json", "w") as file:
            json.dump(cls._id_cache, file)


if __name__ == "__main__":
    YoutubeHandler.get_client()
    print(
        YoutubeHandler.search_for_match(
            {
                "name": "Gamma Knife",
                "artists": [{"name": "King Gizzard & The Lizard Wizard"}],
            }
        )
    )
    YoutubeHandler.save_cache()
