from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList 
from sqlalchemy import PickleType
from sqlalchemy.sql import func 

db  = SQLAlchemy()
class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String())
    seeking_description = db.Column(db.String())
    website_link = db.Column(db.String())
    shows = db.relationship('Show',backref='venue',lazy='joined',cascade='all, delete')
    creation_time = db.Column(db.DateTime(timezone=True),server_default = func.now())


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = "artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.String())
    website_link = db.Column(db.String())
    shows = db.relationship('Show',backref='artist',lazy='joined',cascade='all, delete')
    creation_time = db.Column(db.DateTime(timezone=True),server_default = func.now())
    available_times = db.Column(MutableList.as_mutable(db.PickleType),default=[])

class Show(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'))
  venue_id  = db.Column(db.Integer,db.ForeignKey('venue.id'))
  start_time = db.Column(db.DateTime(timezone=True))
  