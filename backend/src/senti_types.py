from typing import TypedDict


class song_type(TypedDict):
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
    access_token: str
    token_type: str
    expires_in: int
    scope: str | list[str]
    expires_at: int
    refresh_token: str
