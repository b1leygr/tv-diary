from asyncio import gather
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import TmdbClient
from app.shows.models import (
    Actor,
    Creator,
    CreatorCredit,
    Episode,
    Role,
    Season,
    Show,
)
from app.shows.schemas import (
    SeasonCreate,
    ShowCreate,
    ShowSearchRequest,
)


async def get_show(db: AsyncSession, tmdb_client: TmdbClient, show_id: int) -> Show:
    query = (
        select(Show)
        .where(Show.id == show_id)
        .options(
            selectinload(Show.show_creators).selectinload(CreatorCredit.creator),
            selectinload(Show.seasons)
            .selectinload(Season.cast)
            .selectinload(Role.actor),
            selectinload(Show.seasons)
            .selectinload(Season.episodes)
            .selectinload(Episode.guest_stars)
            .selectinload(Role.actor),
        )
    )
    result = await db.execute(query)
    cached_show = result.scalar_one_or_none()

    if (
        cached_show
        and cached_show.last_updated.timestamp()
        > (datetime.now() - timedelta(days=7)).timestamp()
    ):
        return cached_show

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
    show = (await db.execute(query)).scalar_one()
    return show


async def get_season(
    db: AsyncSession, show_id: int, season_number: int
) -> Season | None:
    stmt = (
        select(Season)
        .options(
            selectinload(Season.cast).selectinload(Role.actor),
            selectinload(Season.episodes)
            .selectinload(Episode.guest_stars)
            .selectinload(Role.actor),
        )
        .join(Season.show)
        .where(Season.show_id == show_id)
        .where(Season.season_number == season_number)
    )
    season = (await db.execute(stmt)).scalar_one_or_none()
    return season or None


async def get_episode(
    db: AsyncSession, show_id: int, season_number: int, episode_number: int
) -> Episode | None:
    stmt = (
        select(Episode)
        .options(selectinload(Episode.guest_stars).selectinload(Role.actor))
        .join(Episode.season)
        .where(Season.show_id == show_id)
        .where(Season.season_number == season_number)
        .where(Episode.episode_number == episode_number)
    )
    episode = (await db.execute(stmt)).scalar_one_or_none()
    return episode or None


async def search_tmdb_show(tmdb_client: TmdbClient, query: ShowSearchRequest):
    response = await tmdb_client.get('search/tv', params={'query': query.name})
    response.raise_for_status()
    results = response.json().get('results', [])[:10]

    return results


async def get_tmdb_season(tmdb_client: TmdbClient, show_id: int, season_number: int):
    response = await tmdb_client.get(
        f'/tv/{show_id}/season/{season_number}?append_to_response=credits'
    )
    response.raise_for_status()
    return response.json()
