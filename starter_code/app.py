#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.ext.mutable import MutableList 
from sqlalchemy import PickleType
from sqlalchemy.sql import func 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://augustine:bahdman@localhost:5432/project1'
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
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
    upcoming_shows_count = db.Column(db.Integer)
    past_shows = db.Column(MutableList.as_mutable(db.PickleType), default=[])
    past_shows_count = db.Column(db.Integer)
    upcoming_shows = db.Column(MutableList.as_mutable(db.PickleType), default=[])
    shows = db.relationship('Show',backref='venue',lazy=True)
    creation_time = db.Column(db.DateTime(timezone=True),server_default = func.now())


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = "artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.String())
    website_link = db.Column(db.String())
    upcoming_shows_count = db.Column(db.Integer)
    upcoming_shows = db.Column(MutableList.as_mutable(db.PickleType), default=[])
    past_shows = db.Column(MutableList.as_mutable(db.PickleType),default=[])
    past_shows_count = db.Column(db.Integer)
    shows = db.relationship('Show',backref='artist',lazy=True)
    creation_time = db.Column(db.DateTime(timezone=True),server_default = func.now())

class Show(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'))
  venue_id  = db.Column(db.Integer,db.ForeignKey('venue.id'))
  start_time = db.Column(db.Date)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value,str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recent_venues = Venue.query.order_by(Venue.creation_time).limit(5).all()
  recent_artists = Artist.query.order_by(Artist.creation_time).limit(5).all()
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = Venue.query.all()
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get("search_term")
  if ',' in search_term:
    search_term = search_term.replace(' ','').split(',')
    city = search_term[0]
    state = search_term[1] 
    result = Venue.query.filter(Venue.city.ilike(f'%{city}%'),Venue.state.ilike(f'%{state}%')).all()
    
  else:
    result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  counter = len(result)
  response={
    "count": counter,
    "data" : result,
  }
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  query = Show.query.filter_by(venue_id = venue_id).all()
  instance = Venue.query.get(venue_id)
  current_data = []
  past_data = []
  for result in query:
    if result.start_time >= datetime.now().date():
      info = {
        'artist_id':result.artist_id,
        'artist_name':result.artist.name,
        'start_time':result.start_time,
        'artist_image_link':result.artist.image_link
      }
      current_data.append(info)
    else:
      info = {
        'artist_id':result.artist_id,
        'artist_name':result.artist.name,
        'start_time':result.start_time,
        'artist_image_link':result.artist.image_link
      }
      past_data.append(info)
  instance.upcoming_shows = current_data
  instance.past_shows = past_data
  instance.past_shows_count = len(past_data)
  instance.upcoming_shows_count = len(current_data)
  data = Venue.query.filter_by(id=venue_id).all()[0]
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue_instance = Venue()
  venue_instance.name = request.form.get('name')
  venue_instance.city = request.form.get('city')
  venue_instance.state = request.form.get('state')
  venue_instance.address = request.form.get('address')
  venue_instance.phone = request.form.get('phone')
  venue_instance.facebook_link = request.form.get('facebook_link')
  venue_instance.image_link = request.form.get('image_link')
  venue_instance.website_link = request.form.get('website_link')
  venue_instance.seeking_talent = request.form.get('seeking_talent')
  venue_instance.seeking_description = request.form.get('seeking_description')

  try:
    db.session.add(venue_instance)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  to_delete= Venue.query.get(venue_id)
  try:
    db.session.delete(to_delete)
    db.session.commit()
    flash(f'Succesfully deleted {to_delete.name}')
  except:
    db.session.rollback()
  finally:
    db.session.close()
 
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  term = request.form.get('search_term')
  if ',' in term :
    term = term.replace(' ','').split(',')
    city = term[0]
    state = term[1] 
    result = Artist.query.filter(Artist.city.ilike(f'%{city}%'),Artist.state.ilike(f'%{state}%')).all()
  else:
    result = Artist.query.filter(Artist.name.ilike(f'%{term}%')).all()
  counter = len(result)
  response={
    "count": counter,
    "data": result 
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.filter_by(id=artist_id)[0]
  query = Show.query.filter_by(artist_id=artist_id).all()
  current_data = []
  past_data = []
  for result in query:
    if result.start_time >= datetime.now().date():
      info = {
        'venue_id':result.venue_id,
        'venue_name':result.venue.name,
        'start_time':result.start_time,
        'venue_image_link':result.venue.image_link
      }
      current_data.append(info)
    else:
      info = {
        'venue_id':result.venue_id,
        'venue_name':result.venue.name,
        'start_time':result.start_time,
        'venue_image_link':result.venue.image_link
      }
      past_data.append(info)
  data.upcoming_shows = current_data
  data.upcoming_shows_count = len(current_data)
  data.past_shows = past_data 
  data.past_shows_count = len(past_data)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id = artist_id)[0]
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  info = Artist.query.get(artist_id)
  info.name = request.form.get('name')
  info.city = request.form.get('city','')
  info.state = request.form.get('state','')
  info.address = request.form.get('address','')
  info.phone = request.form.get('phone','')
  info.facebook_link = request.form.get('facebook_link','')
  info.image_link = request.form.get('image_link','')
  info.website_link = request.form.get('website_link','')
  info.seeking_venue = request.form.get('seeking_venue','')
  info.seeking_description = request.form.get('seeking_description',' ')

  try:
    db.session.commit()
    flash('Edit was successful')
  except:
    db.session.rollback()
    return "There was an error"
  finally:
    db.session.close()

  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  data = Venue.query.get(venue_id)
  data.name = request.form.get('name')
  data.city = request.form.get('city','')
  data.state = request.form.get('state','')
  data.address = request.form.get('address','')
  data.phone = request.form.get('phone','')
  data.facebook_link = request.form.get('facebook_link','')
  data.image_link = request.form.get('image_link','')
  data.website_link = request.form.get('website_link','')
  data.seeking_talent = request.form.get('seeking_talent','')
  data.seeking_description = request.form.get('seeking_description',' ')
  
  try:
    db.session.commit()
    flash(f'Edit was successful on{form.name.data}')
  except:
    db.session.rollback()
    flash(f"There was an error editing {form.name.data}")
  finally:
   db.session.close()


  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
