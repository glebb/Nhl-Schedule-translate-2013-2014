from flask import render_template
from flask import jsonify
from flask import request
from flask import send_from_directory
from flask import make_response
from flask import abort
from flask import session
from dateutil import parser
import os
import datetime
import calendar
import pytz

from nhl_schedule_translate import app
from nhl_schedule_translate.nhl_schedule import *


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route('/')
def index():
    session.permanent = True
    if not 'timezone' in session:
        session['timezone'] = 'Europe/Helsinki'
    if not 'temp_start_from' in session:
        session['temp_start_from'] = '17:00'
    if not 'temp_end_by' in session:
        session['temp_end_by'] = '21:30'
    if not 'filter_time' in session:
        session['filter_time'] = 'true'
        
    return render_template('index.html', temp=None)

@app.route('/_get_schedule')
def get_schedule():
    games = []
    try:
        session['timezone'] = request.args.get('TARGET_TIMEZONE', 0) 
        timezone = pytz.timezone(session['timezone'])
        session['team_filter'] = unicode(request.args.get('TEAM_FILTER', 0).encode('utf-8'), 'utf8')
        session['filter_time'] = request.args.get('FILTER_TIME', 0) == "true"
        if session['filter_time']:
            session['temp_start_from'] = request.args.get('START_FROM', 0)
            start_from = datetime.time(hour=int(session['temp_start_from'].split(':')[0]),
                 minute=int(session['temp_start_from'].split(':')[1]))
            session['temp_end_by'] = request.args.get('END_BY', 0)
            end_by = datetime.time(hour=int(session['temp_end_by'].split(':')[0]),
                 minute=int(session['temp_end_by'].split(':')[1]))
        else:
            start_from = datetime.time(hour=0, minute=0)
            end_by = datetime.time(hour=23, minute=59)
    except:
        pass
    else:
        try:
            games = pickle.load( open( SCHEDULE_DATA, "rb" ) )
        except IOError:
            games = save_schedule_from_web()
        games = filter_games(games, timezone, session['team_filter'], start_from, end_by)
    return jsonify(games=games)
    
@app.route('/_get_ical')    
def getIcal():
    tagline = request.args.get('tagline', 0).encode('utf-8')
    time = request.args.get('time', 0)
    timezone = request.args.get('timezone', 0)
    try:
        tz = pytz.timezone(timezone)
        time = parser.parse(time, dayfirst=True).replace(tzinfo=tz)
    except:
        abort(404)
    cal = create_ical(tagline, time)
    response = make_response(cal.to_ical())
    response.headers['Content-Type'] = 'text/calendar'
    response.headers['Content-Disposition'] = 'attachment; filename=game.ics'
    return response