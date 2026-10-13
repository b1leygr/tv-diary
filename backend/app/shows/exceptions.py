from fastapi import status

from app.core.exceptions import DomainException


class EpisodeNotFound(DomainException):
    def __init__(self, episode_id: int):
        super().__init__(
            title='Episode Not Found',
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Episode with ID '{episode_id}' not found.",
        )


class SeasonNotFound(DomainException):
    def __init__(self, season_id: int):
        super().__init__(
            title='Season Not Found',
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Season with ID '{season_id}' not found.",
        )


class ShowNotFound(DomainException):
    def __init__(self, show_id: int):
        super().__init__(
            title='Show Not Found',
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Show with ID '{show_id}' not found.",
        )


class TmdbClientError(DomainException):
    def __init__(self, status_code: int, message: str):
        super().__init__(
            title='TMDB Client Error',
            status_code=status_code,
            message=message,
        )
