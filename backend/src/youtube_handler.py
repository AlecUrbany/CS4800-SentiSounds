"""A handler for interacting with YouTube's API through googleapiclient"""

import json
import queue
import threading

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from secrets_handler import SecretsHandler
from senti_types import song_type


class YoutubeHandler:
    """
    A handler for interacting with the YouTube API.

    Contains a definition for a static _client_instance. This should only be
    accessed via the `get_client()` function, which will automatically fill
    this field if it does not yet exist. Any other accesses to this instance
    are unsafe and should not be used.
    """

    api_service_name = "youtube"
    api_version = "v3"
    MAX_THREAD_COUNT: int = 5
    _youtube_instance: discovery.Resource | None = None
    request_queue: queue.Queue = queue.Queue()
    thread_pool: list[threading.Thread] = []
    _id_cache: dict[str, str] = {}
    _id_cache_lock: threading.Lock = threading.Lock()

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
    def _initialize_client() -> discovery.Resource:
        """
        Initializes the YouTube client.
        """
        with open(".cache/youtube_id_cache.json", "r") as file:
            contents = file.read()
            if contents == "":
                YoutubeHandler._id_cache = {}
            else:
                YoutubeHandler._id_cache = json.loads(contents)
        _youtube_instance: discovery.Resource = discovery.build(
            YoutubeHandler.api_service_name,
            YoutubeHandler.api_version,
            developerKey=SecretsHandler.get_youtube_key(),
        )
        return _youtube_instance

    @classmethod
    def search_for_match(cls, song: song_type):
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
        if song["name"] in cls._id_cache:
            song["external_urls"]["youtube"] = (
                youtube_url % cls._id_cache[song["name"]]
            )
            print(
                f"id {cls._id_cache[song['name']]} for {song['name']} found in cache"
            )
        else:
            try:
                client = cls.get_client()
                response = (
                    client.search()  # type: ignore
                    .list(
                        part="id",
                        q=(
                            song["name"]
                            + " "
                            + song["artists"][0]["name"]  # type: ignore
                        ),
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
                id = response["items"][0]["id"]["videoId"]
                song["external_urls"]["youtube"] = youtube_url % id
                # Cache the id
                with cls._id_cache_lock:
                    cls._id_cache[song["name"]] = id
            else:
                song["external_urls"]["youtube"] = ""
        return song

    @classmethod
    def match_list(cls, songs: list[song_type]):
        """
        Matches a list of songs to their respective youtube videos

        Parameters
        ----------
        songs : list[song_type]
            A list of songs to match
        """
        for song in songs:
            cls.search_for_match(song)
        # for now keep the threading code commented out as it is not working
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
        """

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
        with cls._id_cache_lock:
            with open(".cache/youtube_id_cache.json", "w") as file:
                json.dump(cls._id_cache, file)
