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
        games.append(entry)
    pickle.dump( games, open( SCHEDULE_DATA, "wb" ) )
    return games
    
def _parse_game_entry_from(td):
    item = {}
    parent_row = td.findParents('tr')[0]
    game_info_cells = parent_row.findAll('td')
    item['date'] = str(game_info_cells[0].div.string)
    item['visiting_team'] = str(game_info_cells[1].findAll('a')[1].string)
    item['home_team'] = str(game_info_cells[2].findAll('a')[1].string)
    item['time'] = str(game_info_cells[3].div.string)
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
        usa_et_time = parser.parse(date + ' ' + time).replace(tzinfo=pytz.timezone('US/Eastern'))
        target_time = usa_et_time.astimezone(target_timezone)
        game['target_time'] = target_time.strftime("%A %d.%m.%Y %H:%M")
        _mark_weekend(game, target_time)
        #game['weekday'] = target_time.weekday()
        if target_time.time() >= start_from and target_time.time() <= end_by:
            temp.append(game)
    return temp
    
def _mark_weekend(game, target_time):
    date = target_time
    game['weekend'] = False
    if date.weekday() == 4:
        if date.hour > 16 and date.hour <= 23:
            game['weekend'] = True
    if date.weekday() == 5 or date.weekday() == 6:
        game['weekend'] = True
    
if __name__ == '__main__':
    main()