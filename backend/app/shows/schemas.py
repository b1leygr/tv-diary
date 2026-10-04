from datetime import date, datetime
from operator import itemgetter
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)


class CastMemberCreate(BaseModel):
    id: int
    name: str
    profile_path: str | None
    character: str | None


def parse_cast(cast_members: list) -> list[CastMemberCreate]:
    return [
        CastMemberCreate(**cast_member)
        for cast_member in sorted(cast_members or [], key=itemgetter('order'))
    ]


class Actor(BaseModel):
    id: int
    name: str
    profile_path: str | None
    model_config = ConfigDict(from_attributes=True)


class CastMemberResponse(BaseModel):
    actor: Actor = Field(exclude=True)
    character: str | None
    model_config = ConfigDict(from_attributes=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def id(self) -> int:
        return self.actor.id

    @computed_field  # type: ignore[prop-decorator]
    @property
    def name(self) -> str:
        return self.actor.name

    @computed_field  # type: ignore[prop-decorator]
    @property
    def profile_path(self) -> str | None:
        return self.actor.profile_path


class Creator(BaseModel):
    id: int
    name: str
    profile_path: str | None
    model_config = ConfigDict(from_attributes=True)


class EpisodeBase(BaseModel):
    id: int
    name: str
    episode_number: int
    overview: str | None
    runtime: int | None
    air_date: date | None
    vote_average: float | None
    guest_stars: list[CastMemberCreate] | list[CastMemberResponse]
    still_path: str | None


class SeasonBase(BaseModel):
    id: int
    name: str
    season_number: int
    overview: str | None
    air_date: date | None
    vote_average: float | None
    cast: list[CastMemberCreate] | list[CastMemberResponse]
    poster_path: str | None


class ShowBase(BaseModel):
    id: int
    name: str
    status: str | None
    overview: str | None
    genres: list[str]
    first_air_date: date | None
    last_air_date: date | None
    vote_average: float | None
    creators: list[Creator]
    poster_path: str | None
    backdrop_path: str | None


class EpisodeCreate(EpisodeBase):
    guest_stars: Annotated[list[CastMemberCreate], BeforeValidator(parse_cast)]


class SeasonCreate(SeasonBase):
    cast: Annotated[list[CastMemberCreate], BeforeValidator(parse_cast)]
    episodes: list[EpisodeCreate]

    @model_validator(mode='before')
    @classmethod
    def get_cast(cls, data):
        data['cast'] = data.get('credits', {}).get('cast', [])
        return data


class ShowCreate(ShowBase):
    creators: list[Creator] = Field(validation_alias='created_by')
    season_numbers: list[int]

    @field_validator('genres', mode='before')
    @classmethod
    def parse_genres(cls, genres):
        return [genre.get('name') for genre in genres]

    @model_validator(mode='before')
    @classmethod
    def get_season_numbers(cls, data):
        data['season_numbers'] = sorted(
            [
                season.get('season_number')
                for season in data.get('seasons', [])
                if season.get('season_number') is not None
            ]
            or []
        )
        return data


class EpisodeResponse(EpisodeBase):
    guest_stars: list[CastMemberResponse]
    season_id: int
    is_logged: bool
    model_config = ConfigDict(from_attributes=True)


class EpisodeSummary(BaseModel):
    id: int
    name: str | None
    is_logged: bool


class SeasonResponse(SeasonBase):
    cast: list[CastMemberResponse]
    show_id: int
    episodes_with_progress: list[EpisodeSummary]
    model_config = ConfigDict(from_attributes=True)


class SeasonSummary(BaseModel):
    id: int
    name: str | None
    logged_eps: int
    total_eps: int


class ShowResponse(ShowBase):
    seasons_with_progress: list[SeasonSummary] | None
    last_updated: datetime
    model_config = ConfigDict(from_attributes=True)


class ShowSearchRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, description='A title to search')]


class ShowSearchResult(BaseModel):
    name: str
    id: int
    poster_path: str | None = None
    year: int | None = None

    @model_validator(mode='before')
    @classmethod
    def extract_year(self, data: dict) -> dict:
        first_air_date: str | None = data.get('first_air_date')
        data['year'] = int(first_air_date.split('-')[0]) if first_air_date else None
        return data


class EpisodeLogResponse(BaseModel):
    episode_id: int
    logged_at: datetime | None
    episode_name: str
    model_config = ConfigDict(from_attributes=True)


class UserLogSummary(BaseModel):
    logged_at: datetime
    episode_name: str
    season_name: str
    show_name: str
