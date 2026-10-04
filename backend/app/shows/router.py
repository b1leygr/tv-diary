from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Query

from app.core.dependencies import CurrentUser, DbSession, TmdbClient
from app.shows import service as show_service
from app.shows.schemas import (
    EpisodeLogResponse,
    EpisodeResponse,
    EpisodeSummary,
    SeasonResponse,
    ShowResponse,
    ShowSearchRequest,
    ShowSearchResult,
)

router = APIRouter(tags=['shows'])


@router.get('/shows', response_model=list[ShowSearchResult])
async def search_shows(
    query: Annotated[
        ShowSearchRequest,
        Query(),
    ],
    tmdb_client: TmdbClient,
):
    return await show_service.search_tmdb_show(tmdb_client, query)


@router.get('/shows/{show_id}', response_model=ShowResponse)
async def get_show(
    show_id: int,
    tmdb_client: TmdbClient,
    user: CurrentUser,
    db: DbSession,
):
    return await show_service.get_show(db, user, tmdb_client, show_id)


@router.get(
    '/seasons/{season_id}', response_model=SeasonResponse | list[EpisodeSummary]
)
async def get_season(
    season_id: int,
    user: CurrentUser,
    db: DbSession,
    view: Annotated[Literal['full', 'progress'] | None, Query()] = 'full',
):
    return await show_service.get_season(db, user, season_id, view)


@router.get('/episodes/{episode_id}', response_model=EpisodeResponse)
async def get_episode(
    episode_id: int,
    user: CurrentUser,
    db: DbSession,
):
    return await show_service.get_episode(db, user, episode_id)


@router.post('/episodes/{episode_id}/logs', response_model=EpisodeLogResponse)
async def log_episode(
    episode_id: int,
    user: CurrentUser,
    db: DbSession,
    logged_at: Annotated[datetime | None, Body()] = None,
):
    return await show_service.log_episode(db, user, episode_id, logged_at)
