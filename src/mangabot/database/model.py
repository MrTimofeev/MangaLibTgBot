from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship, declarative_base




# Создаем базовый класс для моделей
Base = declarative_base()

# Модель для пользователя


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, index=True)

    preferred_source = Column(String, nullable=True) #источник None - все
    age_verifed = Column(Boolean, default=False)
   
    subscriptions = relationship('Subscription', back_populates='user')

# Модель для манги


class Manga(Base):
    __tablename__ = 'manga'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)  # Оригинальное название
    is_adult = Column(Boolean, default=False) # True - 18+
    # нормализованное название для поиска
    search_title = Column(String, nullable=False, index=True)
    url = Column(String, nullable=False)
    last_chapter_number = Column(String)
    last_chapter_url = Column(String)
    photo_url = Column(String)
    thumbnail_url = Column(String)
    status = Column(String) # Закончен или нет
    translate_status = Column(String) # Статус перевода
    
    source = Column(String, nullable=False, index=True)

    __table__args__ = (
        UniqueConstraint('title', 'source',
                         name='uq_manga_serch_title_source'),
    )

    chapters = relationship('Chapter', back_populates='manga')
    subscriptions = relationship('Subscription', back_populates='manga')

# Модель для главы


class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True)
    manga_id = Column(Integer, ForeignKey('manga.id'), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    chapter_url = Column(String, nullable=False)

    manga = relationship('Manga', back_populates='chapters')

# Модель для подписки


class Subscription(Base):
    __tablename__ = 'subscriptions'

    user_id = Column(Integer, ForeignKey(
        'users.telegram_id'), primary_key=True)
    manga_id = Column(Integer, ForeignKey('manga.id'), primary_key=True)
    last_notified_chapter = Column(Integer)

    user = relationship('User', back_populates='subscriptions')
    manga = relationship('Manga', back_populates='subscriptions')

