from asyncio import gather
from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import Integer, case, func, literal_column, select, union_all
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, aliased, load_only, selectinload

from app.core.dependencies import TmdbClient
from app.tv.exceptions import (
    EpisodeNotFound,
    SeasonNotFound,
    ShowNotFound,
    TmdbClientError,
)
from app.tv.models import (
    ActivityLog,
    Actor,
    Creator,
    CreatorCredit,
    Episode,
    LogType,
    Role,
    Season,
    Show,
)
from app.tv.schemas import (
    ActivityLogRequest,
    SeasonCreate,
    ShowCreate,
    ShowSearchRequest,
)
from app.users.models import User


async def get_show(
    db: AsyncSession, user: User, tmdb_client: TmdbClient, show_id: int
) -> Show:
    eps_per_season = func.count(Episode.id.distinct()).label('eps_per_season')

    show_log = aliased(ActivityLog)
    show_log_exists = (
        select(literal_column('1'))
        .where(
            show_log.user_id == user.id,
            show_log.log_type == LogType.SHOW,
            show_log.show_id == Show.id,
        )
        .correlate(Show)
        .exists()
    )

    season_log = aliased(ActivityLog)
    season_log_exists = (
        select(literal_column('1'))
        .where(
            season_log.user_id == user.id,
            season_log.log_type == LogType.SEASON,
            season_log.season_id == Season.id,
        )
        .correlate(Season)
        .exists()
    )

    episode_log = aliased(ActivityLog)
    episodes_logged = (
        select(func.count(episode_log.id))
        .join(Episode, episode_log.episode_id == Episode.id)
        .where(
            episode_log.user_id == user.id,
            episode_log.log_type == LogType.EPISODE,
            Episode.season_id == Season.id,
        )
        .correlate(Season)
        .scalar_subquery()
    )

    logged_eps_per_season = case(
        (show_log_exists, eps_per_season),
        (season_log_exists, eps_per_season),
        else_=episodes_logged,
    ).label('logged_eps_per_season')

    query = (
        select(Show, Season.id, Season.name, logged_eps_per_season, eps_per_season)
        .options(selectinload(Show.show_creators).selectinload(CreatorCredit.creator))
        .join(Show.seasons)
        .join(Season.episodes)
        .where(Season.show_id == show_id)
        .group_by(Show.id, Season.id)
        .order_by(Show.name, *(await sort_collection(Season.name)))
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
    await resolve_tmdb_response(response, type='show')
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

    creators = {
        creator.id: creator.model_dump() for creator in parsed_show_data.creators
    }

    if creators:
        stmt = insert(Creator)
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['id'], set_={'name': stmt.excluded.name}
        ).returning(Creator)
        unique_creators = (await db.scalars(upsert_stmt, list(creators.values()))).all()
        creator_map = {creator.id: creator for creator in unique_creators}

    show_record.show_creators.extend(
        CreatorCredit(creator=creator_map[creator.id])
        for creator in parsed_show_data.creators
    )

    db.add(show_record)
    await db.commit()

    result = (await db.execute(query.execution_options(populate_existing=True))).all()

    show = result[0][0]
    show.seasons_with_progress = await parse_progress(result, 'seasons')

    return show


