from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.users.models import User


class Show(Base):
    __tablename__ = 'shows'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    status: Mapped[str | None]
    overview: Mapped[str | None]
    genres: Mapped[list[str]] = mapped_column(ARRAY(String))
    first_air_date: Mapped[date | None]
    last_air_date: Mapped[date | None]
    vote_average: Mapped[float | None]
    show_creators: Mapped[list['CreatorCredit']] = relationship(
        back_populates='show', lazy='raise'
    )
    creators: AssociationProxy[list['Creator']] = association_proxy(
        target_collection='show_creators',
        attr='creator',
        creator=lambda creator_obj: CreatorCredit(creator=creator_obj),
    )
    poster_path: Mapped[str | None]
    backdrop_path: Mapped[str | None]
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    seasons: Mapped[list['Season']] = relationship(
        back_populates='show', cascade='all, delete-orphan', lazy='raise'
    )


class Season(Base):
    __tablename__ = 'seasons'

    id: Mapped[int] = mapped_column(primary_key=True)
    show_id: Mapped[int] = mapped_column(ForeignKey('shows.id', ondelete='CASCADE'))
    name: Mapped[str]
    season_number: Mapped[int]
    overview: Mapped[str | None]
    air_date: Mapped[date | None]
    vote_average: Mapped[float | None]
    cast: Mapped[list['Role']] = relationship(
        back_populates='season', cascade='all, delete-orphan', lazy='raise'
    )
    poster_path: Mapped[str | None]

    show: Mapped['Show'] = relationship(back_populates='seasons')
    episodes: Mapped[list['Episode']] = relationship(
        back_populates='season', cascade='all, delete-orphan', lazy='raise'
    )

    __table_args__ = (
        UniqueConstraint("show_id", "season_number", name="uq_show_season_number"),
    )


class Episode(Base):
    __tablename__ = 'episodes'

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey('seasons.id', ondelete='CASCADE'))
    name: Mapped[str]
    episode_number: Mapped[int]
    overview: Mapped[str | None]
    runtime: Mapped[int | None]
    air_date: Mapped[date | None]
    vote_average: Mapped[float | None]
    guest_stars: Mapped[list['Role']] = relationship(
        back_populates='episode', cascade='all, delete-orphan', lazy='raise'
    )
    still_path: Mapped[str | None]

    season: Mapped['Season'] = relationship(back_populates='episodes')

    __table_args__ = (
        UniqueConstraint(
            "season_id", "episode_number", name="uq_season_episode_number"
        ),
    )


class EpisodeLog(Base):
    __tablename__ = 'episode_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    episode_id: Mapped[int] = mapped_column(ForeignKey('episodes.id'))
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    episode: Mapped['Episode'] = relationship()
    user: Mapped['User'] = relationship()


class Actor(Base):
    __tablename__ = 'actors'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    profile_path: Mapped[str | None]
    roles: Mapped[list['Role']] = relationship(back_populates='actor', lazy='raise')


class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped['Actor'] = mapped_column(
        ForeignKey('actors.id', ondelete='CASCADE')
    )
    character: Mapped[str | None]
    season_id: Mapped[int | None] = mapped_column(
        ForeignKey('seasons.id', ondelete='CASCADE')
    )
    episode_id: Mapped[int | None] = mapped_column(
        ForeignKey('episodes.id', ondelete='CASCADE')
    )
    actor: Mapped['Actor'] = relationship()
    season: Mapped['Season | None'] = relationship(back_populates='cast')
    episode: Mapped['Episode | None'] = relationship(back_populates='guest_stars')

    __tableargs__ = CheckConstraint(
        "(season_id IS NOT NULL AND episode_id IS NULL) OR (season_id IS NULL AND episode_id IS NOT NULL)",
        name="check_season_or_episode_not_null",
    )


class Creator(Base):
    __tablename__ = 'creators'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    profile_path: Mapped[str | None]
    creator_shows: Mapped[list['CreatorCredit']] = relationship(
        back_populates='creator', lazy='raise'
    )
    shows: AssociationProxy[list['Creator']] = association_proxy(
        target_collection='creator_shows', attr='show'
    )


class CreatorCredit(Base):
    __tablename__ = 'creator_credits'
    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey('creators.id'))
    show_id: Mapped[int] = mapped_column(ForeignKey('shows.id'))
    creator: Mapped['Creator'] = relationship(back_populates='creator_shows')
    show: Mapped['Show'] = relationship(back_populates='show_creators')
