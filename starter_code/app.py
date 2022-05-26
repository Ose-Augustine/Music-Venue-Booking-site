#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from typing import final
import pytz
import datetime 
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


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
  return render_template('pages/home.html', recent_venues=recent_venues, recent_artists=recent_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = Venue.query.all()
  return render_template('pages/venues.html', areas=data)

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
  venue = Venue.query.get_or_404(venue_id)
  past_shows = []
  upcoming_shows =[]
  for show in venue.shows :
    show_temp = {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time
    }
    if show.start_time <= pytz.utc.localize(datetime.now()):
      past_shows.append(show_temp)
    else:
      upcoming_shows.append(show_temp)
  data = vars(venue)
  data['past_shows'] = past_shows 
  data['upcoming_shows'] = upcoming_shows 
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #show recents along with submission
  recent_venues = Venue.query.order_by(Venue.creation_time).limit(5).all()
  recent_artists = Artist.query.order_by(Artist.creation_time).limit(5).all()
  form = VenueForm(request.form)
  venue = Venue()
  try:
    venue.name = form.name.data,
    venue.city = form.city.data,
    venue.state = form.state.data,
    venue.address = form.address.data,
    venue.phone = form.phone.data,
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data,
    venue.website_link = form.website_link.data,
    venue.seeking_talent = form.seeking_talent.data,
    venue.seeking_description = form.seeking_description.data,
    venue.genres = form.genres.data
  
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()

  return render_template('pages/home.html',recent_artists=recent_artists,recent_venues=recent_venues)

@app.route('/venues/<venue_id>/delete')
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
  artist = Artist.query.get_or_404(artist_id)
  past_shows = []
  upcoming_shows = []
  for show in artist.shows:
    show_temp = {
      'venue_id':show.artist_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time' : show.start_time
    }
    if show.start_time <= pytz.utc.localize(datetime.now()):
      past_shows.append(show_temp)
    else:
      upcoming_shows.append(show_temp)
  extra = vars(artist)
  extra['upcoming_shows'] = upcoming_shows 
  extra['past_shows'] = past_shows 
  extra['upcoming_shows_count'] = len(upcoming_shows) 
  extra['past_shows_count'] = len(past_shows)

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id = artist_id)[0]
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  edited_artist = Artist.query.get_or_404(artist_id)
  edited_artist.available_times = [form.available_times.time1.data,form.available_times.time2.data]
  edited_artist.name = form.name.data
  edited_artist.city = form.city.data
  edited_artist.state = form.state.data
  edited_artist.phone = form.phone.data
  edited_artist.facebook_link = form.facebook_link.data
  edited_artist.image_link = form.image_link.data
  edited_artist.website_link = form.website_link.data
  edited_artist.seeking_venue = form.seeking_venue.data
  edited_artist.genres = form.genres.data 
  edited_artist.seeking_description = form.seeking_description.data

  try:
    db.session.commit()
    flash(f'Edit was successful for {form.name.data}')
  except:
    db.session.rollback()
    flash(f"There was an error editing {form.name.data}")
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

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  recent_venues = Venue.query.order_by(Venue.creation_time).limit(5).all()
  recent_artists = Artist.query.order_by(Artist.creation_time).limit(5).all()
  form = ArtistForm(request.form)
  times = AvailableForm(request.form)
  artist = Artist(
    name = form.name.data,
    genres = form.genres.data ,
    state = form.state.data,
    phone = form.phone.data,
    facebook_link = form.facebook_link.data,
    website_link = form.website_link.data, 
    image_link = form.image_link.data ,
    seeking_venue = form.seeking_venue.data, 
    seeking_description = form.seeking_description.data,
    available_times = [form.available_times.time1.data,form.available_times.time2.data]
  )
  
  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash(f'An error occured recording data for {form.name.data}')
    db.session.rollback()
  return render_template('pages/home.html',recent_artists=recent_artists,recent_venues=recent_venues)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  show = Show(
    artist_id = form.artist_id.data,
    venue_id = form.venue_id.data, 
    start_time = form.start_time.data 
  )
  artist = Artist.query.get_or_404(form.artist_id.data)
  if not show.start_time in artist.available_times:
    flash (f"Artist won't be available at {show.start_time}")
  else:
      try:
        db.session.add(show)
        db.session.commit()
        flash(f"Venue {show.venue.name} was succesfully listed ")
      except:
        db.session.rollback()
  recent_venues = Venue.query.order_by(Venue.creation_time).limit(5).all()
  recent_artists = Artist.query.order_by(Artist.creation_time).limit(5).all()
  return render_template('pages/home.html',recent_artists=recent_artists,recent_venues=recent_venues)

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