async def get_season(
    db: AsyncSession, user: User, season_id: int, view: str | None
) -> Season | list[dict]:
    episode_log = aliased(ActivityLog)
    season_log = aliased(ActivityLog)
    show_log = aliased(ActivityLog)

    episode_log_exists = (
        select(literal_column('1'))
        .where(
            episode_log.user_id == user.id,
            episode_log.log_type == LogType.EPISODE,
            episode_log.episode_id == Episode.id,
        )
        .correlate(Episode)
        .exists()
    )

    season_log_exists = (
        select(literal_column('1'))
        .where(
            season_log.user_id == user.id,
            season_log.log_type == LogType.SEASON,
            season_log.season_id == Season.id,
        )
        .correlate(Season)
        .exists()
    )

    show_log_exists = (
        select(literal_column('1'))
        .where(
            show_log.user_id == user.id,
            show_log.log_type == LogType.SHOW,
            show_log.show_id == Show.id,
        )
        .correlate(Show)
        .exists()
    )

    is_logged = case(
        (episode_log_exists, True),
        (season_log_exists, True),
        (show_log_exists, True),
        else_=False,
    ).label('is_logged')

    select_stmt = select(Episode.id, Episode.name, is_logged)
    group_target: tuple[InstrumentedAttribute, ...] = Episode.id, Season.id

    if view == 'full':
        select_stmt = (
            select_stmt.with_only_columns(
                Season,
                Show.name.label('show_name'),
                Show.backdrop_path.label('show_backdrop_path'),
                *select_stmt.selected_columns,
            )
            .options(selectinload(Season.cast).selectinload(Role.actor))
            .join(Show, Show.id == Season.show_id)
            .join(Episode, Episode.season_id == Season.id)
        )
        group_target = (*group_target, Show.id, Show.name, Show.backdrop_path)
    elif view == 'progress':
        select_stmt = select_stmt.join(Episode.season)

    stmt = (
        select_stmt.where(Season.id == season_id)
        .group_by(*group_target)
        .order_by(Episode.episode_number)
    )

    result = (await db.execute(stmt)).all()

    if not result:
        raise SeasonNotFound(season_id=season_id)

    if view == 'full':
        season = result[0][0]
        season.show_name = result[0][1]
        season.show_backdrop_path = result[0][2]
        season.episodes_with_progress = await parse_progress(result, 'episodes')
        return season
    else:
        episodes_with_progress = await parse_progress(result, 'episodes')
        return episodes_with_progress


async def get_episode(db: AsyncSession, user: User, episode_id: int) -> Episode:
    episode_log = aliased(ActivityLog)
    season_log = aliased(ActivityLog)
    show_log = aliased(ActivityLog)

    episode_log_exists = (
        select(literal_column('1'))
        .where(
            episode_log.user_id == user.id,
            episode_log.log_type == LogType.EPISODE,
            episode_log.episode_id == Episode.id,
        )
        .correlate(Episode)
        .exists()
    )

    season_log_exists = (
        select(literal_column('1'))
        .where(
            season_log.user_id == user.id,
            season_log.log_type == LogType.SEASON,
            season_log.season_id == Season.id,
        )
        .correlate(Season)
        .exists()
    )

    show_log_exists = (
        select(literal_column('1'))
        .where(
            show_log.user_id == user.id,
            show_log.log_type == LogType.SHOW,
            show_log.show_id == Show.id,
        )
        .correlate(Show)
        .exists()
    )

    is_logged = case(
        (episode_log_exists, True),
        (season_log_exists, True),
        (show_log_exists, True),
        else_=False,
    ).label('is_logged')

    stmt = (
        select(
            Episode,
            Season.name.label('season_name'),
            Season.poster_path.label('season_poster_path'),
            Show.id.label('show_id'),
            Show.name.label('show_name'),
            is_logged,
        )
        .join(Season, Season.id == Episode.season_id)
        .join(Show, Show.id == Season.show_id)
        .options(selectinload(Episode.guest_stars).selectinload(Role.actor))
        .where(Episode.id == episode_id)
        .group_by(
            Episode.id,
            Season.id,
            Season.name,
            Season.poster_path,
            Show.id,
            Show.name,
        )
    )

    try:
        result = (await db.execute(stmt)).one()
    except NoResultFound:
        raise EpisodeNotFound(episode_id=episode_id)

    episode, *attrs = result
    await update_object(
        episode,
        [
            'season_name',
            'season_poster_path',
            'show_id',
            'show_name',
            'is_logged',
        ],
        attrs,
    )
    return episode


async def search_tmdb_show(tmdb_client: TmdbClient, query: ShowSearchRequest):
    response = await tmdb_client.get('search/tv', params={'query': query.name})
    await resolve_tmdb_response(response, type='show')
    results = response.json().get('results', [])[:10]

    return results


