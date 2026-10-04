from asyncio import gather
from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import case, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import TmdbClient
from app.shows.models import (
    Actor,
    Creator,
    CreatorCredit,
    Episode,
    EpisodeLog,
    Role,
    Season,
    Show,
)
from app.shows.schemas import (
    SeasonCreate,
    ShowCreate,
    ShowSearchRequest,
)
from app.users.models import User


async def get_show(
    db: AsyncSession, user: User, tmdb_client: TmdbClient, show_id: int
) -> Show:
    eps_per_season = func.count(Episode.id).label('eps_per_season')

    logged_eps_per_season = func.count(EpisodeLog.episode_id.distinct()).label(
        'logged_eps_per_season'
    )

    query = (
        select(Show, Season.id, Season.name, logged_eps_per_season, eps_per_season)
        .options(selectinload(Show.show_creators).selectinload(CreatorCredit.creator))
        .join(Show.seasons)
        .join(Season.episodes)
        .outerjoin(
            EpisodeLog,
            ((EpisodeLog.episode_id == Episode.id) & (EpisodeLog.user_id == user.id)),
        )
        .where(Season.show_id == show_id)
        .group_by(Show.id, Season.id)
        .order_by(Show.name, Season.name)
    )

    result = (await db.execute(query)).all()
    if result:
        show = result[0][0]
        if (
            show.last_updated.timestamp()
            > (datetime.now() - timedelta(days=7)).timestamp()
        ):
            show.seasons_with_progress = await parse_progress(result, 'seasons')
            return show

    response = await tmdb_client.get(f'/tv/{show_id}')
    response.raise_for_status()
    data = response.json()

    parsed_show_data = ShowCreate.model_validate(data)
    show_record = parsed_show_data.model_dump(exclude={'season_numbers', 'creators'})
    show_record = Show(**show_record)

    tasks = [
        get_tmdb_season(tmdb_client, show_id, season_number)
        for season_number in parsed_show_data.season_numbers
    ]
    seasons = await gather(*tasks)

    all_actors = {}

    validated_seasons = [SeasonCreate.model_validate(season) for season in seasons]

    for season in validated_seasons:
        for actor in season.cast:
            all_actors[actor.id] = actor.model_dump()
        for episode in season.episodes:
            for actor in episode.guest_stars:
                all_actors[actor.id] = actor.model_dump()

    if all_actors:
        stmt = insert(Actor)
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['id'], set_={'name': stmt.excluded.name}
        ).returning(Actor)
        unique_actors = (await db.scalars(upsert_stmt, list(all_actors.values()))).all()
        actor_map = {actor.id: actor for actor in unique_actors}

    for season in validated_seasons:
        season_record = Season(**season.model_dump(exclude={'episodes', 'cast'}))
        season_record.cast.extend(
            Role(
                actor=actor_map[actor.id],
                character=actor.character,
                season=season_record,
            )
            for actor in season.cast
        )

        for episode in season.episodes:
            episode_record = Episode(**episode.model_dump(exclude={'guest_stars'}))
            episode_record.guest_stars.extend(
                Role(
                    actor=actor_map[actor.id],
                    character=actor.character,
                    episode=episode_record,
                )
                for actor in episode.guest_stars
            )
            season_record.episodes.append(episode_record)

        show_record.seasons.append(season_record)

    creators = [
        Creator(**creator.model_dump()) for creator in parsed_show_data.creators
    ]
    db.add_all(creators)
    show_record.creators.extend(creators)

    db.add(show_record)
    await db.commit()

    result = (await db.execute(query.execution_options(populate_existing=True))).all()

    show = result[0][0]
    show.seasons_with_progress = await parse_progress(result, 'seasons')

    return show


async def get_season(
    db: AsyncSession, user: User, season_id: int, view: str | None
) -> Season | list[dict]:
    is_logged = case((func.max(EpisodeLog.id).isnot(None), True), else_=False).label(
        'is_logged'
    )
    select_stmt = select(Episode.id, Episode.name, is_logged)
    if view == 'full':
        select_stmt = select_stmt.with_only_columns(
            Season, *select_stmt.selected_columns
        ).options(selectinload(Season.cast).selectinload(Role.actor))

    stmt = (
        select_stmt.join(Episode.season)
        .outerjoin(
            EpisodeLog,
            ((EpisodeLog.episode_id == Episode.id) & (EpisodeLog.user_id == user.id)),
        )
        .where(Season.id == season_id)
        .group_by(Episode.id, Season.id)
        .order_by(Episode.episode_number)
    )

    result = (await db.execute(stmt)).all()
    if view == 'full':
        season = result[0][0]
        season.episodes_with_progress = await parse_progress(result, 'episodes')
        return season
    else:
        episodes_with_progress = await parse_progress(result, 'episodes')
        return episodes_with_progress


async def get_episode(db: AsyncSession, user: User, episode_id: int) -> Episode:
    is_logged = case((func.max(EpisodeLog.id).isnot(None), True), else_=False).label(
        'is_logged'
    )

    stmt = (
        select(Episode, is_logged)
        .options(selectinload(Episode.guest_stars).selectinload(Role.actor))
        .outerjoin(
            EpisodeLog,
            ((EpisodeLog.episode_id == Episode.id) & (EpisodeLog.user_id == user.id)),
        )
        .where(Episode.id == episode_id)
        .group_by(Episode.id)
    )

    result = (await db.execute(stmt)).one()
    episode, is_logged = result
    episode.is_logged = is_logged
    return episode


async def search_tmdb_show(tmdb_client: TmdbClient, query: ShowSearchRequest):
    response = await tmdb_client.get('search/tv', params={'query': query.name})
    response.raise_for_status()
    results = response.json().get('results', [])[:10]

    return results


async def log_episode(
    db: AsyncSession, user: User, episode_id: int, logged_at: datetime | None
) -> EpisodeLog:
    stmt = select(Episode).where(Episode.id == episode_id)
    result = await db.execute(stmt)
    episode_in_db = result.scalar_one()
    episode_log = EpisodeLog(user=user, episode=episode_in_db, logged_at=logged_at)
    db.add(episode_log)
    await db.commit()
    episode_log.episode_name = episode_log.episode.name
    return episode_log


async def parse_progress(result, type: Literal['seasons', 'episodes']):
    if type == 'episodes':
        episodes = []
        for row in result:
            episodes.append({'id': row[-3], 'name': row[-2], 'is_logged': row[-1]})
        return episodes

    elif type == 'seasons':
        seasons = []
        for row in result:
            seasons.append(
                {
                    'id': row[1],
                    'name': row[2],
                    'logged_eps': row[3],
                    'total_eps': row[4],
                }
            )
        return seasons


async def get_tmdb_season(tmdb_client: TmdbClient, show_id: int, season_number: int):
    response = await tmdb_client.get(
        f'/tv/{show_id}/season/{season_number}?append_to_response=credits'
    )
    response.raise_for_status()
    return response.json()
