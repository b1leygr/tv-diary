from typing import Annotated

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession, TmdbClient
from app.shows import service as show_service
from app.shows.schemas import (
    EpisodeResponse,
    SeasonResponse,
    ShowResponse,
    ShowSearchRequest,
    ShowSearchResult,
)

router = APIRouter(prefix='/shows', tags=['shows'])


@router.get('', response_model=list[ShowSearchResult])
async def search_shows(
    query: Annotated[
        ShowSearchRequest,
        Query(),
    ],
    tmdb_client: TmdbClient,
):
    return await show_service.search_tmdb_show(tmdb_client, query)


@router.get('/{show_id}', response_model=ShowResponse)
async def get_show(
    show_id: int,
    tmdb_client: TmdbClient,
    db: DbSession,
):
    return await show_service.get_show(db, tmdb_client, show_id)


@router.get('/{show_id}/seasons/{season_number}', response_model=SeasonResponse)
async def get_season(
    show_id: int,
    season_number: int,
    db: DbSession,
):
    return await show_service.get_season(db, show_id, season_number)


@router.get(
    '/{show_id}/seasons/{season_number}/episodes/{episode_number}',
    response_model=EpisodeResponse,
)
async def get_episode(
    show_id: int,
    season_number: int,
    episode_number: int,
    db: DbSession,
):
    return await show_service.get_episode(db, show_id, season_number, episode_number)