async def log_activity(
    db: AsyncSession,
    user: User,
    log_request: ActivityLogRequest,
) -> ActivityLog:
    if log_request.episode_id:
        log_type = LogType.EPISODE
        try:
            episode_in_db = (
                await db.execute(
                    select(Episode).where(Episode.id == log_request.episode_id)
                )
            ).scalar_one()
        except NoResultFound:
            raise EpisodeNotFound(episode_id=log_request.episode_id)
    elif log_request.season_id:
        log_type = LogType.SEASON
        season_in_db = (
            (
                await db.execute(
                    select(Season)
                    .options(
                        selectinload(Season.episodes).options(load_only(Episode.id))
                    )
                    .where(Season.id == log_request.season_id)
                )
            )
            .scalars()
            .first()
        )
        if not season_in_db:
            raise SeasonNotFound(season_id=log_request.season_id)
        episode_ids = [episode.id for episode in season_in_db.episodes]
    elif log_request.show_id:
        log_type = LogType.SHOW
        show_in_db = (
            (
                await db.execute(
                    select(Show)
                    .options(
                        selectinload(Show.seasons).options(load_only(Season.id)),
                        selectinload(Show.seasons)
                        .selectinload(Season.episodes)
                        .options(load_only(Episode.id)),
                    )
                    .where(Show.id == log_request.show_id),
                )
            )
            .scalars()
            .first()
        )
        if not show_in_db:
            raise ShowNotFound(show_id=log_request.show_id)
        season_ids = [season.id for season in show_in_db.seasons]
        episode_ids = [
            episode.id for season in show_in_db.seasons for episode in season.episodes
        ]

    activity_log = ActivityLog(
        user=user,
        episode=episode_in_db if log_request.episode_id else None,
        season=season_in_db if log_request.season_id else None,
        show=show_in_db if log_request.show_id else None,
        logged_at=log_request.logged_at,
        log_type=log_type,
    )
    db.add(activity_log)
    await db.commit()

    if log_type == LogType.EPISODE:
        activity_log.episode_name = episode_in_db.name
    elif log_type == LogType.SEASON and season_in_db:
        activity_log.season_name = season_in_db.name
        activity_log.mutated_episodes = episode_ids
    elif log_type == LogType.SHOW and show_in_db:
        activity_log.show_name = show_in_db.name
        activity_log.mutated_seasons = season_ids
        activity_log.mutated_episodes = episode_ids
    return activity_log


async def get_activity(
    db: AsyncSession, user: User, view: Literal['episodes', 'seasons', 'shows'] | None
):
    if view == 'episodes':
        return await get_episode_logs(db, user)
    elif view == 'seasons':
        return await get_season_logs(db, user)
    elif view == 'shows':
        return await get_show_logs(db, user)
    else:
        raise ValueError(
            "Invalid view type. Must be 'episodes', 'seasons', or 'shows'."
        )


