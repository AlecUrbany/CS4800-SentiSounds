"""Short-hands for types used throughout SentiSounds"""
from __future__ import annotations

from typing import TypedDict


class song_type(TypedDict):
    """
    Defines the type for Song objects retrieved from the Spotify API and
    modified by SentiSounds
    """
    name: str
    album: dict[str, str | list[dict[str, str | int]] | dict[str, str]]
    artists: list[dict[str, str | dict[str, str]]]
    preview_url: str
    external_urls: dict[str, str]
    explicit: bool
    is_playable: bool
    popularity: int
    id: str
    liked_by_user: bool


class token_type(TypedDict):
    """
    Defines the type for user authentication tokens from Spotify
    """
    access_token: str
    token_type: str
    expires_in: int
    scope: str | list[str]
    expires_at: int
    refresh_token: str
