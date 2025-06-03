from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    user_name: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    fav_char: Mapped[list['Favorites_Characters']] = relationship(
        back_populates='user', cascade='all, delete-orphan')
    fav_planet: Mapped[list['Favorites_Planets']] = relationship(
        back_populates='user', cascade='all, delete-orphan')
    fav_film: Mapped[list['Favorites_Films']] = relationship(
        back_populates='user', cascade='all, delete-orphan')


class Character(db.Model):
    __tablename__ = 'character'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    birth_year: Mapped[str] = mapped_column(String(10), )
    gender: Mapped[str] = mapped_column(String(10), )
    height_mts: Mapped[int] = mapped_column(Integer, )
    weigth_kg: Mapped[int] = mapped_column(Integer, )
    skin_tone: Mapped[str] = mapped_column(String(20), )
    eye_color: Mapped[str] = mapped_column(String(20), )
    hair_color: Mapped[str] = mapped_column(String(20), )
    favorite_by: Mapped[list['Favorites_Characters']] = relationship(
        back_populates='character', cascade='all, delete-orphan')
    home_planet: Mapped[list['Natives_Planets']] = relationship(
        back_populates='character', cascade='all, delete-orphan')
    appearance: Mapped[list['Appearance_Characters']] = relationship(
        back_populates='character', cascade='all, delete-orphan')


class Planet(db.Model):
    __tablename__ = 'planet'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    climate: Mapped[str] = mapped_column(String(20), )
    terrain: Mapped[str] = mapped_column(String(20), )
    population_count: Mapped[int] = mapped_column(Integer, )
    gravity: Mapped[str] = mapped_column(String, )
    diameter: Mapped[int] = mapped_column(Integer, )
    water_surface: Mapped[int] = mapped_column(Integer, )
    orvital_period: Mapped[int] = mapped_column(Integer, )
    rotation_period: Mapped[int] = mapped_column(Integer, )
    favorite_by: Mapped[list['Favorites_Planets']] = relationship(
        back_populates='planet', cascade='all, delete-orphan')
    natives: Mapped[list['Natives_Planets']] = relationship(
        back_populates='planet', cascade='all, delete-orphan')
    appearance: Mapped[list['Appearance_Planets']] = relationship(
        back_populates='planet', cascade='all, delete-orphan')


class Film(db.Model):
    __tablename__ = 'film'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    episode: Mapped[str] = mapped_column(String(10), )
    director: Mapped[str] = mapped_column(String(20), )
    producer: Mapped[str] = mapped_column(String(20), )
    release_date: Mapped[int] = mapped_column(Date, )
    opening_crawl: Mapped[str] = mapped_column(Text, )
    favorite_by: Mapped[list['Favorites_Films']] = relationship(
        back_populates='film', cascade='all, delete-orphan')
    feature_char: Mapped[list['Appearance_Characters']] = relationship(
        back_populates='film', cascade='all, delete-orphan')
    feature_planet: Mapped[list['Appearance_Planets']] = relationship(
        back_populates='film', cascade='all, delete-orphan')


# favorites
class Favorites_Characters(db.Model):
    __tablename__ = 'favorite_characters'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    user: Mapped[User] = relationship(back_populates='fav_char')
    character_id: Mapped[int] = mapped_column(
        ForeignKey('character.id'), nullable=False)
    character: Mapped[Character] = relationship(back_populates='favorite_by')


class Favorites_Planets(db.Model):
    __tablename__ = 'favorite_planets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    user: Mapped[User] = relationship(back_populates='fav_planet')
    planet_id: Mapped[int] = mapped_column(
        ForeignKey('planet.id'), nullable=False)
    planet: Mapped[Planet] = relationship(back_populates='favorite_by')


class Favorites_Films(db.Model):
    __tablename__ = 'favorite_films'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    user: Mapped[User] = relationship(back_populates='fav_film')
    film_id: Mapped[int] = mapped_column(ForeignKey('film.id'), nullable=False)
    film: Mapped[Film] = relationship(back_populates='favorite_by')

# Natives


class Natives_Planets(db.Model):
    __tablename__ = 'natives_planets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey('character.id'), nullable=False)
    character: Mapped[Character] = relationship(back_populates='home_planet')
    planet_id: Mapped[int] = mapped_column(
        ForeignKey('planet.id'), nullable=False)
    planet: Mapped[Planet] = relationship(back_populates='natives')


# Appearances
class Appearance_Characters(db.Model):
    __tablename__ = 'appearance_characters'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey('character.id'), nullable=False)
    character: Mapped[Character] = relationship(back_populates='apperance')
    film_id: Mapped[int] = mapped_column(ForeignKey('film.id'), nullable=False)
    film: Mapped[Film] = relationship(back_populates='feature_char')


class Appearance_Planets(db.Model):
    __tablename__ = 'appearance_planets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey('planet.id'), nullable=False)
    planet: Mapped[Character] = relationship(back_populates='apperance')
    film_id: Mapped[int] = mapped_column(ForeignKey('film.id'), nullable=False)
    film: Mapped[Film] = relationship(back_populates='feature_planet')