async def get_episode_logs(db: AsyncSession, user: User):
    episodes_logged = (
        select(
            ActivityLog.logged_at.label('logged_at'),
            Episode.id.label('episode_id'),
            Episode.name.label('episode_name'),
            Episode.episode_number.label('episode_number'),
            Season.id.label('season_id'),
            Season.name.label('season_name'),
            Show.id.label('show_id'),
            Show.name.label('show_name'),
            Show.poster_path.label('show_poster_path'),
        )
        .join(Episode, ActivityLog.episode_id == Episode.id)
        .join(Season, Season.id == Episode.season_id)
        .join(Show, Show.id == Season.show_id)
        .where(ActivityLog.user_id == user.id, ActivityLog.log_type == LogType.EPISODE)
    )

    seasons_logged_as_episodes = (
        select(
            ActivityLog.logged_at.label('logged_at'),
            Episode.id.label('episode_id'),
            Episode.name.label('episode_name'),
            Episode.episode_number.label('episode_number'),
            Season.id.label('season_id'),
            Season.name.label('season_name'),
            Show.id.label('show_id'),
            Show.name.label('show_name'),
            Show.poster_path.label('show_poster_path'),
        )
        .join(Season, ActivityLog.season_id == Season.id)
        .join(Episode, Episode.season_id == Season.id)
        .join(Show, Show.id == Season.show_id)
        .where(ActivityLog.user_id == user.id, ActivityLog.log_type == LogType.SEASON)
    )

    shows_logged_as_episodes = (
        select(
            ActivityLog.logged_at.label('logged_at'),
            Episode.id.label('episode_id'),
            Episode.name.label('episode_name'),
            Episode.episode_number.label('episode_number'),
            Season.id.label('season_id'),
            Season.name.label('season_name'),
            Show.id.label('show_id'),
            Show.name.label('show_name'),
            Show.poster_path.label('show_poster_path'),
        )
        .join(Show, ActivityLog.show_id == Show.id)
        .join(Season, Season.show_id == Show.id)
        .join(Episode, Episode.season_id == Season.id)
        .where(ActivityLog.user_id == user.id, ActivityLog.log_type == LogType.SHOW)
    )

    union_stmt = (
        union_all(episodes_logged, seasons_logged_as_episodes, shows_logged_as_episodes)
    ).subquery()

    stmt = (
        select(union_stmt)
        .order_by(
            union_stmt.c.logged_at.desc(),
            union_stmt.c.episode_number.desc(),
        )
        .limit(100)
    )

    results = (await db.execute(stmt)).all()
    return results


async def get_season_logs(db: AsyncSession, user: User):
    episodes_logged_as_seasons = (
        select(
            ActivityLog.logged_at.label('logged_at'),
            Season.id.label('season_id'),
            Season.name.label('season_name'),
            Show.id.label('show_id'),
            Show.name.label('show_name'),
            Show.poster_path.label('show_poster_path'),
        )
        .join(Episode, ActivityLog.episode_id == Episode.id)
        .join(Season, Episode.season_id == Season.id)
        .join(Show, Show.id == Season.show_id)
        .where(ActivityLog.user_id == user.id, ActivityLog.log_type == LogType.EPISODE)
    )

    seasons_logged = (
        select(
            ActivityLog.logged_at.label('logged_at'),
            Season.id.label('season_id'),
            Season.name.label('season_name'),
            Show.id.label('show_id'),
            Show.name.label('show_name'),
            Show.poster_path.label('show_poster_path'),
        )
        .join(Season, ActivityLog.season_id == Season.id)
        .join(Show, Show.id == Season.show_id)
        .where(ActivityLog.user_id == user.id, ActivityLog.log_type == LogType.SEASON)
    )

    shows_logged_as_seasons = (
        select(
            ActivityLog.logged_at.label('logged_at'),
            Season.id.label('season_id'),
            Season.name.label('season_name'),
            Show.id.label('show_id'),
            Show.name.label('show_name'),
            Show.poster_path.label('show_poster_path'),
        )
        .join(Show, ActivityLog.show_id == Show.id)
        .join(Season, Season.show_id == Show.id)
        .where(ActivityLog.user_id == user.id, ActivityLog.log_type == LogType.SHOW)
    )

    union_stmt = (
        union_all(seasons_logged, episodes_logged_as_seasons, shows_logged_as_seasons)
    ).subquery()

    most_recent_stmt = (
        select(
            union_stmt.c.logged_at,
            union_stmt.c.season_id,
            union_stmt.c.season_name,
            union_stmt.c.show_id,
            union_stmt.c.show_name,
            union_stmt.c.show_poster_path,
            func.row_number()
            .over(
                partition_by=union_stmt.c.season_id,
                order_by=union_stmt.c.logged_at.desc(),
            )
            .label('row_num'),
        )
    ).subquery()

    stmt = (
        select(most_recent_stmt)
        .where(most_recent_stmt.c.row_num == 1)
        .order_by(
            most_recent_stmt.c.logged_at.desc(),
            *(await sort_collection(most_recent_stmt.c.season_name)),
        )
        .limit(100)
    )

    results = (await db.execute(stmt)).all()
    return results


