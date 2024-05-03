from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

user_rooms = db.Table("user_rooms",
                      db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
                      db.Column("room_id", db.Integer, db.ForeignKey("rooms.id"), primary_key=True))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    image = db.Column(db.String)
    image_mimetype = db.Column(db.String)
    messages = db.relationship("Message", back_populates="sender")
    rooms = db.relationship("Room", secondary=user_rooms, back_populates="participants")
    advertisements = db.relationship("Advertisement", back_populates="owner")
    favoriteAdvertisements = db.relationship("FavoriteAdvertisement", back_populates="owner")


class Advertisement(db.Model):
    __tablename__ = "advertisement"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    brand = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String, nullable=False)
    data = db.Column(db.String, nullable=False)
    image_name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    image_mimetype = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    verified = db.Column(db.Integer, nullable=False)
    blocked = db.Column(db.Integer, nullable=False)
    number = db.Column(db.Integer, nullable=False)

    owner = db.relationship("User", back_populates="advertisements")
    favoriteAdvertisements = db.relationship("FavoriteAdvertisement", back_populates="advertisement")


class FavoriteAdvertisement(db.Model):
    __tablename__ = "favoriteAdvertisements"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    advertisement_id = db.Column(db.Integer, db.ForeignKey("advertisement.id"))
    owner = db.relationship("User", back_populates="favoriteAdvertisements")
    advertisement = db.relationship("Advertisement", back_populates="favoriteAdvertisements")


class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    messages = db.relationship("Message", back_populates="room")
    participants = db.relationship("User", secondary=user_rooms, back_populates="rooms")


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"))
    text = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    room = db.relationship("Room", back_populates="messages")
    sender = db.relationship("User", back_populates="messages")


class ContactMessage(db.Model):
    __tablename__ = "contactMessages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
