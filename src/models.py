from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from typing import Optional, List

db = SQLAlchemy()

class TipoEnum(Enum):
    VEHICLE = "vehicle"
    CHARACTER = "character"
    PLANET = "planet"

class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    favoritos: Mapped[List["Favorites"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }

class Favorites(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    tipo: Mapped[TipoEnum] = mapped_column(SQLAlchemyEnum(TipoEnum), nullable=False)

    
    planet_id: Mapped[Optional[int]] = mapped_column(ForeignKey('planet.id'))
    character_id: Mapped[Optional[int]] = mapped_column(ForeignKey('character.id'))
    vehicle_id: Mapped[Optional[int]] = mapped_column(ForeignKey('vehicle.id'))

    
    user: Mapped["User"] = relationship(back_populates="favoritos")
    planet: Mapped[Optional["Planet"]] = relationship("Planet")
    character: Mapped[Optional["Character"]] = relationship("Character")
    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tipo": self.tipo.value,
            "planet_id": self.planet_id,
            "character_id": self.character_id,
            "vehicle_id": self.vehicle_id
        }

class Vehicle(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100), unique=True)

    def serialize(self):
        return {
            "id": self.id,
            "model": self.model,
            "name": self.name
        }

class Character(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    genre: Mapped[str] = mapped_column(String(50))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.genre
        }

class Planet(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    clima: Mapped[str] = mapped_column(String(50))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "clima": self.clima
        }