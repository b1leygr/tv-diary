from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUser, DbSession, TmdbClient
from app.tv import service as show_service
from app.tv.schemas import (
    ActivityLogRequest,
    ActivityLogResponse,
    ActivityLogSummary,
    EpisodeResponse,
    EpisodeSummary,
    SeasonResponse,
    ShowResponse,
    ShowSearchRequest,
    ShowSearchResult,
)

router = APIRouter(
    tags=['tv'],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {},
    },
)


@router.get(
    '/shows',
    response_model=list[ShowSearchResult],
    responses={
        status.HTTP_502_BAD_GATEWAY: {},
        status.HTTP_503_SERVICE_UNAVAILABLE: {},
        status.HTTP_504_GATEWAY_TIMEOUT: {},
    },
)
async def search_shows(
    query: Annotated[
        ShowSearchRequest,
        Query(),
    ],
    tmdb_client: TmdbClient,
):
    return await show_service.search_tmdb_show(tmdb_client, query)


@router.get(
    '/shows/{show_id}',
    response_model=ShowResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_502_BAD_GATEWAY: {},
        status.HTTP_503_SERVICE_UNAVAILABLE: {},
        status.HTTP_504_GATEWAY_TIMEOUT: {},
    },
)
async def get_show(
    show_id: int,
    tmdb_client: TmdbClient,
    user: CurrentUser,
    db: DbSession,
):
    return await show_service.get_show(db, user, tmdb_client, show_id)


@router.get(
    '/seasons/{season_id}',
    response_model=SeasonResponse | list[EpisodeSummary],
    responses={status.HTTP_401_UNAUTHORIZED: {}, status.HTTP_404_NOT_FOUND: {}},
)
async def get_season(
    season_id: int,
    user: CurrentUser,
    db: DbSession,
    view: Annotated[Literal['full', 'progress'] | None, Query()] = 'full',
):
    return await show_service.get_season(db, user, season_id, view)


@router.get(
    '/episodes/{episode_id}',
    response_model=EpisodeResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {}, status.HTTP_404_NOT_FOUND: {}},
)
async def get_episode(
    episode_id: int,
    user: CurrentUser,
    db: DbSession,
):
    return await show_service.get_episode(db, user, episode_id)


@router.post(
    '/me/activity',
    response_model=ActivityLogResponse,
    response_model_exclude_none=True,
    responses={status.HTTP_401_UNAUTHORIZED: {}, status.HTTP_404_NOT_FOUND: {}},
)
async def log_activity(
    log_request: ActivityLogRequest,
    user: CurrentUser,
    db: DbSession,
):
    return await show_service.log_activity(db, user, log_request)


@router.get(
    '/me/activity',
    response_model=list[ActivityLogSummary],
    response_model_exclude_none=True,
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
async def get_activity(
    current_user: CurrentUser,
    db: DbSession,
    view: Annotated[
        Literal['episodes', 'seasons', 'shows'] | None, Query()
    ] = 'episodes',
):
    return await show_service.get_activity(db, current_user, view)
