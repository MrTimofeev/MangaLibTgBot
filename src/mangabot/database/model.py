import json

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship

from mangabot.database.session import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, index=True)

    age_verifed = Column(Boolean, default=False)
    preferred_source = Column(String, nullable=True)  # источник None - все

    subscriptions = relationship('Subscription', back_populates='user')

    @property
    def sources_list(self) -> list[str] | None:
        if self.preferred_source:
            return json.loads(self.preferred_source)
        return None

    @sources_list.setter
    def sources_list(self, value: list[str] | None):
        self.preferred_source = json.dumps(
            value, ensure_ascii=False) if value is not None else None


class Manga(Base):
    __tablename__ = 'manga'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)  # Оригинальное название
    # нормализованное название для поиска
    search_title = Column(String, nullable=False, index=True)
    url = Column(String, nullable=False)
    last_chapter_number = Column(String)
    last_chapter_url = Column(String)
    photo_url = Column(String)
    thumbnail_url = Column(String)
    is_adult = Column(Boolean, default=False)  # True - 18+
    status = Column(String)  # Закончен или нет
    translate_status = Column(String)  # Статус перевода

    source = Column(String, nullable=False, index=True)

    __table__args__ = (
        UniqueConstraint('title', 'source',
                         name='uq_manga_serch_title_source'),
    )

    chapters = relationship('Chapter', back_populates='manga')
    subscriptions = relationship('Subscription', back_populates='manga')


class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True)
    manga_id = Column(Integer, ForeignKey('manga.id'), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    chapter_url = Column(String, nullable=False)

    manga = relationship('Manga', back_populates='chapters')


class Subscription(Base):
    __tablename__ = 'subscriptions'

    user_id = Column(Integer, ForeignKey(
        'users.telegram_id'), primary_key=True)
    manga_id = Column(Integer, ForeignKey('manga.id'), primary_key=True)
    last_notified_chapter = Column(Integer)

    user = relationship('User', back_populates='subscriptions')
    manga = relationship('Manga', back_populates='subscriptions')
