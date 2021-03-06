from BeautifulSoup import BeautifulSoup
import datetime
from dateutil import parser
import urllib2
import pytz
import cPickle as pickle

TARGET_TIMEZONE = pytz.timezone('Europe/Helsinki')
START_FROM = datetime.time(hour=7, minute=00)
END_BY = datetime.time(hour=22, minute=30)
TEAM_FILTER = 'Philadelphia'
WRITE_ICAL_ENTRIES = True
SCHEDULE_DATA = "games.p"

if WRITE_ICAL_ENTRIES:
    import icalendar

def main():
    try:
        games = pickle.load( open( SCHEDULE_DATA, "rb" ) )
    except IOError:
        games = save_schedule_from_web()
    
    i = 1
    games = filter_games(games, TARGET_TIMEZONE, TEAM_FILTER, START_FROM, END_BY)
    for game in games:
        tagline = game['home_team'] + ' vs ' + game['visiting_team']
        print str(i) + '. ' + game['target_time'].strftime("%A %d.%m.%Y %H:%M") + ' ' + tagline
        i += 1

        if WRITE_ICAL_ENTRIES:
            cal = create_ical(tagline, game['target_time'])
            f = open(game['target_time'].strftime("%Y-%m-%d - ") + tagline + '.ics', 'wb')
            f.write(cal.to_ical())
            f.close()

def save_schedule_from_web():
    games = []

    data = urllib2.urlopen('http://www.nhl.com/ice/schedulebyseason.htm').read()
    soup = BeautifulSoup(data)

    table_cells = soup.findAll('td', {'class' : 'time'})
    for td in table_cells:
        entry = _parse_game_entry_from(td)
        if entry:
            games.append(entry)
    pickle.dump( games, open( SCHEDULE_DATA, "wb" ) )
    return games
    
def _parse_game_entry_from(td):
    item = {}
    parent_row = td.findParents('tr')[0]
    game_info_cells = parent_row.findAll('td')
    try:
        item['date'] = str(game_info_cells[0].div.string)
        item['visiting_team'] = str(game_info_cells[1].findAll('a')[1].string)
        item['home_team'] = str(game_info_cells[2].findAll('a')[1].string)
        item['time'] = str(game_info_cells[3].div.string)
    except IndexError:
        return None
    return item

def create_ical(tagline, target_time):
    cal = icalendar.Calendar()
    event = icalendar.Event()
    event.add('summary', 'NHL: ' + tagline)
    event.add('dtstart', target_time)
    event.add('dtend', target_time + datetime.timedelta(hours=2, minutes=30))
    cal.add_component(event)
    return cal
    
def filter_games(games, target_timezone, team_filter, start_from, end_by):
    temp = []
    for game in games:
        date = game['date']
        visiting_team = game['visiting_team']
        home_team = game['home_team']
        time = game['time']
    
        if team_filter:
            if not home_team == team_filter and not visiting_team == team_filter:
                continue
        eastern = pytz.timezone('US/Eastern')            
        temp_time = parser.parse(date + ' ' + time)    
        usa_et_time = eastern.localize(temp_time)
        target_time = usa_et_time.astimezone(target_timezone)
        game['target_time'] = target_time.strftime("%A %d.%m.%Y %H:%M")
        _mark_weekend(game, target_time)
        _mark_past(game, target_time, target_timezone)
        if target_time.time() >= start_from and target_time.time() <= end_by:#if start_from <= end_by:
            if start_from <= target_time.time() <= end_by:
                temp.append(game)
        elif target_time.time() <= end_by or target_time.time() >= start_from:
            temp.append(game)
    return temp
    
def _mark_weekend(game, target_time):
    date = target_time
    game['weekend'] = False
    if date.weekday() == 4:
        if date.hour > 16 and date.hour <= 23:#if 16 < date.hour <= 23:
            game['weekend'] = True
    if date.weekday() == 5 or date.weekday() == 6:
        game['weekend'] = True

def _mark_past(game, target_time, target_timezone):
    game['inPast'] = False
    now = datetime.datetime.now().replace(tzinfo=target_timezone)
    difference = _total_seconds(now - target_time)
    if difference / 60 > 150:
        game['inPast'] = True
    
def _total_seconds(deltatime):
    if hasattr(deltatime, "total_seconds"):
        duration = deltatime.total_seconds()
    else: 
        duration = (deltatime.microseconds + (deltatime.seconds +  deltatime.days * 24 * 3600) * 10**6) / 10**6  
    return duration  


if __name__ == '__main__':
    main()