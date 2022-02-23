# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import os

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import re
from models import db, Shows, Venue, Artist

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.Config')
db.init_app(app)

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(value, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    cities = [(row.city, row.state) for row in db.session.query(Venue.city, Venue.state).distinct().all()]

    # Populate 'data' with required attributes to return to venues.html
    i = 0
    for city, state in cities:
        data.append({'city': city, 'state': state, 'venues': []})
        for row in db.session.query(Venue).filter(Venue.city == city).all():
            data[i]['venues'].append({'id': row.id, 'name': row.name})
        i += 1

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_string = '%{0}%'.format(request.form.get('search_term', ''))
    result = db.session.query(Venue).filter(Venue.name.ilike(search_string)).all()
    count = len(result)
    response = {
        'count': count,
        'data': result
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()

    if venue is None:
        abort(404)

    data = {
        'id': venue.id,
        'name': venue.name,
        'city': venue.city,
        'state': venue.state,
        'genres': venue.genres,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link
    }

    past = db.session.query(Shows).filter(Shows.venue_id == venue_id)\
        .filter(Shows.start_time < datetime.now().strftime("%m/%d/%Y, %H:%M:%S")).join(Artist, Shows.artist_id == Artist.id)\
        .values(Artist.id, Artist.name, Shows.start_time)

    upcoming = db.session.query(Shows).filter(Shows.venue_id == venue_id)\
        .filter(Shows.start_time > datetime.now().strftime("%m/%d/%Y, %H:%M:%S")).join(Artist, Shows.artist_id == Artist.id)\
        .values(Artist.id, Artist.name, Shows.start_time)
    
    data.update(
        past_shows=[show for show in past],
        upcoming_shows=[show for show in upcoming]
    )

    data['past_shows_count'] = len(data['past_shows'])
    data['upcoming_shows_count'] = len(data['upcoming_shows'])

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if form.validate_on_submit():
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue)
        db.session.commit()

        venue = db.session.query(Venue).order_by(Venue.id.desc()).first()

        flash('Venue ' + request.form['name'] + ' was successfully added!')
        return redirect(url_for('show_venue', venue_id=venue.id))
    else:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be added')
        db.session.rollback()
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    try:
        Shows.query.filter(Shows.venue_id == venue_id).delete()
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    for row in db.session.query(Artist.id, Artist.name).all():
        data.append({'id': row.id, 'name': row.name})

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_string = '%{0}%'.format(request.form.get('search_term', ''))
    result = db.session.query(Artist).filter(Artist.name.ilike(search_string)).all()
    count = len(result)
    response = {
        'count': count,
        'data': result
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()

    if artist is None:
        abort(404)

    data = {
        'id': artist.id,
        'name': artist.name,
        'city': artist.city,
        'state': artist.state,
        'genres': artist.genres,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link
    }

    past = db.session.query(Shows).filter(Shows.artist_id == artist_id)\
        .filter(Shows.start_time < datetime.now().strftime("%m/%d/%Y, %H:%M:%S")).join(Venue, Shows.venue_id == Venue.id)\
        .values(Venue.id, Venue.name, Shows.start_time)

    upcoming = db.session.query(Shows).filter(Shows.artist_id == artist_id)\
        .filter(Shows.start_time > datetime.now().strftime("%m/%d/%Y, %H:%M:%S")).join(Venue, Shows.venue_id == Venue.id)\
        .values(Venue.id, Venue.name, Shows.start_time)

    data.update(
        past_shows=[show for show in past],
        upcoming_shows=[show for show in upcoming]
    )

    data['past_shows_count'] = len(data['past_shows'])
    data['upcoming_shows_count'] = len(data['upcoming_shows'])

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
        artist.name = request.form.get('name')
        artist.state = request.form.get('state')
        artist.city = request.form.get('city')
        artist.genres = request.form.getlist('genres')
        artist.image_link = request.form.get('image_link')
        artist.website = request.form.get('website_link')
        db.session.commit()
        return redirect(url_for('show_artist', artist_id=artist_id))
    except:
        abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    venue.name = request.form.get('name')
    venue.state = request.form.get('state')
    venue.city = request.form.get('city')
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link')
    venue.website = request.form.get('website_link')
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    data = Artist(
        name=request.form.get('name'),
        state=request.form.get('state'),
        city=request.form.get('city'),
        genres=request.form.getlist('genres'),
        phone=request.form.get('phone'),
        website=request.form.get('website_link'),
        facebook_link=request.form.get('facebook_link'),
        image_link=request.form.get('image_link'),
        seeking_venue=request.form.get('seeking_venue') == 'y',
        seeking_description=request.form.get('seeking_description')
    )
    try:
        db.session.add(data)
        db.session.commit()

        artist = db.session.query(Artist).order_by(Artist.id.desc()).first()
        # make data structure to render

        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('show_artist', artist_id=artist.id))
    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()

        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    result = db.session.query(Shows).join(Venue, Shows.venue_id == Venue.id)\
        .join(Artist, Shows.artist_id == Artist.id)

    data = []
    for res in result:
        data.append({
            'artist_name': res.artist.name,
            'artist_id': res.artist.id,
            'venue_id': res.venue.id,
            'venue_name': res.venue.name,
            'start_time': res.start_time,
            'artist_image_link': res.artist.image_link
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        new_show = Shows(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time'])
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully added!')
    except:
        flash('An error occurred during show submission. Show could not be added.')
        db.session.rollback()
    finally:
        db.session.close()
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()


'''
# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