async def get_show_logs(db: AsyncSession, user: User):
    episode_log = aliased(Episode)
    season_for_episode_log = aliased(Season)
    show_for_episode_log = aliased(Show)

    season_log = aliased(Season)
    show_for_season_log = aliased(Show)

    show_log = aliased(Show)

    show_id_case = case(
        (ActivityLog.log_type == LogType.SHOW, show_log.id),
        (ActivityLog.log_type == LogType.SEASON, show_for_season_log.id),
        (ActivityLog.log_type == LogType.EPISODE, show_for_episode_log.id),
    )

    subquery = (
        select(
            ActivityLog.logged_at.label('logged_at'),
            show_id_case.label('show_id'),
            case(
                (ActivityLog.log_type == LogType.SHOW, show_log.name),
                (ActivityLog.log_type == LogType.SEASON, show_for_season_log.name),
                (ActivityLog.log_type == LogType.EPISODE, show_for_episode_log.name),
            ).label('show_name'),
            case(
                (ActivityLog.log_type == LogType.SHOW, show_log.poster_path),
                (
                    ActivityLog.log_type == LogType.SEASON,
                    show_for_season_log.poster_path,
                ),
                (
                    ActivityLog.log_type == LogType.EPISODE,
                    show_for_episode_log.poster_path,
                ),
                else_=None,
            ).label('show_poster_path'),
            func.row_number()
            .over(
                partition_by=show_id_case,
                order_by=ActivityLog.logged_at.desc(),
            )
            .label('row_num'),
        )
        .outerjoin(show_log, ActivityLog.show_id == show_log.id)
        .outerjoin(season_log, ActivityLog.season_id == season_log.id)
        .outerjoin(show_for_season_log, season_log.show_id == show_for_season_log.id)
        .outerjoin(episode_log, ActivityLog.episode_id == episode_log.id)
        .outerjoin(
            season_for_episode_log, episode_log.season_id == season_for_episode_log.id
        )
        .outerjoin(
            show_for_episode_log,
            season_for_episode_log.show_id == show_for_episode_log.id,
        )
        .where(ActivityLog.user_id == user.id)
    ).subquery()

    stmt = (
        select(subquery)
        .where(literal_column('row_num') == 1)
        .order_by(literal_column('logged_at').desc())
        .limit(100)
    )

    results = (await db.execute(stmt)).all()
    return results


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
    await resolve_tmdb_response(response)
    return response.json()


async def update_object(object, keys: list[str], attrs: list):
    for key, val in zip(keys, attrs, strict=True):
        setattr(object, key, val)


async def resolve_tmdb_response(
    response, type: Literal['show', 'season'] | None = None
):
    if response.status_code == 404:
        if type == 'show':
            raise ShowNotFound(show_id=response.url.path.split('/')[-1])
        elif type == 'season':
            raise SeasonNotFound(season_id=response.url.path.split('/')[-1])
    elif response.status_code in [500, 502]:
        raise TmdbClientError(
            status_code=502,
            message="The TMDB API encountered an error and could not fulfill the request.",
        )
    elif response.status_code == 503:
        raise TmdbClientError(
            status_code=503,
            message="The TMDB API is currently unavailable. Please try again later.",
        )
    elif response.status_code == 504:
        raise TmdbClientError(
            status_code=504,
            message="The TMDB API request timed out. Please try again later.",
        )


async def sort_collection(column):
    prefix = func.regexp_replace(column, r'(\d+$)', '')
    digits = func.substring(column, r'(\d+)$')
    ends_with_digits = column.op('~')(r'\d+$')

    return [
        prefix,
        case(
            (ends_with_digits, func.cast(digits, Integer)),
            else_=0,
        ),
        column,
    ]
